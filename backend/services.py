from sqlalchemy.orm import Session
from ..models import User, Trip
from ..schemas import UserCreate, TripCreate
from ..auth import get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=fake_hashed_password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_trip_for_user(db: Session, trip: TripCreate, user_id: int):
    db_trip = Trip(**trip.dict(), owner_id=user_id)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip
