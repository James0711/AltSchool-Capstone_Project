from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import app.schemas as schemas
from app.crud import rating_crud_service, movie_crud_service
from app.database import get_db
from app.auth import get_current_user
from app.logger import logger

rating_router = APIRouter()

@rating_router.get("/", status_code=200, response_model=List[schemas.Rating])
async def get_ratings(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    ratings = rating_crud_service.get_ratings(db, offset=offset, limit=limit)
    return ratings

@rating_router.get("/{rating_id}", status_code=200, response_model=schemas.Rating)
async def get_rating_by_id(rating_id: int, db: Session = Depends(get_db)):
    rating = rating_crud_service.get_rating_by_id(db, rating_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return rating

@rating_router.get("/movie/{movie_id}", status_code=200, response_model=List[schemas.Rating])
async def get_ratings_by_movie_id(movie_id: int, db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    ratings = rating_crud_service.get_ratings_by_movie_id(db, movie_id, offset, limit)
    return ratings

@rating_router.get("/average_rating/{movie_id}", status_code=200)
async def get_movie_avg_rating(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    avg_rating = rating_crud_service.aggregate_rating(db, movie_id)
    data = {
        "movie_id": movie.id,
        "movie_title": movie.title,
        "owner_id": movie.user_id,
        "avg_rating": avg_rating
    }
    return {"message": "Successful", "data": data}

@rating_router.post('/{movie_id}', status_code=201, response_model=schemas.Rating)
async def rate_movie(movie_id: int, rating: schemas.RatingCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    existing_rating = rating_crud_service.get_rating(db, user_id=current_user.id, movie_id=movie_id)
    if existing_rating is not None:
        logger.warning(f"User {current_user.id} is trying to rate movie {movie_id} again.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already rated this movie. Update your existing rating instead.")

    new_rating = rating_crud_service.rate_movie_by_id(db, rating=rating, user_id=current_user.id, movie_id=movie_id)
    return new_rating

@rating_router.put("/{rating_id}", status_code=200, response_model=schemas.Rating)
async def update_rating(rating_id: int, payload: schemas.RatingUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rating = rating_crud_service.get_rating_by_id(db, rating_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    updated_rating = rating_crud_service.update_rating(db, rating_payload=payload, rating_id=rating_id)
    return updated_rating

@rating_router.delete("/{rating_id}", status_code=200)
async def delete_rating(rating_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    rating = rating_crud_service.get_rating_by_id(db, rating_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    rating_crud_service.delete_rating(db, rating_id)
    return {"message": "Rating deleted successfully"}
