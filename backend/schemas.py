from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    disabled: bool = False

    class Config:
        orm_mode = True


class TripBase(BaseModel):
    departure_point: str
    destination_point: str


class TripCreate(TripBase):
    pass


class Trip(TripBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
