from bot_config import database
from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from .keyboards import start_keyboard

menu_router = Router()


@menu_router.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery):
    categories = database.get_categories_with_dishes()

    if categories:
        category_buttons = [[types.KeyboardButton(text=category)] for category in categories]

        category_buttons.append([types.KeyboardButton(text="Возврат в главное меню бота")])

        menu_kb = types.ReplyKeyboardMarkup(keyboard=category_buttons,
                                            resize_keyboard=True,
                                            one_time_keyboard=True)
        await callback.message.answer('Выберите категорию из меню:', reply_markup=menu_kb)
    else:
        await callback.message.answer('На данный момент меню пусто.')


@menu_router.message(F.text == "Возврат в главное меню бота")
async def back_to_bot_menu(message: types.Message):
    await message.answer('Возврат в главное меню бота!',
                         reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Главное меню:", reply_markup=start_keyboard())


@menu_router.message(F.text.in_(database.get_categories_with_dishes()))
async def show_menu_by_cat(message: types.Message):
    menu = database.get_menu()
    cat_name = message.text
    dishes = [dish for dish in menu if dish["category"] == cat_name]

    if dishes:
        for dish in dishes:
            picture = dish["dish_picture"] or None

            txt = (f"Название: {dish['name']}\n"
                   f"Цена: {dish['price']}\n"
                   f"Описание: {dish['description']}\n"
                   f"Категория: {dish['category']}\n")

            if picture:
                await message.answer_photo(photo=picture, caption=txt)
            else:
                await message.answer(txt)

    backstep_menu = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Назад к категориям",
                                           callback_data="menu"),
            ]
        ]
    )

    await message.answer('Возврат к категориям:',
                         reply_markup=backstep_menu)
