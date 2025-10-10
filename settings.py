import os
import json
import copy

DATA = {
    "config": {
        "path": "bot_settings/config.json",
        "default": {
            "funpay": {
                "api": {
                    "golden_key": "",
                    "user_agent": "",
                    "proxy": "",
                    "requests_timeout": 30,
                    "runner_requests_delay": 4
                },
                "bot": {
                    "messages_watermark_enabled": True,
                    "messages_watermark": "©️ 𝗙𝘂𝗻𝗣𝗮𝘆 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
                    "custom_commands_enabled": True,
                    "auto_deliveries_enabled": True,
                    "auto_raising_lots_enabled": True,
                    "auto_reviews_replies_enabled": True,
                    "auto_support_tickets_enabled": True,
                    "auto_support_tickets_orders_per_ticket": 25,
                    "auto_support_tickets_create_interval": 86400,
                    "tg_logging_enabled": True,
                    "tg_logging_chat_id": "",
                    "tg_logging_events": {
                        "new_user_message": True,
                        "new_system_message": True,
                        "new_order": True,
                        "order_status_changed": True,
                        "new_review": True
                    }
                }
            },
            "telegram": {
                "api": {
                    "token": ""
                },
                "bot": {
                    "password": "",
                    "signed_users": []
                }
            }
        },
        "params": {
            "funpay": {
                "api": {
                    "golden_key": {
                        "required": True,
                        "type": str,
                        "desc": [
                            "golden_key вашего аккаунта FunPay, который необходим для того, чтобы бот подключился и работал с вашим аккаунтом.",
                            "Его можно скопировать из cookie сайта funpay.com. Можете воспользоваться расширением Cookie-Editor."
                        ]
                    },
                    "user_agent": {
                        "required": False,
                        "type": str,
                        "desc": [
                            "Юзер агент вашего браузера. Желательно указать, чтобы бот лучше работал с вашим аккаунтом и возникало меньше проблем с подключением.",
                            "Узнать его просто: Переходите на сайт https://www.whatismybrowser.com/detect/what-is-my-user-agent/ и копируете весь текст в синем окошке."
                        ]
                    },
                    "proxy": {
                        "required": False,
                        "type": str,
                        "desc": [
                            "IPv4 прокси. Если желаете, можете указать его, тогда запросы будут отправляться с него.",
                            "Формат: user:pass@ip:port или ip:port"
                        ]
                    }
                }
            },
            "telegram": {
                "api": {
                    "token": {
                        "required": True,
                        "type": str,
                        "desc": [
                            "Токен Telegram бота. В TG боте можно будет настроить остальную часть функционала бота.",
                            "Чтобы получить токен, нужно создать бота у @BotFather. Пишите /newbot и начинаете настройку."
                        ]
                    }
                },
                "bot": {
                    "password": {
                        "required": True,
                        "type": str,
                        "desc": [
                            "Пароль от вашего Telegram бота. Будет запрашиваться для использования бота."
                        ]
                    }
                }
            }
        }
    },
    "messages": {
        "path": "bot_settings/messages.json",
        "default": {
            "first_message": {
                "enabled": True,
                "text": [
                    "👋 Привет, {username}, я бот-помощник 𝗙𝘂𝗻𝗣𝗮𝘆 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗮𝗹",
                    "",
                    "💡 Если вы хотите поговорить с продавцом, напишите команду !продавец, чтобы я пригласил его в этот диалог",
                    "",
                    "Чтобы узнать все мои команды, напишите !команды"
                ]
            },
            "cmd_error": {
                "enabled": True,
                "text": [
                    "❌ При вводе команды произошла ошибка: {error}"
                ]
            },
            "cmd_commands": {
                "enabled": True,
                "text": [
                    "🕹️ Основные команды:",
                    "・ !продавец — уведомить и позвать продавца в этот чат"
                ]
            },
            "cmd_seller": {
                "enabled": True,
                "text": [
                    "💬 Продавец был вызван в этот чат. Ожидайте, пока он подключиться к диалогу..."
                ]
            },
            "new_order": {
                "enabled": False,
                "text": [
                    "📋 Спасибо за покупку «{order_title}» в количестве {order_amount} шт.",
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
                    "🛍️ Товар: {order_title}",
                    "",
                    "🔢 Количество: {order_amount} шт."
                ]
            }
        }
    },
    "custom_commands": {
        "path": "bot_settings/custom_commands.json",
        "default": {}
    },
    "auto_deliveries": {
        "path": "bot_settings/auto_deliveries.json",
        "default": {}
    }
}


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
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(new, f, indent=4, ensure_ascii=False)

class Settings:
    
    @staticmethod
    def get(name, data: dict | None = None) -> dict:
        data = data if data is not None else DATA
        if name not in data:
            return None
        return get_json(data[name]["path"], data[name]["default"])

    @staticmethod
    def set(name, new, data: dict | None = None) -> dict:
        data = data if data is not None else DATA
        if name not in data:
            return None
        set_json(data[name]["path"], new)