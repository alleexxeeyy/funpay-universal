import os
import sys
import asyncio
import traceback
from colorama import Fore, init as init_colorama
from logging import getLogger

from __init__ import ACCENT_COLOR, VERSION
from core.utils import (
    set_title, 
    setup_logger, 
    install_requirements, 
    patch_requests, 
    init_main_loop, 
    run_async_in_thread, 
    acquire_instance_lock
)
from core.modules import (
    load_modules, 
    set_modules, 
    connect_modules
)
from core.handlers import call_bot_event
from updater import (
    check_for_updates, 
    check_new_releases_task
)
from utils import configure_config


logger = getLogger("universal")

try:
    main_loop = asyncio.get_running_loop()
except RuntimeError:
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)

# патч colorama: на Linux без TTY (запуск через systemd или os.execv)
# winterm=None и colorama падает в convert_osc -> set_title
# патчим convert_osc напрямую чтобы это работало при любом способе запуска
import colorama.ansitowin32 as _a32
if not sys.stdout.isatty():
    class _FakeWinTerm:
        def set_title(self, t): pass
        def set_cursor_position(self, *a, **k): pass
        def set_foreground(self, *a, **k): pass
        def set_background(self, *a, **k): pass
        def reset_all(self, *a, **k): pass
        def style(self, *a, **k): pass
    _a32.winterm = _FakeWinTerm()
    _orig_osc = _a32.AnsiToWin32.convert_osc
    def _safe_osc(self, text):
        try: return _orig_osc(self, text)
        except (AttributeError, TypeError): return text
    _a32.AnsiToWin32.convert_osc = _safe_osc

init_colorama()
init_main_loop(main_loop)


async def clear_logs_task():
    from settings import Settings as sett
    
    path = "logs/latest.log"
    while True:
        if os.path.exists(path):
            file_size_bytes = os.path.getsize(path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            config = sett.get("config")
            if file_size_mb > config["logs"]["max_file_size"]:
                with open(path, 'w'):
                    pass
        await asyncio.sleep(30)


async def start_telegram_bot(from_tg=False):
    from tgbot.telegrambot import TelegramBot
    run_async_in_thread(TelegramBot().run_bot, (from_tg,))


async def start_funpay_bot():
    from fpbot.funpaybot import FunPayBot
    await FunPayBot().run_bot()


def show_panel(title: str, body: str, color: str):
    try:
        from core.console import print_panel
        print_panel(title, body, color, width=72)
    except Exception: # rich ещё не установлен или сам и упал — пишем как есть
        print(f"\n{title}\n{body}\n")


if __name__ == "__main__":
    running_pid = acquire_instance_lock()
    if running_pid is not None:
        show_panel(
            f"{Fore.LIGHTRED_EX}■ Бот уже запущен",
            f"FunPay Universal из этой папки уже работает в другом окне{f' (процесс {running_pid})' if running_pid else ''}. "
            f"Закройте это окно — если запустить одного бота дважды, заказы и сообщения будут обрабатываться по два раза.\n\n"
            f"{Fore.LIGHTBLACK_EX}Если бот на самом деле не запущен — завершите зависший процесс python и попробуйте снова.",
            "red"
        )
        sys.exit(1)

    try:
        from_tg = "--from_tg" in sys.argv

        install_requirements("requirements.txt") # установка недостающих зависимостей, если таковые есть
        patch_requests()
        setup_logger()
        
        set_title(f"FunPay Universal v{VERSION} by @friedfluoride")
        from core.console import print_panel
        print_panel(
            f"{ACCENT_COLOR}FunPay Universal {Fore.LIGHTWHITE_EX}v{VERSION} {Fore.LIGHTBLACK_EX}· by {Fore.LIGHTYELLOW_EX}@friedfluoride (fried)",
            [
                ("GitHub", "github.com/alleexxeeyy/funpay-universal"),
                ("Новости", "t.me/friedfunpay"),
                ("Плагины", "t.me/friedshopbot")
            ],
            color="yellow",
            width=72
        )
        
        check_for_updates()
        configure_config()

        modules = load_modules()
        set_modules(modules)
        asyncio.run(connect_modules(modules))
        
        main_loop.run_until_complete(start_telegram_bot(from_tg))
        main_loop.run_until_complete(start_funpay_bot())

        main_loop.create_task(clear_logs_task())
        main_loop.create_task(check_new_releases_task())

        asyncio.run(call_bot_event("ON_INIT"))

        main_loop.run_forever()
    except Exception as e:
        traceback.print_exc()
        show_panel(
            f"{Fore.LIGHTRED_EX}■ Бот словил непредвиденную ошибку и был выключен",
            f"Попробуйте найти свою проблему в статье с самыми частыми ошибками:\n"
            f"{Fore.LIGHTWHITE_EX}https://devfried.com/docs/faq/ {Fore.LIGHTBLACK_EX}(CTRL + Клик ЛКМ)",
            "red"
        )
    except KeyboardInterrupt:
        show_panel(f"{Fore.YELLOW}Работа бота остановлена", f"{Fore.LIGHTBLACK_EX}Вы нажали Ctrl + C", "yellow")