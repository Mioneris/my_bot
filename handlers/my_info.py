from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

my_info_router = Router()


@my_info_router.callback_query(F.data == 'my_info')
async def my_info(callback: CallbackQuery):
    info = callback.from_user.first_name, callback.from_user.username, callback.from_user.id
    await callback.message.reply(f'Информация о пользователе:\n'
                                 f'Имя : {info[0]},\n'
                                 f'Username : {info[1]},\n'
                                 f'ID : {info[2]},\n')
    await callback.answer()
