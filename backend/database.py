import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Create a SQLAlchemy engine and sessionmaker using the DATABASE_URL from environment variables
engine = create_engine(os.environ["DATABASE_URL"]) # Engine is used to manage connections to the database
SessionLocal = sessionmaker(bind=engine) # SessionLocal is a factory for creating new Session objects, which are used to interact with the database

# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
