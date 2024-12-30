import re
from datetime import timedelta
from aiogram import Router, F, types
from aiogram.filters import Command
from bot_config import database

group_router = Router()

group_router.message.filter(F.chat.type != 'private')


# реобразование кода в машиночитаемый формат,
# позволяющий проводить дальнейшую обработку и анализ


@group_router.chat_member()
async def group_greeting(chat_member_update: types.ChatMemberUpdated):
    if chat_member_update.new_chat_member.status == "member":
        user = chat_member_update.new_chat_member.user
        first_name = user.first_name or 'Пятушка'
        welcome_message = (f"Приветсвую,{first_name}!\n"
                           f" Нашему комьюнити чуждо АНИ*Е и мы отвергаем любое обсуждение АНИ*Е.\n"
                           f"Пожалуйста, будь дружелюбным и соблюдай местные традиции.")

        await chat_member_update.bot.send_message(chat_member_update.chat.id, welcome_message)


BAD_WORDS = ('аниме', "анимешник", "наруто")


def parsing_time(time_str: str):
    match = re.match(r'(\d+)([мчдн])', time_str.strip().lower())

    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    if unit == 'м':
        return timedelta(minutes=value)

    elif unit == 'ч':
        return timedelta(hours=value)

    elif unit == 'д':
        return timedelta(days=value)

    elif unit == 'н':
        return timedelta(weeks=value)
    return None

@group_router.message(Command('ban', prefix='!'))
async def user_ban(message: types.Message):
    replay = message.reply_to_message

    if not replay:
        await message.answer('Команда !ban должна быть ответом на сообщение.')
        return

    command_args = message.text.split(maxsplit=1)
    if len(command_args) < 2:
        await message.answer('Укажите время бана.')
        return

    ban_time_str = command_args[1].strip()
    ban_time = parsing_time(ban_time_str)

    if not ban_time:
        await message.answer('Неверный формат периода бана.\n'
                             '1д (день), 3ч (часы), 10м (минуты), 3н (недели)')

    user = message.reply_to_message.from_user.id

    await message.chat.ban(user_id=user,
                           until_date=ban_time)

    await message.answer(f'{user} улетел в бан на {ban_time}')


@group_router.message(F.text)
async def check_bad_words(message: types.Message):
    message_text = message.text.lower()
    user = message.from_user
    user_id = user.id
    user_name = message.from_user.first_name

    database.insert_or_update_user(user_id)

    for word in BAD_WORDS:
        if word in message_text:
            warnings = database.update_warnings(user_id)

            if warnings > 3:
                await message.bot.ban_chat_member(chat_id=message.chat.id,
                                                  user_id=user_id)
                await message.answer(f'{user_name} получил 3 предупреждения и был забанен. Осуждаем!\n'
                                     f'Ты можешь читать, но не писать. ')
                database.ban_user(user_id)
            else:
                await message.answer(f'Мы осуждаем тебя, {user_name}!\n'
                                     f'Это твое {warnings}/3 предупреждение.')
                await message.delete()
                break
