import asyncio
from handlers.random import random_router
from handlers.start import start_router
from handlers.my_info import my_info_router
from bot_config import dp,bot
import logging






async def main():
    dp.include_routers(random_router,
                       start_router,
                       my_info_router,)
    # запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())