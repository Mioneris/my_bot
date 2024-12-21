from aiogram import Router, types
from aiogram.filters import Command

start_router = Router()

users = set()

commands = ('/myinfo\n'
            '/recipes')


@start_router.message(Command('start'))
async def start(message: types.Message):
    name = message.from_user.first_name
    user_id = message.from_user.id
    users.add(user_id)
    user_count = len(users)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text='Информация о Вас', callback_data="my_info"),
                types.InlineKeyboardButton(text='Случайный рецепт из бота', callback_data="recipes")
            ],
            [
                types.InlineKeyboardButton(text="Оставить отзыв", callback_data="start_review"),
                types.InlineKeyboardButton(text='Меню заведения', callback_data="menu")
            ],
            [
                types.InlineKeyboardButton(text='Админ. редактор', callback_data="start_editing")
            ]
        ])

    await message.answer(f'Привет, {name}!\n'
                         f' Наш бот обслуживает уже {user_count} пользователей.\n'
                         f'Ниже предоставлен доступный функционал бота\n',
                         reply_markup=keyboard)
