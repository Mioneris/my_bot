from aiogram import Bot, Dispatcher
from dotenv import dotenv_values
from database import Database
from db_dish_edit import Dish_db

token = dotenv_values(".env")["BOT_TOKEN"]
bot = Bot(token=token)
dp = Dispatcher()
database = Database('db.sqlite3')
database_dish = Dish_db('db.sqlite')
