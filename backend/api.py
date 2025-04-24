from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import timedelta
from pydantic import EmailStr
from jinja2 import TemplateNotFound
from .database import engine, SessionLocal
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .auth import authenticate_user, create_access_token, get_current_active_user
from .models import User, Trip
from .schemas import UserCreate, UserUpdate, TripCreate, TokenData
from .utils import generate_unique_id

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Подключение сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    print("Starting server...")

@app.on_event("shutdown")
async def shutdown():
    print("Shutting down server...")

@app.post("/token", response_model=TokenData)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Annotated[Session, Depends(get_db)]):
    """
    Генерирует JWT-токен после успешной авторизации.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неправильные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", include_in_schema=False)
async def read_root(request: Request):
    """
    Главная страница приложения (для рендеринга front-end шаблонов).
    """
    try:
        template = request.app.templates.get_template("index.html")
        return template.render()
    except TemplateNotFound:
        return Response(content="Template not found.", media_type="text/html", status_code=404)

@app.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """
    Регистрация нового пользователя.
    """
    db_user = User(username=user.username, hashed_password=get_password_hash(user.password), full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}/", response_model=UserCreate)
async def get_user(user_id: int, db: Annotated[Session, Depends(get_db)],
                   current_user: Annotated[User, Security(get_current_active_user)]):
    """
    Возвращает информацию о конкретном пользователе.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user

@app.put("/users/{user_id}/", response_model=UserUpdate)
async def update_user(user_id: int, updated_user: UserUpdate, db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[User, Security(get_current_active_user)]):
    """
    Редактирует профиль пользователя.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    for key, value in updated_user.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}/", response_model=str)
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[User, Security(get_current_active_user)]):
    """
    Удаляет пользователя.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(db_user)
    db.commit()
    return f"Пользователь с ID {user_id} удалён."

@app.post("/trips/", response_model=TripCreate)
async def create_trip(trip: TripCreate, db: Annotated[Session, Depends(get_db)],
                     current_user: Annotated[User, Security(get_current_active_user)]):
    """
    Создаёт новую поездку.
    """
    db_trip = Trip(departure_point=trip.departure_point, arrival_point=trip.arrival_point, distance=trip.distance, price=trip.price, user_id=current_user.id)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

@app.get("/trips/", response_model=list[TripCreate])
async def list_trips(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    """
    Показывает список всех поездок.
    """
    return db.query(Trip).offset(skip).limit(limit).all()

@app.get("/trips/{trip_id}/", response_model=TripCreate)
async def get_trip(trip_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    Получает детальную информацию о конкретной поездке.
    """
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    return db_trip

@app.put("/trips/{trip_id}/", response_model=TripCreate)
async def update_trip(trip_id: int, updated_trip: TripCreate, db: Annotated[Session, Depends(get_db)]):
    """
    Обновляет информацию о поездке.
    """
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    for key, value in updated_trip.model_dump(exclude_unset=True).items():
        setattr(db_trip, key, value)
    db.commit()
    db.refresh(db_trip)
    return db_trip

@app.delete("/trips/{trip_id}/", response_model=str)
async def delete_trip(trip_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    Удаляет поездку.
    """
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    db.delete(db_trip)
    db.commit()
    return f"Поездка с ID {trip_id} удалена."
