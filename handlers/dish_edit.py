from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
from aiogram.types import  CallbackQuery
from bot_config import database
from dotenv import dotenv_values

USER_ID = int(dotenv_values(".env")["USER_ID"])

dish_management_router = Router()


def remove_keyboard():
    return types.ReplyKeyboardRemove()


class Dish_info(StatesGroup):
    name = State()
    price = State()
    description = State()
    category = State()
    dish_picture = State()


@dish_management_router.callback_query(F.data == "start_editing")
async def dish_edit_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != USER_ID:
        await callback.answer('У Вас нет прав для выполнения этой команды!', show_alert=True)
        return
    await callback.message.edit_text('|Название блюда|\n'
                                     'Введите название блюда.')
    await state.set_state(Dish_info.name)


@dish_management_router.message(Dish_info.name)
async def get_dish_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name or not any(char.isalpha() for char in name):
        await message.answer('Пожалуйста, используйте буквы.')
        return
    await state.update_data(name=name)

    categories = database.get_categories_dish_edit()

    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=category)]
            for category in categories],
        resize_keyboard=True, one_time_keyboard=True)

    await message.answer('|Категория|\n'
                         'Укажите категорию добавляемого блюда.', reply_markup=kb)
    await state.set_state(Dish_info.category)


@dish_management_router.message(Dish_info.category)
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
                         "Введите стоимость блюда (в числовом формате)", reply_markup=remove_keyboard())
    await state.set_state(Dish_info.price)


@dish_management_router.message(Dish_info.price)
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
    await state.set_state(Dish_info.description)


@dish_management_router.message(Dish_info.description)
async def get_dish_description(message: types.Message, state: FSMContext):
    description = message.text
    if len(description) > 150:
        await message.answer('Описание не должно превышать 150 символов.')
        return

    await state.update_data(description=description)
    await message.answer("|Фото блюда|\n"
                         "Прикрепите фото блюда(одно изображение).")
    await state.set_state(Dish_info.dish_picture)


@dish_management_router.message(Dish_info.dish_picture, F.photo)
async def get_dish_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer('Пожалуйста, отправьте изображение.')
        return

    dis_pics = message.photo
    biggest_image = dis_pics[-1]
    biggest_image_id = biggest_image.file_id
    await state.update_data(dish_picture=biggest_image_id)

    data = await state.get_data()

    await (message.answer(
        f"Название блюда: {data['name']}\n"
        f"Категория блюда: {data['category']}\n"
        f"Стоимость блюда: {data['price']}\n"
        f"Описание: {data['description']}\n"
        f"Фото: {biggest_image_id}"
    ))

    database.save_dish_info(data)
    await state.clear()
