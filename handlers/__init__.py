from aiogram import Router, F

from .random import random_router
from .start import start_router
from .my_info import my_info_router
from .dish_edit import dish_management_router
from .menu import menu_router
from .review_dialog import review_router

private_router = Router()

private_router.include_routers(start_router,
                               random_router,
                               my_info_router,
                               review_router,
                               menu_router,
                               dish_management_router)

private_router.message.filter(F.chat.type == "private")
private_router.callback_query.filter(F.chat.type == "private")
