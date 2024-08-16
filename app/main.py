from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import logger
from app.middleware import log_middleware
from app.auth import authenticate_user, create_access_token, pwd_context
from app.crud import user_crud_service
import app.schemas as schemas
from app.database import engine, Base, get_db
from app.routers.users import user_router
from app.routers.comments import comment_router
from app.routers.movies import movie_router
from app.routers.ratings import rating_router

# Initialize FastAPI app and set up the database
app = FastAPI()
Base.metadata.create_all(bind=engine)

# Add logging middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
logger.info('API is starting...')

# Root route
@app.get('/')
async def index():
    return {'message': 'Welcome to Movie API'}

# Include routers for different resources
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(comment_router, prefix="/movies/comments", tags=["Comments"])
app.include_router(movie_router, prefix="/movies", tags=["Movies"])
app.include_router(rating_router, prefix="/movies/ratings", tags=["Ratings"])

# Signup endpoint
@app.post("/signup/", status_code=201, response_model=schemas.User)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud_service.get_user_by_email_or_username(db, credentials=user.username)
    if db_user:
        logger.warning("Attempted signup with existing user...")
        raise HTTPException(status_code=400, detail="User already registered")
    
    hashed_password = pwd_context.hash(user.password)
    return user_crud_service.create_user(db=db, user=user, hashed_password=hashed_password)

# Login endpoint
@app.post("/login", status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning("Login attempt with incorrect credentials...")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
