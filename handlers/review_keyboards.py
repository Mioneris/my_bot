from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


RATING_DICT = {
    "ужасно": 1,
    "плохо": 2,
    "нормально": 3,
    "хорошо": 4,
    "отлично": 5
}


def create_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text=key.capitalize(),
                                     callback_data=key)
                for key in RATING_DICT
            ]
        ]
    )
