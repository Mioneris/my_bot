from bot_config import database_dish
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3

menu_router = Router()


@menu_router.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery):
    categories = database_dish.get_categories()

    menu_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=category, callback_data=f"category:{category}")
            ] for category in categories
        ]
    )
    await callback.message.edit_text('Выберите категорию из меню:', reply_markup=menu_kb)


@menu_router.callback_query(F.data.startswith("category:"))
async def show_menu(callback: CallbackQuery):
    category_name = callback.data.split("category:")[1]

    with sqlite3.connect(database_dish.path) as conn:
        cursor = conn.execute(
            "SELECT name,price,description FROM dish_info WHERE category = ?",
            (category_name,)
        )
    dishes = cursor.fetchall()

    if dishes:
        for dish in dishes:
            name, price, description = dish
            await callback.message.answer(
                f"Название: {name}\n"
                f"Цена:{price}\n"
                f"Описание:{description}"
            )
    else:
        await callback.message.answer("В выбранной категории пока отсутствуют блюда")

    backstep_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад к категориям", callback_data="menu")
            ]
        ]
    )

    await callback.message.answer('Возврат к категория:',
                                  reply_markup=backstep_menu)
