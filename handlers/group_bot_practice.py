# import re
# from aiogram import Router, F, types
# from aiogram.types import ChatMemberUpdated, Message
# from datetime import timedelta
# from natasha import MorphVocab, Doc, Segmenter
# import pymorphy2
# from pymorphy2 import MorphAnalyzer
#
# group_router = Router()
# group_router.message.filter(F.chat.type != 'private')
#
# BAD_WORDS = ('Аниме', "Анимешник", "Наруто")
#
# morph_vocab = MorphVocab()
# segmenter = Segmenter()
#
#
#
#
#
#
# def normalize_words(words):
#     normalized_words = []
#     for word in words:
#         doc = Doc(word)
#         doc.segment(segmenter)
#         doc.tag_morph(morph_vocab)
#
#         if doc.tokens:
#             normalized_words.append(doc.tokens[0].lemma.lower())
#     return normalized_words
#
#
# BAD_WORDS_NORMALIZED = normalize_words(BAD_WORDS)
#
#
# def contains_bad_word(txt: str) -> bool:
#     txt = txt.lower()
#     txt = re.sub(r'[^\w\s]', '', txt)
#
#     if not txt.strip():
#         return False
#
#     try:
#         doc = Doc(txt)
#         doc.segment(segmenter)
#         doc.tag_morph(morph_vocab)
#
#         for token in doc.tokens:
#             if token.lemma and token.lemma.lower() in BAD_WORDS_NORMALIZED:
#                 return True
#
#     except Exception as e:
#         print(e)
#         return False
#
#     return False
#
#
# @group_router.message(F.text)
# async def check_message(message: Message):
#     if contains_bad_word(message.text):
#         await message.delete()
#         await message.answer(f"{message.from_user.first_name or 'Пятушка'} , Ты не можешь использовать эти слова!\n"
#                              "Ты предупрежден, будь аккуратнее.\n"
#                              "Следующее нарушение правил будет иметь последствия.")
#
#
# @group_router.chat_member()
# async def group_greeting(chat_member_update: types.ChatMemberUpdated):
#     if chat_member_update.new_chat_member.status == "member":
#         user = chat_member_update.new_chat_member.user
#         first_name = user.first_name or 'Пятушка'
#         full_name = user.full_name or 'Пятушка'
#
#         welcome_message = (f"Приветсвую,{first_name}!\n"
#                            f" Нашему комьюнити чуждо АНИ*Е и мы отвергаем любое обсуждение АНИ*Е.\n"
#                            f"Пожалуйста, будь дружелюбным и соблюдай местные традиции.")
#
#         await chat_member_update.bot.send_message(chat_member_update.chat.id, welcome_message)
#
#         if contains_bad_word(full_name):
#             await chat_member_update.bot.send_message(
#                 chat_member_update.chat.id,
#                 f'{user.first_name}, в твоем имени запрещенные слова. Мы осуждаем тебя!'
#             )
