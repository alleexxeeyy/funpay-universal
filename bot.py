from core.modules_manager import load_modules, connect_modules, set_modules

from core.console import set_title
import asyncio
from threading import Thread
import ctypes
from settings import Config
import traceback
from utils.logger import get_logger
logger = get_logger("UNIVERSAL")
from colorama import init, Fore, Style
init()

from fpbot.funpaybot import FunPayBot
from services.updater import Updater

class BotsManager:
    """ Класс для управления запусками ботов """

    def __init__(self):
        self.tgbot = None

    async def start_funpay_bot(self):
        """ Запускает FunPay бота в отдельном потоке """
        this_loop = asyncio.get_running_loop()
        self.fpbot_loop = asyncio.new_event_loop()
        self.fpbot = FunPayBot(self.tgbot, this_loop)

        def run():
            self.fpbot_loop.run_until_complete(self.fpbot.run_bot())
        
        self.fpbot_thread = Thread(target=run, daemon=True)
        self.fpbot_thread.start()

    async def start_telegram_bot(self) -> None:
        """ Запускает Telegram бота """
        from tgbot.telegrambot import TelegramBot
        config = Config().get()
        self.tgbot = TelegramBot(config["tg_bot_token"])
        
        await self.start_funpay_bot()
        await self.tgbot.run_bot()


if __name__ == "__main__":
    """ Запуск всех ботов """
    from bot_settings.app import CURRENT_VERSION
    try:
        set_title(f"FunPay Universal v{CURRENT_VERSION} by @alleexxeeyy")
        print(f"\n   {Fore.CYAN}FunPay Universal {Fore.WHITE}v{Fore.LIGHTWHITE_EX}{CURRENT_VERSION}"
              f"\n   {Fore.WHITE}→ tg: {Fore.LIGHTWHITE_EX}@alleexxeeyy"
              f"\n   {Fore.WHITE}→ tg channel: {Fore.LIGHTWHITE_EX}@alexeyproduction\n")
        
        if Updater.check_for_updates():
            exit()
        
        config = Config().get()
        if not config["golden_key"]:
            print(f"{Fore.WHITE}🫸  Постойте... Не обнаружил в конфиге необходимых для работы бота данных. "
                  f"Возможно вы запускаете его впервые, поэтому давайте проведём быструю настройку конфига, чтобы вы смогли приступить к работе.")
            Config().configure_config()
        
        print(f"{Fore.WHITE}⏳ Загружаю и подключаю модули...")
        modules = load_modules()
        if len(modules) == 0:
            print(f"{Fore.WHITE}Модулей не обнаружено")
        set_modules(modules)
        
        if len(modules) > 0:
            connect_modules(modules)
        
        for module in modules:
            if "ON_MODULE_CONNECTED" in module.bot_event_handlers and module.enabled:
                for handler in module.bot_event_handlers["ON_MODULE_CONNECTED"]:
                    try:
                        handler(module)
                    except Exception as e:
                        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_MODULE_CONNECTED: {Fore.WHITE}{e}")

        from core.handlers_manager import _bot_event_handlers

        def handle_on_init():
            """ 
            Запускается при инициализации софта.
            Запускает за собой все хендлеры ON_INIT
            """
            if "ON_INIT" in _bot_event_handlers:
                for handler in _bot_event_handlers["ON_INIT"]:
                    try:
                        handler()
                    except Exception as e:
                        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_INIT: {Fore.WHITE}{e}")
        handle_on_init()
        
        print(f"{Fore.WHITE}🤖 Запускаю бота...\n")
        asyncio.run(BotsManager.start_telegram_bot())
    except Exception as e:
        print(traceback.print_exc())