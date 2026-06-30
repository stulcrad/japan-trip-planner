'''
This module defines the Pydantic schemas used for request validation and response serialization.
'''
import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

# Define the LoginRequest schema for validating login requests
class LoginRequest(BaseModel):
    name: str

# Define the UserOut schema for serializing user data in responses
class UserOut(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        # Used to allow SQLAlchemy to read User objects attributes
        from_attributes = True

# Define the GroupCreate schema for validating new trip group requests
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: uuid.UUID
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None

# Define the GroupOut schema for serializing trip group data in responses
class GroupOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_by: uuid.UUID
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Define the JoinRequest schema for validating group join requests
class JoinRequest(BaseModel):
    user_id: uuid.UUID

# Define the DayCreate schema for validating new itinerary day requests
class DayCreate(BaseModel):
    date: datetime.date
    location: str
    summary: Optional[str] = None

# Define the DayUpdate schema for validating itinerary day edits (all fields optional)
class DayUpdate(BaseModel):
    date: Optional[datetime.date] = None
    location: Optional[str] = None
    summary: Optional[str] = None

# Define the DayOut schema for serializing itinerary day data in responses
class DayOut(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    date: datetime.date
    location: str
    summary: Optional[str]

    class Config:
        from_attributes = True

# Define the ItemCreate schema for validating new itinerary item requests
class ItemCreate(BaseModel):
    title: str
    added_by: uuid.UUID
    time: Optional[datetime.time] = None
    notes: Optional[str] = None

# Define the ItemUpdate schema for validating itinerary item edits (all fields optional)
class ItemUpdate(BaseModel):
    title: Optional[str] = None
    time: Optional[datetime.time] = None
    notes: Optional[str] = None
    order_index: Optional[int] = None

# Define the ItemOut schema for serializing itinerary item data in responses
class ItemOut(BaseModel):
    id: uuid.UUID
    day_id: uuid.UUID
    time: Optional[datetime.time]
    title: str
    notes: Optional[str]
    added_by: Optional[uuid.UUID]
    order_index: int

    class Config:
        from_attributes = True
