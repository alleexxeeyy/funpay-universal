import os
import json
import copy
import tempfile
from dataclasses import dataclass


@dataclass
class SettingsFile:
    name: str
    path: str
    need_restore: bool
    default: list | dict


CONFIG = SettingsFile(
    name="config",
    path="bot_settings/config.json",
    need_restore=True,
    default={
        "funpay": {
            "api": {
                "golden_key": "",
                "user_agent": "",
                "proxy": "",
                "requests_timeout": 30,
                "runner_requests_delay": 4
            },
            "watermark": {
                "enabled": True,
                "value": "©️ 𝗙𝘂𝗻𝗣𝗮𝘆 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
            },
            "auto_raise_lots": True,
            "auto_review_replies": True,
            "auto_tickets": {
                "enabled": True,
                "orders_per_ticket": 25,
                "min_order_age": 86400,
                "interval": 86400,
                "last_time": ""
            },
            "auto_withdrawal": {
                "enabled": False,
                "interval": 86400,
                "last_time": "",
                "currency": "rub",
                "wallet_type": "CARD_RUB",
                "address": "",
                "amount_type": "all",
                "amount": 0.0
            },
            "notifications": {
                "enabled": True,
                "chat_id": "",
                "events": {
                    "new_user_message": True,
                    "new_system_message": True,
                    "new_order": True,
                    "order_status_changed": True,
                    "new_review": True,
                    "ticket_created": True,
                    "withdrawal_requested": True
                }
            }
        },
        "telegram": {
            "api": {
                "token": "",
                "proxy": ""
            },
            "bot": {
                "password": "",
                "signed_users": []
            }
        },
        "updates": {
            "auto_update": True,
            "notify": True
        },
        "logs": {
            "max_file_size": 300
        }
    }
)
MESSAGES = SettingsFile(
    name="messages",
    path="bot_settings/messages.json",
    need_restore=True,
    default={
        "first_message": {
            "enabled": True,
            "text": [
                "👋 Привет, {user.username}, я бот-помощник 𝗙𝘂𝗻𝗣𝗮𝘆 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
                "",
                "💡 Если вы хотите поговорить с продавцом, напишите команду !продавец, чтобы я пригласил его в этот диалог"
            ]
        },
        "cmd_error": {
            "enabled": True,
            "text": [
                "❌ При вводе команды произошла ошибка: {error}"
            ]
        },
        "cmd_seller": {
            "enabled": True,
            "text": [
                "💬 Продавец был вызван в этот чат. Ожидайте, пока он подключится к диалогу..."
            ]
        },
        "new_order": {
            "enabled": False,
            "text": [
                "📋 Спасибо за покупку «{order.title}» в количестве {order.amount} шт.",
                ""
                "Продавца сейчас может не быть на месте, чтобы позвать его, используйте команду !продавец."
            ]
        },
        "order_confirmed": {
            "enabled": False,
            "text": [
                "🌟 Спасибо за успешную сделку. Буду рад, если оставите отзыв. Жду вас в своём магазине в следующий раз, удачи!"
            ]
        },
        "order_refunded": {
            "enabled": False,
            "text": [
                "📦 Заказ был возвращён. Надеюсь эта сделка не принесла вам неудобств. Жду вас в своём магазине в следующий раз, удачи!"
            ]
        },
        "order_review_reply": {
            "enabled": True,
            "text": [
                "📅 Дата отзыва: {review_date}",
                "",
                "🌟 Оценка: {review.stars}",
                "",
                "👤 Автор: {review.author}",
                "",
                "🛍️ Товар: {order.title}",
                "",
                "🔢 Количество: {order.amount} шт."
            ]
        }
    }
)
CUSTOM_COMMANDS = SettingsFile(
    name="custom_commands",
    path="bot_settings/custom_commands.json",
    need_restore=False,
    default={}
)
AUTO_DELIVERIES = SettingsFile(
    name="auto_deliveries",
    path="bot_settings/auto_deliveries.json",
    need_restore=False,
    default={}
)
FAST_REPLIES = SettingsFile(
    name="fast_replies",
    path="bot_settings/fast_replies.json",
    need_restore=False,
    default=[]
)
DATA = [CONFIG, MESSAGES, CUSTOM_COMMANDS, AUTO_DELIVERIES, FAST_REPLIES]


def validate_config(config, default):
    """
    Проверяет структуру конфига на соответствие стандартному шаблону.

    :param config: Текущий конфиг.
    :type config: `dict`

    :param default: Стандартный шаблон конфига.
    :type default: `dict`

    :return: True если структура валидна, иначе False.
    :rtype: bool
    """
    for key, value in default.items():
        if key not in config:
            return False
        if type(config[key]) is not type(value):
            return False
        if isinstance(value, dict) and isinstance(config[key], dict):
            if not validate_config(config[key], value):
                return False
    return True


def restore_config(config: dict, default: dict):
    """
    Восстанавливает недостающие параметры в конфиге из стандартного шаблона.
    И удаляет параметры из конфига, которых нету в стандартном шаблоне.

    :param config: Текущий конфиг.
    :type config: `dict`

    :param default: Стандартный шаблон конфига.
    :type default: `dict`

    :return: Восстановленный конфиг.
    :rtype: `dict`
    """
    config = copy.deepcopy(config)

    def check_default(config, default):
        for key, value in dict(default).items():
            if key not in config:
                config[key] = value
            elif type(value) is not type(config[key]):
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                check_default(config[key], value)
        return config

    config = check_default(config, default)
    return config
    

def get_json(path: str, default: dict, need_restore: bool = True) -> dict:
    """
    Получает данные файла настроек.
    Создаёт файл настроек, если его нет.
    Добавляет новые данные, если такие есть.

    :param path: Путь к json файлу.
    :type path: `str`

    :param default: Стандартный шаблон файла.
    :type default: `dict`

    :param need_restore: Нужно ли сделать проверку на целостность конфига.
    :type need_restore: `bool`
    """
    folder_path = os.path.dirname(path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if need_restore:
            new_config = restore_config(config, default)
            if config != new_config:
                config = new_config
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
    except:
        config = default
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    finally:
        return config
    

def set_json(path: str, new: dict):
    """
    Устанавливает новые данные в файл настроек.

    :param path: Путь к json файлу.
    :type path: `str`

    :param new: Новые данные.
    :type new: `dict`
    """
    dir_name = os.path.dirname(path)
    
    with tempfile.NamedTemporaryFile( # атомарная запись файла
        "w",
        encoding="utf-8",
        dir=dir_name,
        delete=False
    ) as tmp:
        json.dump(new, tmp, ensure_ascii=False, indent=4)
        tmp.flush()
        os.fsync(tmp.fileno())

    os.replace(tmp.name, path)


class Settings:
    
    @staticmethod
    def get(name: str, data: list[SettingsFile] = DATA) -> dict | None:
        try: 
            file = [file for file in data if file.name == name][0]
            return get_json(file.path, file.default, file.need_restore)
        except: return None

    @staticmethod
    def set(name: str, new: list | dict, data: list[SettingsFile] = DATA):
        try: 
            file = [file for file in data if file.name == name][0]
            set_json(file.path, new)
        except: pass