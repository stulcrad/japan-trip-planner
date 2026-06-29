'''
This module defines the FastAPI application and its endpoints.
'''
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import LoginRequest, UserOut

# Create a FastAPI application instance
app = FastAPI()

# Add CORS middleware to allow requests from the frontend application
app.add_middleware(
    CORSMiddleware,
    # Allow requests from the specified origin (frontend application)
    allow_origins=["https://japan-trip-planner-ruddy.vercel.app/"],
    # Allow all HTTP methods and headers for CORS requests
    allow_methods=["*"],
    # Allow all headers for CORS requests
    allow_headers=["*"],
)

# Define a root endpoint that returns a simple status message
@app.get("/")
def root():
    return {"status": "ok", "message": "Japan trip planner backend is alive"}

# Define a health check endpoint that returns a simple status message
@app.get("/health")
def health():
    return {"status": "healthy"}

# Define a database check endpoint that executes a simple SQL query to verify the database connection
@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "connected"}

# Define a login endpoint that handles user authentication and registration
@app.post("/auth/login", response_model=UserOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    user = db.query(User).filter(func.lower(User.name) == name.lower()).first()
    if user is None:
        user = User(name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user