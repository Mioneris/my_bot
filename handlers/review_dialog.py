from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot_config import database
import datetime
from .keyboards import create_keyboard

review_router = Router()
users = set()


class RestourantReview(StatesGroup):
    name = State()
    contact_info = State()
    food_rating = State()
    cleanliness_rating = State()
    extra_comments = State()
    confirm_review = State()


RATING_DICT = {
    "ужасно": 1,
    "плохо": 2,
    "нормально": 3,
    "хорошо": 4,
    "отлично": 5
}


def stop_review():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отменить отзыв', callback_data="stop")
            ]
        ], resize_keyboard=True
    )


@review_router.callback_query(F.data == "stop")
async def cancel_review(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.message.answer('Вы отменили составление отзыва.',
                                  reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    users.discard(user_id)
    await callback.answer()


@review_router.callback_query(F.data == "start_review")
async def start_review(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = database.check_user_id(user_id)

    if user:
        await callback.message.answer('Вы уже оставляли отзыв!')
        await callback.answer()
        await state.clear()
        return

    users.add(user_id)

    await callback.message.answer('Вы начали оставлять отзыв.\n'
                                  'Для отмены нажмите кнопку ниже.')
    await callback.message.answer("Как Вас зовут?", reply_markup=stop_review())
    await callback.answer()
    await state.set_state(RestourantReview.name)


@review_router.message(RestourantReview.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name.isalpha():
        await message.answer('Пожалуйста, используйте буквы для ввода имени.', reply_markup=stop_review())
        return

    await state.update_data(name=name)
    await message.answer('пожалуйста, оставьте контактные данные для обратной связи '
                         '(Контактный номер телефона/Инстаграм)', reply_markup=stop_review())
    await state.set_state(RestourantReview.contact_info)


@review_router.message(RestourantReview.contact_info)
async def get_contact_info(message: types.Message, state: FSMContext):
    contact_info = message.text.strip()
    await state.update_data(contact_info=contact_info)

    await message.answer('Пожалуйста, оцените блюдо по шкале от 1 до 5.',
                         reply_markup=create_keyboard())
    await state.set_state(RestourantReview.food_rating)


@review_router.callback_query(RestourantReview.food_rating)
@review_router.message(RestourantReview.food_rating)
async def get_food_rating(event: types.Message | CallbackQuery, state: FSMContext):
    await (handle_rating
           (event,
            state,
            "food_rating",
            RestourantReview.cleanliness_rating,
            "оцените чистоту заведения"))


@review_router.callback_query(RestourantReview.cleanliness_rating)
@review_router.message(RestourantReview.cleanliness_rating)
async def get_cleanliness_rating(event: types.Message | CallbackQuery, state: FSMContext):
    await (handle_rating
           (event,
            state,
            "cleanliness_rating",
            RestourantReview.extra_comments,
            "предложения/пожелания",
            final_step=True))


async def handle_rating(event, state, current_field, next_state,
                        next_question, final_step=False):
    rating = None

    send_response = None

    if isinstance(event, types.Message):
        rating = event.text.strip().lower()
        send_response = event.answer

    elif isinstance(event, CallbackQuery):
        rating = event.data.strip().lower()
        send_response = event.message.answer
    else:
        return

    if rating.isdigit() and 1 <= int(rating) <= 5:
        rating = int(rating)

    elif rating in RATING_DICT:
        rating = RATING_DICT[rating]

    else:
        await send_response("Пожалуйста, укажите корректную оценку.", reply_markup=create_keyboard())
        return

    await state.update_data(**{current_field: rating})
    await send_response('Благодарим за Вашу оценку!', reply_markup=stop_review())

    if final_step:
        await send_response('Пожалуйста, оставьте свои пожелания/предложения(до 300 символов).',
                            reply_markup=stop_review())
        await state.set_state(next_state)

    else:
        await send_response(f'Пожалуйста, оцените {next_question} по шкале от 1 до 5.',
                            reply_markup=create_keyboard())
        await state.set_state(next_state)


@review_router.message(RestourantReview.extra_comments)
async def extra_comments(message: types.Message, state: FSMContext):
    comments = message.text.strip()
    if len(comments) > 300:
        await message.answer('Допустимое количество символов - 300', reply_markup=stop_review())
        return

    await state.update_data(extra_comments=comments)
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    await state.update_data(user_id=message.from_user.id)
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
            f"Дата отзыва: {data['review_date']}", reply_markup=types.ReplyKeyboardRemove()))

    await message.answer('Отзыв составлен.\n'
                         'Подтверждаете корректность написаного отзыва?', reply_markup=kb)

    await state.set_state(RestourantReview.confirm_review)


@review_router.callback_query(F.data == "YES")
async def confirm_review(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    database.save_review_results(data)
    await callback.message.answer("Ваш отзыв успешно сохранен. Спасибо!", reply_markup=types.ReplyKeyboardRemove())
    await callback.answer()
    await state.clear()


@review_router.callback_query(F.data == "NO")
async def retry_review(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if user_id in users:
        users.remove(user_id)

    await callback.message.answer("Отзыв возможно изменить.\n"
                                  "Начнем сначала!", reply_markup=types.ReplyKeyboardRemove())
    await callback.answer()
    await state.clear()
    await start_review(callback, state)
