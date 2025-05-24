from .fpbot.funpaybot_handlers import FunPayBotHandlers
from .tgbot.telegrambot_handlers import TelegramBotHandlers
from .tgbot import router
from .meta import *
from colorama import Fore
from core.modules_manager import disable_module, Module
from .settings import Config

from FunPayAPI.updater.events import EventTypes

_module: Module = None
def get_module(module: Module):
    global _module
    _module = module

def handler_on_init():
    print(f"{PREFIX} Модуль инициализирован")
    if not Config().get().get("some_first_int_value"):
        print(f"{PREFIX} 🫸  Постойте... Не обнаружил в конфиге необходимых для работы модуля данных. "
              f"Возможно вы запускаете его впервые, поэтому давайте проведём быструю настройку конфига, чтобы вы смогли приступить к работе.")
        Config().configure_config()


fpbhandlers = FunPayBotHandlers()
BOT_EVENT_HANDLERS = {
    "ON_MODULE_CONNECTED": [get_module],
    "ON_INIT": [handler_on_init],
    "ON_FUNPAY_BOT_INIT": [fpbhandlers.handler_on_funpay_bot_init],
    "ON_TELEGRAM_BOT_INIT": [TelegramBotHandlers.handler_on_telegram_bot_init]
}
FUNPAY_EVENT_HANDLERS = {
    EventTypes.NEW_MESSAGE: [fpbhandlers.handler_new_message],
    EventTypes.NEW_ORDER: [fpbhandlers.handler_new_order]
}
TELEGRAM_BOT_ROUTERS = [router]