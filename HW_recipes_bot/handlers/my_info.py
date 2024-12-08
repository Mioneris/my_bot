from aiogram import Router , types
from aiogram.filters import Command

my_info_router = Router()

@my_info_router.message(Command('myinfo'))
async def my_info(message: types.Message):
    info = message.from_user.first_name, message.from_user.username, message.from_user.id
    await message.reply(f'Information about you:\n'
                         f'First Name : {info[0]},\n'
                         f'Username : {info[1]},\n'
                         f'ID : {info[2]},\n')
