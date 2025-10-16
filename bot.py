import asyncio
import re
import string
import requests
from threading import Thread
import traceback
from colorama import init, Fore, Style
init()
from logging import getLogger
logger = getLogger(f"universal")

from FunPayAPI.account import Account
from FunPayAPI.common.exceptions import UnauthorizedError

from __init__ import ACCENT_COLOR, VERSION
from settings import Settings as sett
from core.utils import set_title, setup_logger, install_requirements, patch_requests
from core.modules import load_modules, set_modules, connect_modules
from core.handlers import get_bot_event_handlers
from services.updater import check_for_updates


async def start_telegram_bot():
    from tgbot.telegrambot import TelegramBot
    config = sett.get("config")
    tgbot = TelegramBot(config["telegram"]["api"]["token"])
    await tgbot.run_bot()


async def start_funpay_bot():
    from fpbot.funpaybot import FunPayBot
    def run():
        asyncio.new_event_loop().run_until_complete(FunPayBot().run_bot())
    Thread(target=run, daemon=True).start()


def check_and_configure_config():
    config = sett.get("config")

    def is_golden_key_valid(s: str) -> bool:
        pattern = r'^[a-z0-9]{32}$'
        return bool(re.match(pattern, s))
    
    def is_fp_account_working() -> bool:
        try:
            proxy = {"https": "http://" + config["funpay"]["api"]["proxy"], "http": "http://" + config["funpay"]["api"]["proxy"]} if config["funpay"]["api"]["proxy"] else None
            Account(golden_key=config["funpay"]["api"]["golden_key"],
                    user_agent=config["funpay"]["api"]["user_agent"],
                    requests_timeout=config["funpay"]["api"]["requests_timeout"],
                    proxy=proxy).get()
            return True
        except:
            return False

    def is_user_agent_valid(ua: str) -> bool:
        if not ua or not (10 <= len(ua) <= 512):
            return False
        allowed_chars = string.ascii_letters + string.digits + string.punctuation + ' '
        return all(c in allowed_chars for c in ua)

    def is_proxy_valid(proxy: str) -> bool:
        ip_pattern = r'(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)'
        pattern_ip_port = re.compile(
            rf'^{ip_pattern}\.{ip_pattern}\.{ip_pattern}\.{ip_pattern}:(\d+)$'
        )
        pattern_auth_ip_port = re.compile(
            rf'^[^:@]+:[^:@]+@{ip_pattern}\.{ip_pattern}\.{ip_pattern}\.{ip_pattern}:(\d+)$'
        )
        match = pattern_ip_port.match(proxy)
        if match:
            port = int(match.group(1))
            return 1 <= port <= 65535
        match = pattern_auth_ip_port.match(proxy)
        if match:
            port = int(match.group(1))
            return 1 <= port <= 65535
        return False
    
    def is_proxy_working(proxy: str, timeout: int = 10) -> bool:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        test_url = "https://funpay.com"
        try:
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    def is_token_valid(token: str) -> bool:
        pattern = r'^\d{7,12}:[A-Za-z0-9_-]{35}$'
        return bool(re.match(pattern, token))
    
    def is_tg_bot_exists() -> bool:
        try:
            response = requests.get(f"https://api.telegram.org/bot{config['telegram']['api']['token']}/getMe", timeout=5)
            data = response.json()
            return data.get("ok", False) is True and data.get("result", {}).get("is_bot", False) is True
        except Exception:
            return False
        
    def is_password_valid(password: str) -> bool:
        if len(password) < 6 or len(password) > 64:
            return False
        common_passwords = {
            "123456", "1234567", "12345678", "123456789", "password", "qwerty",
            "admin", "123123", "111111", "abc123", "letmein", "welcome",
            "monkey", "login", "root", "pass", "test", "000000", "user",
            "qwerty123", "iloveyou"
        }
        if password.lower() in common_passwords:
            return False
        return True
    
    while not config["funpay"]["api"]["golden_key"]:
        print(f"\n{Fore.WHITE}Введите {Fore.YELLOW}golden_key {Fore.WHITE}вашего FunPay аккаунта. Его можно узнать из Cookie-данных, воспользуйтесь расширением Cookie-Editor."
              f"\n  {Fore.WHITE}· Пример: blkrlwv7epmhx21bzqwp3x17bf2yhgre")
        golden_key = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
        if is_golden_key_valid(golden_key):
            config["funpay"]["api"]["golden_key"] = golden_key
            sett.set("config", config)
            print(f"\n{Fore.GREEN}golden_key успешно сохранён в конфиг.")
        else:
            print(f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный golden_key. Убедитесь, что он соответствует формату и попробуйте ещё раз.")

        print(f"\n{Fore.WHITE}Введите {Fore.LIGHTMAGENTA_EX}User Agent {Fore.WHITE}вашего браузера. Его можно скопировать на сайте {Fore.LIGHTWHITE_EX}https://whatmyuseragent.com. Или вы можете пропустить этот параметр, нажав Enter."
              f"\n  {Fore.WHITE}· Пример: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
        user_agent = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
        if not user_agent:
            print(f"\n{Fore.YELLOW}Вы пропустили ввод User Agent. Учтите, что в таком случае бот может работать нестабильно.")
            break
        if is_user_agent_valid(user_agent):
            config["funpay"]["api"]["user_agent"] = user_agent
            sett.set("config", config)
            print(f"\n{Fore.GREEN}User Agent успешно сохранён в конфиг.")
        else:
            print(f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный User Agent. Убедитесь, что в нём нет русских символов и попробуйте ещё раз.")
        
        print(f"\n{Fore.WHITE}Введите {Fore.LIGHTBLUE_EX}IPv4 Прокси {Fore.WHITE}в формате user:password@ip:port или ip:port, если он без авторизации. Если вы не знаете что это, или не хотите устанавливать прокси - пропустите этот параметр, нажав Enter."
              f"\n  {Fore.WHITE}· Пример: DRjcQTm3Yc:m8GnUN8Q9L@46.161.30.187:8000")
        proxy = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
        if not proxy:
            print(f"\n{Fore.WHITE}Вы пропустили ввод прокси.")
            break
        if is_proxy_valid(proxy):
            config["funpay"]["api"]["proxy"] = proxy
            sett.set("config", config)
            print(f"\n{Fore.GREEN}Прокси успешно сохранён в конфиг.")
        else:
            print(f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный Прокси. Убедитесь, что он соответствует формату и попробуйте ещё раз.")

    while not config["telegram"]["api"]["token"]:
        print(f"\n{Fore.WHITE}Введите {Fore.CYAN}Токен вашего Telegram бота{Fore.WHITE}. Бота нужно создать у @BotFather."
              f"\n  {Fore.WHITE}· Пример: 7257913369:AAG2KjLL3-zvvfSQFSVhaTb4w7tR2iXsJXM")
        token = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
        if is_token_valid(token):
            config["telegram"]["api"]["token"] = token
            sett.set("config", config)
            print(f"\n{Fore.GREEN}Токен Telegram бота успешно сохранён в конфиг.")
        else:
            print(f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный токен. Убедитесь, что он соответствует формату и попробуйте ещё раз.")

    while not config["telegram"]["bot"]["password"]:
        print(f"\n{Fore.WHITE}Придумайте и введите {Fore.YELLOW}пароль для вашего Telegram бота{Fore.WHITE}. Бот будет запрашивать этот пароль при каждой новой попытке взаимодействия чужого пользователя с вашим Telegram ботом."
              f"\n  {Fore.WHITE}· Пароль должен быть сложным, длиной не менее 6 и не более 64 символов.")
        password = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
        if is_password_valid(password):
            config["telegram"]["bot"]["password"] = password
            sett.set("config", config)
            print(f"\n{Fore.GREEN}Пароль успешно сохранён в конфиг.")
        else:
            print(f"\n{Fore.LIGHTRED_EX}Ваш пароль не подходит. Убедитесь, что он соответствует формату и не является лёгким и попробуйте ещё раз.")

    if config["funpay"]["api"]["proxy"] and not is_proxy_working(config["funpay"]["api"]["proxy"]):
        print(f"\n{Fore.LIGHTRED_EX}Похоже, что указанный вами прокси не работает. Пожалуйста, проверьте его и введите снова.")
        config["funpay"]["api"]["golden_key"] = ""
        config["funpay"]["api"]["user_agent"] = ""
        config["funpay"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    elif config["funpay"]["api"]["proxy"]:
        logger.info(f"{Fore.WHITE}Прокси успешно работает.")

    if not is_fp_account_working():
        print(f"\n{Fore.LIGHTRED_EX}Не удалось подключиться к вашему FunPay аккаунту. Пожалуйста, убедитесь, что у вас указан верный golden_key и введите его снова.")
        config["funpay"]["api"]["golden_key"] = ""
        config["funpay"]["api"]["user_agent"] = ""
        config["funpay"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    else:
        logger.info(f"{Fore.WHITE}FunPay аккаунт успешно авторизован.")

    if not is_tg_bot_exists():
        print(f"\n{Fore.LIGHTRED_EX}Не удалось подключиться к вашему Telegram боту. Пожалуйста, убедитесь, что у вас указан верный токен и введите его снова.")
        config["telegram"]["api"]["token"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    else:
        logger.info(f"{Fore.WHITE}Telegram бот успешно работает.")


if __name__ == "__main__":
    try:
        install_requirements("requirements.txt") # установка недостающих зависимостей, если таковые есть
        patch_requests()
        setup_logger()
        set_title(f"FunPay Universal v{VERSION} by @alleexxeeyy")
        print(f"\n\n   {ACCENT_COLOR}FunPay Universal {Fore.WHITE}v{Fore.LIGHTWHITE_EX}{VERSION}"
              f"\n   ↳ {Fore.LIGHTWHITE_EX}https://t.me/alleexxeeyy"
              f"\n   ↳ {Fore.LIGHTWHITE_EX}https://t.me/alexeyproduction\n\n")
        
        check_for_updates()
        check_and_configure_config()
        
        modules = load_modules()
        set_modules(modules)
        
        if len(modules) > 0:
            connect_modules(modules)

        bot_event_handlers = get_bot_event_handlers()
        def handle_on_init():
            """ 
            Запускается при инициализации софта.
            Запускает за собой все хендлеры ON_INIT.
            """
            for handler in bot_event_handlers.get("ON_INIT", []):
                try:
                    handler()
                except Exception as e:
                    logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_INIT: {Fore.WHITE}{e}")
        handle_on_init()
        
        asyncio.run(start_funpay_bot())
        asyncio.run(start_telegram_bot())
    except Exception as e:
        traceback.print_exc()
    print(f"\n   {Fore.LIGHTRED_EX}Ваш бот словил непредвиденную ошибку и был выключен."
          f"\n   {Fore.WHITE}Пожалуйста, напишите в Telegram разработчика {Fore.LIGHTWHITE_EX}@alleexxeeyy{Fore.WHITE}, для уточнения причин")
    raise SystemExit(1)