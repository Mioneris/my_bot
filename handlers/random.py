from aiogram import Router , types
from aiogram.filters import Command
import random
import os #встроенный модуль для предоставления функции взаимодействий с ОС.
# позволяет работать с файловой системой,
# путями, процессами и другими системными функциями.
# используется для работы с файлами и директориями
from aiogram.types import FSInputFile
random_router = Router()

RECIPES = "handlers/recipes_pics"

@random_router.message(Command('recipes'))
async def random_recipes(message: types.Message):
    recipes_dirs = [d for d in os.listdir(RECIPES) if os.path.isdir(os.path.join(RECIPES, d))]

    chosen_recipe = random.choice(recipes_dirs)
    recipes = os.path.join(RECIPES, chosen_recipe)

    recipe_txt = None
    recipe_img = None

    for file in os.listdir(recipes):
        if file.endswith('.txt'):
            recipe_txt = os.path.join(recipes, file)
        elif file.endswith('.jpg'):
            recipe_img = os.path.join(recipes, file)

    if not recipe_txt or not recipe_img:
        await message.answer('Ошибка')
        return

    with open(recipe_txt, 'r', encoding='utf-8') as f: #кодировка utf-8 для поддержания символов вне ASCII(кириллица)
        recipe_txt_send = f.read().strip()

    photo = FSInputFile(recipe_img)

    await message.reply_photo(photo=photo, caption='Изображение блюда')
    # здесь происходит обход ограничения количества символов

    MAX_CAPTION = 1024
    while len(recipe_txt_send) > MAX_CAPTION:
        parts = recipe_txt_send[: MAX_CAPTION]
        recipe_txt_send = recipe_txt_send[MAX_CAPTION:]
        await message.answer(parts)

    if recipe_txt_send:
        await message.answer(str(recipe_txt_send))
