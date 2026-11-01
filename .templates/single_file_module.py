from colorama import Fore
from logging import getLogger

from core.modules import Module
from FunPayAPI.updater.events import EventTypes, NewMessageEvent


ACCENT_COLOR = Fore.YELLOW
PREFIX = f"{ACCENT_COLOR}example {Fore.LIGHTBLACK_EX}·{Fore.WHITE}"
VERSION = "1.0"
NAME = "example"
DESCRIPTION = "Одиночный модуль-пример для бота FunPay Universal. Отвечает «понг» на сообщение «пинг»"
AUTHORS = "@friedfluoride"
LINKS = "https://t.me/friedfluoride, https://t.me/friedfunpay"


logger = getLogger(NAME)
_module: Module = None


def set_module(new: Module):
    global _module
    _module = new


def get_module():
    return _module


async def on_module_enabled(module: Module):
    set_module(module)
    logger.info(f"{PREFIX} Модуль подключен и активен")


async def on_new_message(bot, event: NewMessageEvent):
    message = event.message
    if message.author == bot.account.username:
        return
    if (message.text or "").strip().lower() == "пинг":
        bot.send_message(message.chat_id, "понг", chat_name=message.chat_name)


BOT_EVENT_HANDLERS = {
    "ON_MODULE_ENABLED": [on_module_enabled]
}
FUNPAY_EVENT_HANDLERS = {
    EventTypes.NEW_MESSAGE: [on_new_message]
}
TELEGRAM_BOT_ROUTERS = []
