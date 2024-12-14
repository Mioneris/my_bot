from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3

review_router = Router()

users = set()


class RestourantReview(StatesGroup):
    name = State()
    contact_info = State()
    food_rating = State()
    cleanliness_rating = State()
    extra_comments = State()


@review_router.callback_query(F.data == "start_review")
async def start_review(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if user_id in users:
        await callback.message.answer('Вы уже оставляли отзыв!')
        await callback.answer()
        await state.clear()
        return

    users.add(user_id)

    await callback.message.answer('Вы начали оставлять отзыв.')

    await callback.message.answer("Как Вас зовут?")
    await callback.answer()
    await state.set_state(RestourantReview.name)


@review_router.message(RestourantReview.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    print(name)
    await state.update_data(name=message.text)
    await message.answer('пожалуйста, оставьте контактные данные для обратной связи '
                         '(Контактный номер телефона/Инстаграм)')
    await state.set_state(RestourantReview.contact_info)


@review_router.message(RestourantReview.contact_info)
async def get_contact_info(message: types.Message, state: FSMContext):
    contact_info = message.text
    print(contact_info)
    await state.update_data(contact_info=message.text)
    get_food_rating_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
        ]
    )
    await message.answer('Пожалуйста, оцените блюдо по шкале от 1 до 5.', reply_markup=get_food_rating_kb)
    await state.set_state(RestourantReview.food_rating)


@review_router.message(RestourantReview.food_rating)
async def get_food_rating_manual(message: types.Message, state: FSMContext):
    food_rating = message.text
    if food_rating.isdigit():
        food_rating = int(food_rating)
        if 1 <= food_rating <= 5:
            await state.update_data(food_rating=food_rating)
            await message.answer("Благодарим за Вашу оценку!")

            get_cleanlinnes_rating_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
                ]
            )
            await message.answer('Пожалуйста, оцените чистоту нашего заведения по шкале от 1 до 5.',
                                 reply_markup=get_cleanlinnes_rating_kb)
            await state.set_state(RestourantReview.cleanliness_rating)
        else:
            await message.answer("Пожалуйста, укажите оценку от 1 до 5.")
            return
    else:
        await message.answer("Пожалуйста, укажите оценку от 1 до 5.")
        return


@review_router.callback_query(RestourantReview.food_rating)
async def get_food_rating_callback(callback: CallbackQuery, state: FSMContext):
    food_rating = callback.data
    if food_rating.isdigit():
        food_rating = int(food_rating)
        if 1 <= food_rating <= 5:
            await state.update_data(food_rating=food_rating)
            await callback.message.answer('Благодарим за Вашу оценку!')

            get_cleanlinnes_rating_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
                ]
            )
            await callback.message.answer('Пожалуйста, оцените чистоту нашего заведения по шкале от 1 до 5.',
                                          reply_markup=get_cleanlinnes_rating_kb)
            await callback.answer()
            await state.set_state(RestourantReview.cleanliness_rating)
        else:
            await callback.answer('Пожалуйста, выберите оценку от 1 до 5.')
            return


@review_router.message(RestourantReview.cleanliness_rating)
async def get_cleanliness_rating_manual(message: types.Message, state: FSMContext):
    cleanliness_rating = message.text
    if cleanliness_rating.isdigit():
        cleanliness_rating = int(cleanliness_rating)
        if 1 <= cleanliness_rating <= 5:
            await state.update_data(cleanliness_rating=cleanliness_rating)
            await message.answer('Благодарим за Вашу оценку! Пожалуйста, оставьте свои предложения/пожелания.')
            await message.answer('Допустимое количество символов - 300.')
            await state.set_state(RestourantReview.extra_comments)
        else:
            await message.answer('Пожалуйста, выберите оценку от 1 до 5')
            return
    else:
        await message.answer('Пожалуйста, выберите оценку от 1 до 5')
        return


@review_router.callback_query(RestourantReview.cleanliness_rating)
async def get_cleanliness_rating_callback(callback: CallbackQuery, state: FSMContext):
    cleanliness_rating = callback.data
    if cleanliness_rating.isdigit():
        cleanliness_rating = int(cleanliness_rating)
        if 1 <= cleanliness_rating <= 5:
            await state.update_data(cleanliness_rating=cleanliness_rating)
            await callback.message.answer('Благодарим за Вашу оценку! '
                                          'Пожалуйста, оставьте свои предложения/пожелания.')
            await callback.message.answer('Допустимое количество символов - 300.')
            await callback.answer()
            await state.set_state(RestourantReview.extra_comments)
        else:
            await callback.answer('Пожалуйста, выберите оценку от 1 до 5')
            return


@review_router.message(RestourantReview.extra_comments)
async def extra_comments(message: types.Message, state: FSMContext):
    if len(message.text.strip()) > 300:
        await message.answer('Допустимое количество символов - 300')
        return
    await state.update_data(extra_comments=message.text)
    data = await state.get_data()

    with sqlite3.connect('db.review_results') as connection:
        connection.execute("""INSERT INTO review_results
        (name, contact_info,
         food_rating, cleanliness_rating,
          extra_comments) VALUES (?, ?, ?, ?, ?)""",
                           (data['name'], data['contact_info'],
                            data['food_rating'], data['cleanliness_rating'],
                            data['extra_comments'])
                           )

    await (message.answer
           (f"Благодарим Вас за оставленный отзыв!\n"
            f"Имя: {data['name']}\n"
            f"Контакт: {data['contact_info']}\n"
            f"Оценка блюда: {data['food_rating']}\n"
            f"Оценка санитарии заведения: {data['cleanliness_rating']}\n"
            f"Коментарий: {data['extra_comments']}"))

    await state.clear()
