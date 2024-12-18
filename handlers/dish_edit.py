from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
from db_dish_edit import Dish_db
from aiogram.filters import Command
from bot_config import database_dish
from dotenv import dotenv_values

USER_ID = int(dotenv_values(".env")["USER_ID"])

dish_management_router = Router()
dish_management_router.message.filter(F.from_user.id == USER_ID)


class dish_info(StatesGroup):
    name = State()
    price = State()
    description = State()
    category = State()


@dish_management_router.message(Command('start_editing'))
async def dish_edit_callback(message: types.Message, state: FSMContext):
    await message.answer('|Название блюда|\n'
                         'Введите название блюда.')
    await state.set_state(dish_info.name)


@dish_management_router.message(dish_info.name)
async def get_dish_name(message: types.Message, state: FSMContext):
    name = message.text
    if not name.isalpha():
        await message.answer('Пожалуйста, используйте буквы.')
        return
    await state.update_data(name=name)

    categories = database_dish.get_categories()
    if not categories:
        await message.answer('Категория блюд не найдена. Выберите из предложенных.')
        return

    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=category)]
            for category in categories],
        resize_keyboard=True, one_time_keyboard=True)

    await message.answer('|Категория|\n'
                         'Укажите категорию добавляемого блюда.', reply_markup=kb)
    await state.set_state(dish_info.category)


@dish_management_router.message(dish_info.category)
async def get_dish_category(message: types.Message, state: FSMContext):
    category = message.text
    allowed_categories = ["Супы",
                          "Вторые блюда",
                          "Горячие напитки",
                          "Холодные напитки"]

    if category not in allowed_categories:
        await message.answer("Пожалуйста, выберите категорию из предложенных вариантов.")
        return

    await state.update_data(category=category)
    await message.answer("|Цена|\n"
                         "Введите стоимость блюда (в числовом формате)")
    await state.set_state(dish_info.price)


@dish_management_router.message(dish_info.price)
async def get_dish_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректную стоимость блюда (положительное число).")
        return
    await state.update_data(price=price)
    await message.answer('|Описание|\n'
                         'Введите описание блюда\n'
                         '(До 150 символов)')
    await state.set_state(dish_info.description)


@dish_management_router.message(dish_info.description)
async def get_dish_description(message: types.Message, state: FSMContext):
    description = message.text
    if len(description) > 150:
        await message.answer('Описание не должно превышать 150 символов.')
        return

    await state.update_data(description=description)
    data = await state.get_data()
    database_dish.save_dish_info(data)

    await (message.answer(
        f"Название блюда: {data['name']}\n"
        f"Категория блюда: {data['category']}\n"
        f"Стоимость блюда: {data['price']}\n"
        f"Описание: {data['description']}"
    ))


