import uuid

from pydantic import BaseModel


class LoginRequest(BaseModel):
    name: str


class UserOut(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True
