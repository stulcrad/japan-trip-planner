'''
This module defines the Pydantic schemas used for request validation and response serialization.
'''
import uuid
from datetime import date, datetime
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
    start_date: Optional[date] = None
    end_date: Optional[date] = None

# Define the GroupOut schema for serializing trip group data in responses
class GroupOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_by: uuid.UUID
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True

# Define the JoinRequest schema for validating group join requests
class JoinRequest(BaseModel):
    user_id: uuid.UUID
