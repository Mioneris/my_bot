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


def start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Информация о Вас', callback_data="my_info"),
                InlineKeyboardButton(text='Случайный рецепт из бота', callback_data="recipes")
            ],
            [
                InlineKeyboardButton(text="Оставить отзыв", callback_data="start_review"),
                InlineKeyboardButton(text='Меню заведения', callback_data="menu")
            ],
            [
                InlineKeyboardButton(text='Админ. редактор', callback_data="start_editing")
            ]
        ])
