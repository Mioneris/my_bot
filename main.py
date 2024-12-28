import asyncio
from handlers.group_bot import group_router
from handlers import private_router
from bot_config import dp, bot, database
import logging


async def on_startup(bot):
    database.create_tables()
    database.insert_categories()


async def main():
    dp.include_routers(private_router,
                       group_router)

    dp.startup.register(on_startup)
    # запуск бота
    await dp.start_polling(bot)


# async def on_startup(bot):
#     database.create_tables()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
