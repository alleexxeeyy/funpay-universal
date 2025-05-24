from aiogram.types import BotCommand

from tgbot.telegrambot import TelegramBot
from tgbot import router as bot_router
import tgbot.templates.user_templates as Templates

from ..settings import Config
from ..meta import NAME
from utils.logger import get_logger
logger = get_logger(f"{NAME}.TelegramBot")



class TelegramBotHandlers:
    """ Класс, содержащий хендлеры ивентов Telegram бота """

    async def handler_on_telegram_bot_init(tgbot: TelegramBot) -> None:
        """ Хендлер инициализации Telegram бота """

        main_menu_commands = await tgbot.bot.get_my_commands()
        autobooster_menu_commands = [
            BotCommand(command=f"/{NAME}",
                       description=f"🔌📈 Управление модулем {NAME}")
        ]
        await tgbot.bot.set_my_commands(list(main_menu_commands + autobooster_menu_commands))