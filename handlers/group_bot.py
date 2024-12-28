from aiogram import Router, F, types
from aiogram.types import ChatMember

group_router = Router()
group_router.message.filter(F.chat.type != 'private')

BAD_WORDS = ('Аниме', "Анимешник", "Наруто")


@group_router.chat_member()
async def group_greeting(chat_member_update: types.ChatMember):
    if chat_member_update.new_chat_member.status == ChatMember.MEMBER:
        user = chat_member_update.new_chat_member.username

        welcome_message = (f"Приветсвую,{user.first_name}!\n"
                           f" Нашему комьюнити чуждо АНИ*Е и мы отвергаем любое обсуждение АНИ*Е.\n"
                           f"Пожалуйста, будь дружелюбным и соблюдай местные традиции.")

        await chat_member_update.bot.send_message(chat_member_update.chat.id, welcome_message)

        if any(bad_word.lower() in user.full_name.lower() for bad_word in BAD_WORDS):
            await chat_member_update.bot.send_message(
                chat_member_update.chat.id,
                f'{user.first_name}, в твоем имени запрещенные слова. Мы осуждаем тебя!'
            )


@group_router.message()
async def bad_words_check(message: types.Message):
    for word in BAD_WORDS:
        if word in message.text:
            await message.answer("Ты не можешь использовать эти слова!\n"
                                 "Ты предупрежден, будь аккуратнее.\n"
                                 "Следующее нарушение правил будет иметь последствия.")
