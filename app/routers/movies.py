from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import app.schemas as schemas
from app.crud import movie_crud_service
from app.database import get_db
from app.auth import get_current_user
from app.logger import logger

movie_router = APIRouter()

@movie_router.get("/", status_code=200, response_model=List[schemas.Movie])
async def get_movies(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    movies = movie_crud_service.get_movies(db, offset=offset, limit=limit)
    return movies

@movie_router.get("/{movie_id}", status_code=200, response_model=schemas.Movie)
async def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        logger.warning(f"Movie with ID {movie_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie

@movie_router.get("/genre/{genre}", status_code=200, response_model=List[schemas.Movie])
async def get_movies_by_genre(genre: str, db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    movies = movie_crud_service.get_movies_by_genre(db, genre, offset, limit)
    if not movies:
        logger.info(f"No movies found for genre '{genre}'.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No movies found for this genre")
    return movies

@movie_router.get("/title/{movie_title}", status_code=200, response_model=List[schemas.Movie])
async def get_movies_by_title(movie_title: str, db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    movies = movie_crud_service.get_movies_by_title(db, movie_title, offset, limit)
    if not movies:
        logger.info(f"No movies found with title '{movie_title}'.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No movies found with this title")
    return movies

@movie_router.post('/', status_code=201, response_model=schemas.Movie)
async def create_movie(payload: schemas.MovieCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = movie_crud_service.create_movie(db, payload, user_id=current_user.id)
    return movie

@movie_router.put('/{movie_id}', status_code=200, response_model=schemas.Movie)
async def update_movie(movie_id: int, payload: schemas.MovieUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    if db_movie.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    updated_movie = movie_crud_service.update_movie(db, movie_id, payload)
    return updated_movie

@movie_router.delete("/{movie_id}", status_code=200)
async def delete_movie(movie_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    if movie.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    movie_crud_service.delete_movie(db, movie_id)
    return {"message": "Movie deleted successfully"}
