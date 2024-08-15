import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Load environment variables from .env file
SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL')

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)


# Create a session maker bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db():
     # Provide a database session to be used in dependency injection
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()