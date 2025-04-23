from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now())

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    departure_point = Column(String)
    arrival_point = Column(String)
    distance = Column(Float)
    price = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="trips")
