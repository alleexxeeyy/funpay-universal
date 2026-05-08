import re
import sys
import pytz
import requests
import string
import requests
from datetime import datetime, timedelta
from collections import Counter
from colorama import Fore
from logging import getLogger

from FunPayAPI.account import Account
from settings import Settings as sett
from data import Data as data


logger = getLogger("universal")


def get_event_next_time(last_time_iso, interval):
    return (
        datetime.fromisoformat(last_time_iso) + timedelta(seconds=interval)
        if last_time_iso else datetime.now()
    )


def is_golden_key_valid(s: str) -> bool:
    pattern = r'^[a-z0-9]{32}$'
    return bool(re.match(pattern, s))


def is_fp_account_working() -> bool:
    try:
        config = sett.get("config")
        proxy = {
            "https": "http://" + config["funpay"]["api"]["proxy"], 
            "http": "http://" + config["funpay"]["api"]["proxy"]
        } if config["funpay"]["api"]["proxy"] else None
        Account(
            golden_key=config["funpay"]["api"]["golden_key"],
            user_agent=config["funpay"]["api"]["user_agent"],
            requests_timeout=config["funpay"]["api"]["requests_timeout"],
            proxy=proxy
        ).get()
        return True
    except Exception:
        return False


def is_fp_account_banned() -> bool:
    config = sett.get("config")
    proxy = {
        "https": "http://" + config["funpay"]["api"]["proxy"], 
        "http": "http://" + config["funpay"]["api"]["proxy"]
    } if config["funpay"]["api"]["proxy"] else None
    acc = Account(
        golden_key=config["funpay"]["api"]["golden_key"],
        user_agent=config["funpay"]["api"]["user_agent"],
        requests_timeout=config["funpay"]["api"]["requests_timeout"],
        proxy=proxy
    ).get()
    user = acc.get_user(acc.id)
    return user.banned


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


def is_proxy_working(proxy: str, test_url="https://funpay.com", timeout=10) -> bool:
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        return response.status_code < 404
    except Exception:
        return False


def is_token_valid(token: str) -> bool:
    pattern = r'^\d{7,12}:[A-Za-z0-9_-]{35}$'
    return bool(re.match(pattern, token))


def is_tg_bot_exists() -> bool:
    try:
        config = sett.get("config")
        token = config["telegram"]["api"]["token"]
        proxy = config["telegram"]["api"]["proxy"]
        
        if proxy:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}",
            }
        else:
            proxies = None
        
        response = requests.get(
            f"https://api.telegram.org/bot{token}/getMe", 
            proxies=proxies,
            timeout=5
        )
        
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


def check_and_configure_config():
    config = sett.get("config")

    needs_setup = (
        not config["funpay"]["api"]["golden_key"] or
        not config["telegram"]["api"]["token"] or
        not config["telegram"]["bot"]["password"]
    )

    if needs_setup and not sys.stdin.isatty():
        print(
            f"\n{Fore.YELLOW}⚠️  Бот не настроен!"
            f"\n{Fore.WHITE}Подключитесь к серверу и выполните команду:"
            f"\n\n   {Fore.CYAN}fpuniversal setup"
            f"\n\n{Fore.WHITE}Это запустит интерактивную настройку прямо в терминале.\n"
        )
        sys.exit(0)
    
    while not config["funpay"]["api"]["golden_key"]:
        while not config["funpay"]["api"]["golden_key"]:
            print(
                f"\n{Fore.LIGHTYELLOW_EX}┌────┤ Введите {Fore.YELLOW}Golden Key {Fore.LIGHTYELLOW_EX}├──────────────────────┐{Fore.WHITE}"
                f"\n\n  Авторизуйтесь в свой аккаунт на FunPay, а после скопируйте golden_key с помощью расширения Cookie-Editor"
                f"\n  (ЛКМ на расширение → Export → Header String)"
                f"\n\n  {Fore.LIGHTWHITE_EX}· Пример: {Fore.WHITE}blkrlwv7epmhx21bzqwp3x17bf2yhgre"
            )
            golden_key = input(f"  {Fore.WHITE}→ {Fore.LIGHTWHITE_EX}").strip()
            
            if is_golden_key_valid(golden_key):
                config["funpay"]["api"]["golden_key"] = golden_key
                sett.set("config", config)
                print(f"\n{Fore.GREEN}Golden Key успешно сохранён в конфиг.")
                break
            else:
                print(
                    f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный Golden Key. "
                    f"Убедитесь, что он соответствует формату и попробуйте ещё раз."
                )

        while not config["funpay"]["api"]["user_agent"]:
            print(
                f"\n{Fore.LIGHTYELLOW_EX}┌────┤ Введите {Fore.LIGHTMAGENTA_EX}Юзер-агент {Fore.LIGHTYELLOW_EX}├──────────────────────┐{Fore.WHITE}"
                f"\n\n  Его можно скопировать на сайте https://whatmyuseragent.com"
                f"\n  {Fore.LIGHTWHITE_EX}Или пропустите эту настройку, нажав Enter"
                f"\n\n  {Fore.LIGHTWHITE_EX}· Пример: {Fore.WHITE}Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
            )
            user_agent = input(f"  {Fore.WHITE}→ {Fore.LIGHTWHITE_EX}").strip()
            
            if not user_agent:
                print(f"\n{Fore.WHITE}Вы пропустили ввод Юзер-агента.")
                break
            if is_user_agent_valid(user_agent):
                config["funpay"]["api"]["user_agent"] = user_agent
                sett.set("config", config)
                print(f"\n{Fore.GREEN}Юзер-агент успешно сохранён в конфиг.")
            else:
                print(
                    f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный Юзер-агент. "
                    f"Убедитесь, что в нём нет русских символов и попробуйте ещё раз."
                )
        
        while not config["funpay"]["api"]["proxy"]:
            print(
                f"\n{Fore.LIGHTYELLOW_EX}┌────┤ Введите {Fore.LIGHTBLUE_EX}HTTP прокси {Fore.LIGHTYELLOW_EX}для FunPay ├──────────────────────┐{Fore.WHITE}"
                f"\n\n  Формат: user:password@ip:port, ip:port:user:password или ip:port"
                f"\n  {Fore.LIGHTWHITE_EX}Или пропустите эту настройку, нажав Enter"
                f"\n\n  {Fore.LIGHTWHITE_EX}· Пример: {Fore.WHITE}DRjcQTm3Yc:m8GnUN8Q9L@46.161.30.187:8000"
            )
            proxy = input(f"  {Fore.WHITE}→ {Fore.LIGHTWHITE_EX}").strip()

            if proxy.count(":") == 3:
                ip, port, user, passwd = proxy.split(":")
                proxy = f"{user}:{passwd}@{ip}:{port}"
                
            if not proxy:
                print(f"\n{Fore.WHITE}Вы пропустили ввод прокси.")
                break
            if is_proxy_valid(proxy):
                config["funpay"]["api"]["proxy"] = proxy
                sett.set("config", config)
                print(f"\n{Fore.GREEN}Прокси успешно сохранён в конфиг.")
            else:
                print(
                    f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный прокси. "
                    f"Убедитесь, что он соответствует формату и попробуйте ещё раз."
                )

    while not config["telegram"]["api"]["token"]:
        while not config["telegram"]["api"]["token"]:
            print(
                f"\n{Fore.LIGHTYELLOW_EX}┌────┤ Введите {Fore.CYAN}Токен Telegram бота {Fore.LIGHTYELLOW_EX}├──────────────────────┐{Fore.WHITE}"
                f"\n\n  {Fore.WHITE}Бота нужно создать у @BotFather (https://t.me/BotFather)"
                f"\n\n  {Fore.LIGHTWHITE_EX}· Пример: {Fore.WHITE}7257913369:AAG2KjLL3-zvvfSQFSVhaTb4w7tR2iXsJXM"
            )
            token = input(f"  {Fore.WHITE}→ {Fore.LIGHTWHITE_EX}").strip()
            
            if is_token_valid(token):
                config["telegram"]["api"]["token"] = token
                sett.set("config", config)
                print(f"\n{Fore.GREEN}Токен Telegram бота успешно сохранён в конфиг.")
            else:
                print(
                    f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный токен. "
                    f"Убедитесь, что он соответствует формату и попробуйте ещё раз."
                )

        while not config["telegram"]["api"]["proxy"]:
            print(
                f"\n{Fore.LIGHTYELLOW_EX}┌────┤ Введите {Fore.LIGHTBLUE_EX}HTTP прокси {Fore.LIGHTYELLOW_EX}для Telegram ├──────────────────────┐{Fore.WHITE}"
                f"\n\n  Формат: user:password@ip:port, ip:port:user:password или ip:port"
                f"\n  {Fore.LIGHTWHITE_EX}Или пропустите эту настройку, нажав Enter"
                f"\n\n  {Fore.LIGHTWHITE_EX}· Пример: {Fore.WHITE}DRjcQTm3Yc:m8GnUN8Q9L@46.161.30.187:8000"
            )
            proxy = input(f"  {Fore.WHITE}→ {Fore.LIGHTWHITE_EX}").strip()

            if proxy.count(":") == 3:
                ip, port, user, passwd = proxy.split(":")
                proxy = f"{user}:{passwd}@{ip}:{port}"

            if not proxy:
                print(f"\n{Fore.WHITE}Вы пропустили ввод прокси.")
                break
            if is_proxy_valid(proxy):
                config["telegram"]["api"]["proxy"] = proxy
                sett.set("config", config)
                print(f"\n{Fore.GREEN}Прокси успешно сохранён в конфиг.")
            else:
                print(
                    f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный прокси. "
                    f"Убедитесь, что он соответствует формату и попробуйте ещё раз."
                )

    while not config["telegram"]["bot"]["password"]:
        print(
            f"\n{Fore.LIGHTYELLOW_EX}┌────┤ Придумайте {Fore.YELLOW}Пароль для Telegram бота {Fore.LIGHTYELLOW_EX}├──────────────────────┐{Fore.WHITE}"
            f"\n\n  Бот будет запрашивать его при каждой новой попытке взаимодействия чужого пользователя"
            f"\n\n  {Fore.LIGHTWHITE_EX}· Важно: {Fore.WHITE}Пароль должен быть сложным, длиной не менее 6 и не более 64 символов"
        )
        password = input(f"  {Fore.WHITE}→ {Fore.LIGHTWHITE_EX}").strip()

        if is_password_valid(password):
            config["telegram"]["bot"]["password"] = password
            sett.set("config", config)
            print(f"\n{Fore.GREEN}Пароль успешно сохранён в конфиг.")
        else:
            print(
                f"\n{Fore.LIGHTRED_EX}Ваш пароль не подходит. "
                f"Убедитесь, что он соответствует формату и не является лёгким и попробуйте ещё раз."
            )

    logger.info("")

    if config["funpay"]["api"]["proxy"] and not is_proxy_working(config["funpay"]["api"]["proxy"]):
        print(
            f"{Fore.LIGHTRED_EX}\nПохоже, что прокси для FunPay аккаунта не работает. "
            f"Пожалуйста, проверьте его и введите снова."
        )
        config["funpay"]["api"]["golden_key"] = ""
        config["funpay"]["api"]["user_agent"] = ""
        config["funpay"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    elif config["funpay"]["api"]["proxy"]:
        logger.info(f"{Fore.LIGHTYELLOW_EX}FunPay прокси успешно работает.")

    if not is_fp_account_working():
        print(
            f"{Fore.LIGHTRED_EX}\nНе удалось подключиться к вашему FunPay аккаунту. "
            f"Пожалуйста, убедитесь, что у вас указан верный Golden Key и введите его снова."
        )
        config["funpay"]["api"]["golden_key"] = ""
        config["funpay"]["api"]["user_agent"] = ""
        config["funpay"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    else:
        logger.info(f"{Fore.LIGHTYELLOW_EX}FunPay аккаунт успешно авторизован.")

    if is_fp_account_banned():
        print(
            f"{Fore.LIGHTRED_EX}\nВаш FunPay аккаунт забанен! "
            f"Увы, я не могу запустить бота на заблокированном аккаунте..."
        )
        config["funpay"]["api"]["golden_key"] = ""
        config["funpay"]["api"]["user_agent"] = ""
        config["funpay"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()

    if config["telegram"]["api"]["proxy"] and not is_proxy_working(
        config["telegram"]["api"]["proxy"], 
        "https://api.telegram.org/"
    ):
        print(
            f"{Fore.LIGHTRED_EX}\nПохоже, что прокси для Telegram бота не работает. "
            f"Пожалуйста, проверьте его и введите снова."
        )
        config["telegram"]["api"]["token"] = ""
        config["telegram"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    elif config["telegram"]["api"]["proxy"]:
        logger.info(f"{Fore.LIGHTYELLOW_EX}Telegram прокси успешно работает.")

    if not is_tg_bot_exists():
        print(
            f"{Fore.LIGHTRED_EX}\nНе удалось подключиться к вашему Telegram боту. "
            f"Если вы находитесь на территории России, вам нужно подключить прокси к Telegram боту или использовать VPN, в виду блокировок со стороны РКН."
        )
        config["telegram"]["api"]["token"] = ""
        config["telegram"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    else:
        logger.info(f"{Fore.LIGHTYELLOW_EX}Telegram бот успешно работает.")


def get_stats():
    cached_orders = data.get("cached_orders")

    now = datetime.now(pytz.timezone("Europe/Moscow"))
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    day_orders = [o for o in cached_orders.values() if datetime.fromisoformat(o["date"]) >= day_ago]
    week_orders = [o for o in cached_orders.values() if datetime.fromisoformat(o["date"]) >= week_ago]
    month_orders = [o for o in cached_orders.values() if datetime.fromisoformat(o["date"]) >= month_ago]
    all_orders = list(cached_orders.values())

    day_active = [o for o in day_orders if not o["status"] == "CLOSED" and not o["status"] == "REFUNDED"]
    week_active = [o for o in week_orders if not o["status"] == "CLOSED" and not o["status"] == "REFUNDED"]
    month_active = [o for o in month_orders if not o["status"] == "CLOSED" and not o["status"] == "REFUNDED"]
    all_active = [o for o in all_orders if not o["status"] == "CLOSED" and not o["status"] == "REFUNDED"]

    day_completed = [o for o in day_orders if o["status"] == "CLOSED"]
    week_completed = [o for o in week_orders if o["status"] == "CLOSED"]
    month_completed = [o for o in month_orders if o["status"] == "CLOSED"]
    all_completed = [o for o in all_orders if o["status"] == "CLOSED"]

    day_refunded = [o for o in day_orders if o["status"] == "REFUNDED"]
    week_refunded = [o for o in week_orders if o["status"] == "REFUNDED"]
    month_refunded = [o for o in month_orders if o["status"] == "REFUNDED"]
    all_refunded = [o for o in all_orders if o["status"] == "REFUNDED"]

    day_profit = round(sum(o["price"] for o in day_orders if o["status"] == "CLOSED"), 2)
    week_profit = round(sum(o["price"] for o in week_orders if o["status"] == "CLOSED"), 2)
    month_profit = round(sum(o["price"] for o in month_orders if o["status"] == "CLOSED"), 2)
    all_profit = round(sum(o["price"] for o in all_orders if o["status"] == "CLOSED"), 2)

    day_best = Counter(o["description"] for o in day_orders).most_common(1)[0][0] if day_orders else "-"
    week_best = Counter(o["description"] for o in week_orders).most_common(1)[0][0] if day_orders else "-"
    month_best = Counter(o["description"] for o in month_orders).most_common(1)[0][0] if day_orders else "-"
    all_best = Counter(o["description"] for o in all_orders).most_common(1)[0][0] if day_orders else "-"

    return {
        "day": {
            "orders": len(day_orders),
            "active": len(day_active),
            "completed": len(day_completed),
            "refunded": len(day_refunded),
            "profit": day_profit,
            "best": day_best
        },
        "week": {
            "orders": len(week_orders),
            "active": len(week_active),
            "completed": len(week_completed),
            "refunded": len(week_refunded),
            "profit": week_profit,
            "best": week_best
        },
        "month": {
            "orders": len(month_orders),
            "active": len(month_active),
            "completed": len(month_completed),
            "refunded": len(month_refunded),
            "profit": month_profit,
            "best": month_best
        },
        "all": {
            "orders": len(all_orders),
            "active": len(all_active),
            "completed": len(all_completed),
            "refunded": len(all_refunded),
            "profit": all_profit,
            "best": all_best
        }
    }