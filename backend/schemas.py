from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: date

    class Config:
        orm_mode = True

class TripBase(BaseModel):
    departure_point: str
    arrival_point: str
    distance: float
    price: float

class TripCreate(TripBase):
    pass

class Trip(TripBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
