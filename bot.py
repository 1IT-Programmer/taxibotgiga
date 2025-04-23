
#### 6. `bot.py`
Основной скрипт нашего бота, содержащий всю бизнес-логику и обработку запросов.

```python
import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from aiosqlite import connect as async_connect

load_dotenv()  # Загружаем переменные окружения из .env

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    name = Column(String)

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), default=None)
    from_place = Column(String)
    to_place = Column(String)
    status = Column(String, default="pending")

Base.metadata.create_all(bind=engine)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я транспортный бот. Используй команды для регистрации и отправки заявок.")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2 or args[0] not in ['admin', 'driver', 'passenger']:
        await update.message.reply_text("Использование: /register <роль> <имя>. Роли: admin, driver, passenger.")
        return
    role, name = args
    with SessionLocal() as session:
        new_user = User(id=update.effective_user.id, role=role, name=name)
        session.add(new_user)
        session.commit()
        await update.message.reply_text(f"Успешно зарегистрирован как {role}: {name}.")

async def create_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Использование: /create_trip <откуда> <куда>")
        return
    from_place, to_place = args
    with SessionLocal() as session:
        new_trip = Trip(passenger_id=update.effective_user.id, from_place=from_place, to_place=to_place)
        session.add(new_trip)
        session.commit()
        await update.message.reply_text(f"Твоя поездка создана. ID: {new_trip.id}, Маршрут: {from_place} → {to_place}")

async def assign_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Использование: /assign_driver <ID поездки> <ID водителя>")
        return
    trip_id, driver_id = map(int, args)
    with SessionLocal() as session:
        trip = session.query(Trip).filter_by(id=trip_id).first()
        if not trip:
            await update.message.reply_text("Поездка не найдена.")
            return
        trip.driver_id = driver_id
        trip.status = "assigned"
        session.commit()
        await update.message.reply_text(f"Назначил водителя {driver_id} на поездку {trip_id}.")

async def complete_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Использование: /complete_trip <ID поездки>")
        return
    trip_id = int(args[0])
    with SessionLocal() as session:
        trip = session.query(Trip).filter_by(id=trip_id).first()
        if not trip:
            await update.message.reply_text("Поездка не найдена.")
            return
        trip.status = "completed"
        session.commit()
        await update.message.reply_text(f"Поездка {trip_id} завершена.")

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("create_trip", create_trip))
    app.add_handler(CommandHandler("assign_driver", assign_driver))
    app.add_handler(CommandHandler("complete_trip", complete_trip))

    app.run_polling()

if __name__ == "__main__":
    main()
