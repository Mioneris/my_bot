from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot_config import database
import datetime

review_router = Router()
users = set()


class RestourantReview(StatesGroup):
    name = State()
    contact_info = State()
    food_rating = State()
    cleanliness_rating = State()
    extra_comments = State()
    confirm_review = State()


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
    if not name.isalpha():
        await message.answer('Пожалуйста, используйте буквы для ввода имени.')
        return
    await state.update_data(name=message.text)
    await message.answer('пожалуйста, оставьте контактные данные для обратной связи '
                         '(Контактный номер телефона/Инстаграм)')
    await state.set_state(RestourantReview.contact_info)


@review_router.message(RestourantReview.contact_info)
async def get_contact_info(message: types.Message, state: FSMContext):
    contact_info = message.text.strip()
    await state.update_data(contact_info=contact_info)
    get_food_rating_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
        ]
    )
    await message.answer('Пожалуйста, оцените блюдо по шкале от 1 до 5.', reply_markup=get_food_rating_kb)
    await state.set_state(RestourantReview.food_rating)


@review_router.callback_query(RestourantReview.food_rating)
@review_router.message(RestourantReview.food_rating)
async def get_food_rating(event: types.Message | types.CallbackQuery, state: FSMContext):
    await (handle_rating
           (event, state, "food_rating", RestourantReview.cleanliness_rating, "чистоту"))


@review_router.callback_query(RestourantReview.cleanliness_rating)
@review_router.message(RestourantReview.cleanliness_rating)
async def get_cleanliness_rating(event: types.Message | types.CallbackQuery, state: FSMContext):
    await (handle_rating
           (event, state, "cleanliness_rating", RestourantReview.extra_comments,
            "предложения/пожелания", final_step=True))


async def handle_rating(event, state, current_field, next_state, next_question, final_step=False):
    rating = None
    send_response = None

    if isinstance(event, types.Message):
        rating = event.text
        send_response = event.answer
    elif isinstance(event, CallbackQuery):
        rating = event.data
        send_response = event.message.answer

    if rating.isdigit() and 1 <= int(rating) <= 5:
        await state.update_data(**{current_field: int(rating)})
        await send_response('Благодарим за Вашу оценку!')

        if final_step:
            await send_response('Пожалуйста, оставьте свои пожелания/предложения(до 300 символов).')
            await state.set_state(next_state)
        else:
            rating_kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
                ]
            )
            await send_response(f'Пожалуйста, оцените {next_question} по шкале от 1 до 5.',
                                reply_markup=rating_kb)
            await state.set_state(next_state)
    else:
        await send_response('Пожалуйста, укажите корретную оценку от 1 до 5.')


@review_router.message(RestourantReview.extra_comments)
async def extra_comments(message: types.Message, state: FSMContext):
    if len(message.text.strip()) > 300:
        await message.answer('Допустимое количество символов - 300')
        return
    await state.update_data(extra_comments=message.text)

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    await state.update_data(review_date=current_date)

    data = await state.get_data()

    kb = InlineKeyboardMarkup(

        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data='YES'),
                InlineKeyboardButton(text="Нет", callback_data='NO')
            ]
        ]
    )

    await (message.answer
           (f"Благодарим Вас за оставленный отзыв!\n"
            f"Имя: {data['name']}\n"
            f"Контакт: {data['contact_info']}\n"
            f"Оценка блюда: {data['food_rating']}\n"
            f"Оценка санитарии заведения: {data['cleanliness_rating']}\n"
            f"Коментарий: {data['extra_comments']}\n"
            f"Дата отзыва: {data['review_date']}"))

    await message.answer('Отзыв составлен.\n'
                         'Подтверждаете корректность написаного отзыва?', reply_markup=kb)

    await state.set_state(RestourantReview.confirm_review)


@review_router.callback_query(F.data == "YES")
async def confirm_review(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    database.save_review_results(data)
    await callback.message.answer("Ваш отзыв успешно сохранен. Спасибо!")
    await callback.answer()
    await state.clear()


@review_router.callback_query(F.data == "NO")
async def retry_review(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if user_id in users:
        users.remove(user_id)

    await callback.message.answer("Отзыв возможно изменить.\n"
                                  "Начнем сначала!")
    await callback.answer()
    await state.clear()
    await start_review(callback, state)



    # with sqlite3.connect('db.sqlite3') as connection:
    #     connection.execute(
    #         """
    #         INSERT INTO review_results
    #         (name, contact_info,
    #         food_rating,
    #         cleanliness_rating,
    #         extra_comments)
    #         VALUES (?, ?, ?, ?, ?)""",
    #                        (data['name'],
    #                         data['contact_info'],
    #                         data['food_rating'],
    #                         data['cleanliness_rating'],
    #                         data['extra_comments'])
    #                        )

#
# @review_router.message(RestourantReview.food_rating)
# async def get_food_rating_manual(message: types.Message, state: FSMContext):
#     food_rating = message.text
#     if food_rating.isdigit():
#         food_rating = int(food_rating)
#         if 1 <= food_rating <= 5:
#             await state.update_data(food_rating=food_rating)
#             await message.answer("Благодарим за Вашу оценку!")
#
#             get_cleanlinnes_rating_kb = InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
#                 ]
#             )
#             await message.answer('Пожалуйста, оцените чистоту нашего заведения по шкале от 1 до 5.',
#                                  reply_markup=get_cleanlinnes_rating_kb)
#             await state.set_state(RestourantReview.cleanliness_rating)
#         else:
#             await message.answer("Пожалуйста, укажите оценку от 1 до 5.")
#             return
#     else:
#         await message.answer("Пожалуйста, укажите оценку от 1 до 5.")
#         return
#
#
# @review_router.callback_query(RestourantReview.food_rating)
# async def get_food_rating_callback(callback: CallbackQuery, state: FSMContext):
#     food_rating = callback.data
#     if food_rating.isdigit():
#         food_rating = int(food_rating)
#         if 1 <= food_rating <= 5:
#             await state.update_data(food_rating=food_rating)
#             await callback.message.answer('Благодарим за Вашу оценку!')
#
#             get_cleanlinnes_rating_kb = InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
#                 ]
#             )
#             await callback.message.answer('Пожалуйста, оцените чистоту нашего заведения по шкале от 1 до 5.',
#                                           reply_markup=get_cleanlinnes_rating_kb)
#             await callback.answer()
#             await state.set_state(RestourantReview.cleanliness_rating)
#         else:
#             await callback.answer('Пожалуйста, выберите оценку от 1 до 5.')
#             return
#
#
# @review_router.message(RestourantReview.cleanliness_rating)
# async def get_cleanliness_rating_manual(message: types.Message, state: FSMContext):
#     cleanliness_rating = message.text
#     if cleanliness_rating.isdigit():
#         cleanliness_rating = int(cleanliness_rating)
#         if 1 <= cleanliness_rating <= 5:
#             await state.update_data(cleanliness_rating=cleanliness_rating)
#             await message.answer('Благодарим за Вашу оценку! Пожалуйста, оставьте свои предложения/пожелания.')
#             await message.answer('Допустимое количество символов - 300.')
#             await state.set_state(RestourantReview.extra_comments)
#         else:
#             await message.answer('Пожалуйста, выберите оценку от 1 до 5')
#             return
#     else:
#         await message.answer('Пожалуйста, выберите оценку от 1 до 5')
#         return
#
#
# @review_router.callback_query(RestourantReview.cleanliness_rating)
# async def get_cleanliness_rating_callback(callback: CallbackQuery, state: FSMContext):
#     cleanliness_rating = callback.data
#     if cleanliness_rating.isdigit():
#         cleanliness_rating = int(cleanliness_rating)
#         if 1 <= cleanliness_rating <= 5:
#             await state.update_data(cleanliness_rating=cleanliness_rating)
#             await callback.message.answer('Благодарим за Вашу оценку! '
#                                           'Пожалуйста, оставьте свои предложения/пожелания.')
#             await callback.message.answer('Допустимое количество символов - 300.')
#             await callback.answer()
#             await state.set_state(RestourantReview.extra_comments)
#         else:
#             await callback.answer('Пожалуйста, выберите оценку от 1 до 5')
#             return
#
