
from aiogram import Router , types
from aiogram.filters import Command

start_router = Router()

users = set()
@start_router.message(Command('start'))
async def start(message: types.Message):
    name = message.from_user.first_name
    user_id = message.from_user.id

    users.add(user_id)

    user_count = len(users)

    commands = ('/myinfo\n'
                '/recipes')

    await message.answer(f'Hello, {name}!'
                         f' Our bot already serves {user_count} users.\n'
                         f'Available Commands:\n'
                         f' {commands}')