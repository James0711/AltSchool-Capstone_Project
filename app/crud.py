from math import floor
import statistics
from sqlalchemy import func, select
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas

# User CRUD Operations
class UserCRUDService:

    @staticmethod
    def create_user(db: Session, user_data: schemas.UserCreate, hashed_password: str):
        new_user = models.User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def get_users(db: Session, offset: int = 0, limit: int = 10):
        return db.query(models.User).offset(offset).limit(limit).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(models.User).filter(models.User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def get_user_by_email_or_username(db: Session, credentials: str):
        user = UserCRUDService.get_user_by_email(db, credentials) or \
               UserCRUDService.get_user_by_username(db, credentials)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_updates: schemas.UserUpdate):
        user = UserCRUDService.get_user_by_id(db, user_id)
        if not user:
            return None

        updates_dict = user_updates.model_dump(exclude_unset=True)
        for key, value in updates_dict.items():
            setattr(user, key, value)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = UserCRUDService.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
        return None

# Movies CRUD Operations
class MovieCRUDService:

    @staticmethod
    def create_movie(db: Session, movie_data: schemas.MovieCreate, user_id: int):
        new_movie = models.Movie(**movie_data.model_dump(), user_id=user_id)
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)
        return new_movie

    @staticmethod
    def get_movies(db: Session, offset: int = 0, limit: int = 10):
        return db.query(models.Movie).offset(offset).limit(limit).all()

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int):
        return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

    @staticmethod
    def get_movie_by_title(db: Session, title: str, offset: int = 0, limit: int = 10):
        return db.query(models.Movie).filter(models.Movie.title == title).offset(offset).limit(limit).all()

    @staticmethod
    def get_movie_by_genre(db: Session, genre: str, offset: int = 0, limit: int = 10):
        return db.query(models.Movie).filter(models.Movie.genre == genre).offset(offset).limit(limit).all()

    @staticmethod
    def update_movie(db: Session, movie_id: int, movie_updates: schemas.MovieUpdate):
        movie = MovieCRUDService.get_movie_by_id(db, movie_id)
        if not movie:
            return None

        updates_dict = movie_updates.model_dump(exclude_unset=True)
        for key, value in updates_dict.items():
            setattr(movie, key, value)

        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie

    @staticmethod
    def delete_movie(db: Session, movie_id: int):
        movie = MovieCRUDService.get_movie_by_id(db, movie_id)
        if movie:
            db.delete(movie)
            db.commit()
        return None

# Ratings CRUD Operations
class RatingCRUDService:

    @staticmethod
    def rate_movie(db: Session, rating_data: schemas.RatingCreate, user_id: int, movie_id: int):
        new_rating = models.Rating(
            **rating_data.model_dump(),
            user_id=user_id,
            movie_id=movie_id
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating

    @staticmethod
    def get_ratings(db: Session, offset: int = 0, limit: int = 10):
        return db.query(models.Rating).offset(offset).limit(limit).all()

    @staticmethod
    def get_rating(db: Session, user_id: int, movie_id: int):
        return db.query(models.Rating).filter(models.Rating.user_id == user_id, models.Rating.movie_id == movie_id).first()

    @staticmethod
    def get_rating_by_id(db: Session, rating_id: int):
        return db.query(models.Rating).filter(models.Rating.id == rating_id).first()

    @staticmethod
    def get_ratings_by_movie(db: Session, movie_id: int, offset: int = 0, limit: int = 10):
        return db.query(models.Rating).filter(models.Rating.movie_id == movie_id).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_all_ratings_for_movie(db: Session, movie_id: int):
        return db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()

    @staticmethod
    def aggregate_rating(db: Session, movie_id: int):
        ratings = RatingCRUDService.get_all_ratings_for_movie(db, movie_id)
        if not ratings:
            return 0.0
        
        rating_values = [rating.rating_value for rating in ratings]
        mean_rating = statistics.mean(rating_values)
        return round(mean_rating, 2)

    @staticmethod
    def update_rating(db: Session, rating_id: int, rating_updates: schemas.RatingUpdate):
        rating = RatingCRUDService.get_rating_by_id(db, rating_id)
        if not rating:
            return None

        updates_dict = rating_updates.model_dump(exclude_unset=True)
        for key, value in updates_dict.items():
            setattr(rating, key, value)

        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating

    @staticmethod
    def delete_rating(db: Session, rating_id: int):
        rating = RatingCRUDService.get_rating_by_id(db, rating_id)
        if rating:
            db.delete(rating)
            db.commit()
        return None

# Comments CRUD Operations
class CommentCRUDService:

    @staticmethod
    def create_comment(db: Session, comment_data: schemas.CommentCreate, movie_id: int, user_id: int):
        new_comment = models.Comment(
            **comment_data.model_dump(),
            user_id=user_id,
            movie_id=movie_id
        )
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment

    @staticmethod
    def get_comments(db: Session, offset: int = 0, limit: int = 10):
        subquery = (
            db.query(
                models.Comment.parent_id,
                func.count(models.Comment.id).label("reply_count")
            )
            .group_by(models.Comment.parent_id)
            .subquery()
        )

        comments_with_replies = (
            db.query(
                models.Comment,
                models.User,
                func.coalesce(subquery.c.reply_count, 0).label("replies")
            )
            .join(models.User, models.Comment.user_id == models.User.id)
            .outerjoin(subquery, models.Comment.id == subquery.c.parent_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        return comments_with_replies

    @staticmethod
    def get_replies(db: Session, parent_id: int, offset: int = 0, limit: int = 10):
        return db.query(models.Comment).filter(models.Comment.parent_id == parent_id).offset(offset).limit(limit).all()

    @staticmethod
    def get_comments_by_movie(db: Session, movie_id: int, offset: int = 0, limit: int = 10):
        return db.query(models.Comment).filter(models.Comment.movie_id == movie_id).offset(offset).limit(limit).all()

    @staticmethod
    def get_comment_by_id(db: Session, comment_id: int):
        reply_count_subquery = (
            select(
                models.Comment.parent_id,
                func.count(models.Comment.id).label("reply_count")
            )
            .group_by(models.Comment.parent_id)
            .subquery()
        )

        query = (
            select(
                models.Comment,
                func.coalesce(reply_count_subquery.c.reply_count, 0).label("replies")
            )
            .outerjoin(reply_count_subquery, models.Comment.id == reply_count_subquery.c.parent_id)
            .where(models.Comment.id == comment_id)
        )
        return db.execute(query).fetchone()

    @staticmethod
    def get_comments_by_user(db: Session, user_id: int, offset: int = 0, limit: int = 10):
        return db.query(models.Comment).filter(models.Comment.user_id == user_id).offset(offset).limit(limit).all()

    @staticmethod
    def get_comment(db: Session, comment_id: int):
        return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    @staticmethod
    def reply_to_comment(db: Session, parent_id: int, comment_data: schemas.CommentBase, user_id: int):
        parent_comment = CommentCRUDService.get_comment(db, parent_id)
        if not parent_comment:
            return None
        
        new_comment = models.Comment(
            **comment_data.model_dump(),
            movie_id=parent_comment.movie_id,
            parent_id=parent_id,
            user_id=user_id
        )
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment

    @staticmethod
    def update_comment(db: Session, comment_id: int, comment_updates: schemas.CommentUpdate):
        comment = CommentCRUDService.get_comment(db, comment_id)
        if not comment:
            return None

        updates_dict = comment_updates.model_dump(exclude_unset=True)
        for key, value in updates_dict.items():
            setattr(comment, key, value)

        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete_comment(db: Session, comment_id: int):
        comment = CommentCRUDService.get_comment(db, comment_id)
        if comment:
            db.delete(comment)
            db.commit()
        return None

# Instantiate CRUD Services
user_crud_service = UserCRUDService()
movie_crud_service = MovieCRUDService()
rating_crud_service = RatingCRUDService()
comment_crud_service = CommentCRUDService()
