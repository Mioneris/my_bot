from aiogram import Router, types, F
from aiogram.filters import Command
from .keyboards import start_keyboard


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

    await message.answer(f'Привет, {name}!\n'
                         f'Наш бот обслуживает уже {user_count} пользователей.\n'
                         f'Ниже предоставлен доступный функционал бота\n',
                         reply_markup=start_keyboard()
                         )
