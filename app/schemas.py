from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # Use orm_mode instead of from_attributes for SQLAlchemy integration

# Movie Schemas
class MovieBase(BaseModel):
    title: str
    genre: str
    description: Optional[str] = None
    release_year: Optional[int] = None

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None

class Movie(MovieBase):
    id: int
    user_id: int
    created_at: datetime
    owner: User

    class Config:
        orm_mode = True  # Use orm_mode instead of from_attributes for SQLAlchemy integration

# Rating Schemas
class RatingBase(BaseModel):
    rating_value: int = Field(..., ge=1, le=10)

class RatingCreate(RatingBase):
    pass

class RatingUpdate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime
    user: User

    class Config:
        orm_mode = True  # Use orm_mode instead of from_attributes for SQLAlchemy integration

# Comment Schemas
class CommentBase(BaseModel):
    comment: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    comment: Optional[str] = None

class Comment(CommentBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime
    parent_id: Optional[int] = None
    author: User

    class Config:
        orm_mode = True  # Use orm_mode instead of from_attributes for SQLAlchemy integration

# Response Schemas
class AuthorResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True  # Use orm_mode instead of from_attributes for SQLAlchemy integration

class CommentResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    comment: str
    parent_id: Optional[int] = None
    created_at: datetime
    author: AuthorResponse
    replies: int

    class Config:
        orm_mode = True  # Use orm_mode instead of from_attributes for SQLAlchemy integration

class CommentOut(BaseModel):
    comment: Comment
    replies: int
