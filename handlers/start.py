from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .review_dialog import start_review

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
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton
             (text="Оставить отзыв", callback_data="start_review")]
        ])

    await message.answer(f'Hello, {name}!'
                         f' Our bot already serves {user_count} users.\n'
                         f'Available Commands:\n'
                         f' {commands}', reply_markup=keyboard)

