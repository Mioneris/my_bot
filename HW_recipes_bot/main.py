import asyncio
from handlers.random import random_router
from handlers.start import start_router
from handlers.my_info import my_info_router
from bot_config import dp, bot, database
import logging
from handlers.review_dialog import review_router


async def main():
    dp.include_routers(start_router,
                       random_router,
                       my_info_router,
                       review_router)

    dp.startup.register(on_startup)
    # запуск бота
    await dp.start_polling(bot)


async def on_startup(bot):
    database.create_tables()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
