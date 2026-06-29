'''
This module defines the Pydantic schemas used for request validation and response serialization.
'''
import uuid

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
