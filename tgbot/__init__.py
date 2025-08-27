from aiogram import Router

from .handlers import router as handlers_router
from .callback_handlers import router as callback_handlers_router

router = Router()
router.include_routers(callback_handlers_router, handlers_router)

import asyncio
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .telegrambot import TelegramBot


_telegram_bot: 'TelegramBot' = None

def get_telegram_bot() -> 'TelegramBot':
    global _telegram_bot
    return _telegram_bot

def set_telegram_bot(new: 'TelegramBot') -> 'TelegramBot':
    global _telegram_bot
    _telegram_bot = new


_telegram_bot_loop: 'asyncio.AbstractEventLoop' = None

def get_telegram_bot_loop() -> 'asyncio.AbstractEventLoop':
    global _telegram_bot_loop
    return _telegram_bot_loop

def set_telegram_bot_loop(new: 'asyncio.AbstractEventLoop') -> 'asyncio.AbstractEventLoop':
    global _telegram_bot_loop
    _telegram_bot_loop = new