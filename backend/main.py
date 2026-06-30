'''
This module defines the FastAPI application and its endpoints.
'''
import uuid
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from database import get_db
from models import GroupMember, ItineraryDay, ItineraryItem, TripGroup, User
from schemas import (
    DayCreate,
    DayOut,
    DayUpdate,
    GroupCreate,
    GroupOut,
    ItemCreate,
    ItemOut,
    ItemUpdate,
    JoinRequest,
    LoginRequest,
    UserOut,
)

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

    # We can use python's functions instead of a raw SQL query to find a user by name, ignoring case
    user = db.query(User).filter(func.lower(User.name) == name.lower()).first()
    # SQL query equivalent: SELECT * FROM users WHERE lower(name) = lower(:name) LIMIT 1
    if user is None:
        user = User(name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

# List all trip groups, newest first
@app.get("/groups", response_model=List[GroupOut])
def list_groups(db: Session = Depends(get_db)):
    return db.query(TripGroup).order_by(TripGroup.created_at.desc()).all()


# Create a trip group and add its creator as the first member
@app.post("/groups", response_model=GroupOut)
def create_group(payload: GroupCreate, db: Session = Depends(get_db)):
    # Find the creator user by ID to ensure they exist before creating the group
    creator = db.query(User).filter(User.id == payload.created_by).first()
    if creator is None:
        raise HTTPException(status_code=404, detail="User not found")

    group = TripGroup(
        name=payload.name,
        description=payload.description,
        created_by=payload.created_by,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(group)
    db.flush()  # assigns group.id within the open transaction, without committing yet

    db.add(GroupMember(group_id=group.id, user_id=payload.created_by))
    db.commit()
    db.refresh(group)
    return group


# Fetch a single trip group by id
@app.get("/groups/{group_id}", response_model=GroupOut)
def get_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    group = db.query(TripGroup).filter(TripGroup.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


# Join a trip group; joining a group you're already in is a no-op
@app.post("/groups/{group_id}/join")
def join_group(group_id: uuid.UUID, payload: JoinRequest, db: Session = Depends(get_db)):
    # Find the group and user by ID to ensure it exists before adding the user as a member
    group = db.query(TripGroup).filter(TripGroup.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    membership = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == payload.user_id)
        .first()
    )
    if membership is None:
        db.add(GroupMember(group_id=group_id, user_id=payload.user_id))
        db.commit()

    return {"status": "joined"}


# List a group's itinerary days in date order (the broad day-by-day plan view)
@app.get("/groups/{group_id}/days", response_model=List[DayOut])
def list_days(group_id: uuid.UUID, db: Session = Depends(get_db)):
    group = db.query(TripGroup).filter(TripGroup.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    return (
        db.query(ItineraryDay)
        .filter(ItineraryDay.group_id == group_id)
        .order_by(ItineraryDay.date)
        .all()
    )


# Add a day to a group's itinerary
@app.post("/groups/{group_id}/days", response_model=DayOut)
def create_day(group_id: uuid.UUID, payload: DayCreate, db: Session = Depends(get_db)):
    # Find the group by ID to ensure it exists before adding a day
    group = db.query(TripGroup).filter(TripGroup.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if a day already exists for the given date in the group to enforce uniqueness
    existing = (
        db.query(ItineraryDay)
        .filter(ItineraryDay.group_id == group_id, ItineraryDay.date == payload.date)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="A day already exists for this date")

    # Create a new ItineraryDay object and add it to the database
    day = ItineraryDay(
        group_id=group_id,
        date=payload.date,
        location=payload.location,
        summary=payload.summary,
    )
    db.add(day)
    db.commit()
    db.refresh(day)
    return day


# Partially update a day (only fields included in the request body are changed)
@app.patch("/days/{day_id}", response_model=DayOut)
def update_day(day_id: uuid.UUID, payload: DayUpdate, db: Session = Depends(get_db)):
    # Find the day by ID to ensure it exists before updating
    day = db.query(ItineraryDay).filter(ItineraryDay.id == day_id).first()
    if day is None:
        raise HTTPException(status_code=404, detail="Day not found")

    # Update only the fields that are included in the request body (exclude_unset=True)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(day, field, value)

    db.commit()
    db.refresh(day)
    return day


# List a day's itinerary items in manual order
@app.get("/days/{day_id}/items", response_model=List[ItemOut])
def list_items(day_id: uuid.UUID, db: Session = Depends(get_db)):
    # Find the day by ID to ensure it exists before listing its items
    day = db.query(ItineraryDay).filter(ItineraryDay.id == day_id).first()
    if day is None:
        raise HTTPException(status_code=404, detail="Day not found")

    return (
        db.query(ItineraryItem)
        .filter(ItineraryItem.day_id == day_id)
        .order_by(ItineraryItem.order_index)
        .all()
    )


# Add an item to a day's itinerary, appended after any existing items
@app.post("/days/{day_id}/items", response_model=ItemOut)
def create_item(day_id: uuid.UUID, payload: ItemCreate, db: Session = Depends(get_db)):
    # Find the day and user by ID to ensure they exist before adding the item
    day = db.query(ItineraryDay).filter(ItineraryDay.id == day_id).first()
    if day is None:
        raise HTTPException(status_code=404, detail="Day not found")

    user = db.query(User).filter(User.id == payload.added_by).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Determine the next order index for the new item by finding the max order_index of existing items for the day
    max_order = (
        db.query(func.max(ItineraryItem.order_index))
        .filter(ItineraryItem.day_id == day_id)
        .scalar()
    )
    # max_order will be None if there are no existing items for the day
    next_order = 0 if max_order is None else max_order + 1

    item = ItineraryItem(
        day_id=day_id,
        time=payload.time,
        title=payload.title,
        notes=payload.notes,
        added_by=payload.added_by,
        order_index=next_order,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# Partially update an item (only fields included in the request body are changed)
@app.patch("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: uuid.UUID, payload: ItemUpdate, db: Session = Depends(get_db)):
    # Find the item by ID to ensure it exists before updating
    item = db.query(ItineraryItem).filter(ItineraryItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


# Delete an item
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.query(ItineraryItem).filter(ItineraryItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
