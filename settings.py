import json
from colorama import Fore, Style


class Config:
    def __init__(self):
        self.config_path = 'bot_settings/config.json'
    
    def get(self) -> dict:
        """ Возвращает конфиг в JSON формате """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(Config.default_config(), f, indent=4, ensure_ascii=False)
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        finally:
            return config
    
    def update(self, new_data) -> None:
        """
        Перезаписывает данные в конфиг

        :param new_data: Новый экземпляр конфига
        """
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)

    def default_config() -> dict:
        """ Возвращает стандартную структуру конфига """
        return {
            "golden_key": "",
            "user_agent": "",
            "tg_admin_id": 0,
            "tg_bot_token": "",
            "funpayapi_timeout": 30,
            "runner_requests_delay": 4,
            "first_message_enabled": True,
            "custom_commands_enabled": True,
            "auto_deliveries_enabled": True,
            "auto_raising_lots_enabled": True,
            "lots_saving_interval": 3600,
            "auto_reviews_replies_enabled": True,
        }
    
    def configure_config(self):
        """ Начинает настройку конфига """

        # Словарь, содержащий описание каждого параметра в конфиге
        params = {
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
            "funpayapi_timeout": {
                "required": False,
                "type": int,
                "desc": [
                    "Максимальное время таймаут на подключение к funpay.com. Если у вас плохой интернет - указывайте значение больше. Указывается в секундах."
                ]
            },
            "runner_requests_delay": {
                "required": False,
                "type": int,
                "desc": [
                    "Периодичность отправления запросов на funpay.com для получения ивентов. Не рекомендуем ставить ниже 4, ",
                    "в виду повышенного риска блокировки вашего IP адреса со стороны FunPay. Указывается в секундах."
                ]
            },
            "tg_admin_id": {
                "required": True,
                "type": int,
                "desc": [
                    "ID вашего Telegram аккаунта. Можно узнать у бота @myidbot. Только пользователь с этим ID сможет взаимодействовать с ботом."
                ]
            },
            "tg_bot_token": {
                "required": True,
                "type": str,
                "desc": [
                    "Токен Telegram бота. В TG боте можно будет настроить остальную часть функционала бота.",
                    "Чтобы получить токен, нужно создать бота у @BotFather. Пишите /newbot и начинаете настройку."
                ]
            }
        }

        config = self.get()
        answers = {}
        print(f"\n{Fore.LIGHTWHITE_EX}↓ Всего {Fore.LIGHTYELLOW_EX}{len(params.keys())} {Fore.LIGHTWHITE_EX}параметра(-ов), ничего сложного ( ͡° ͜ʖ ͡°)")
        i=0
        for param in params.keys():
            if param in config:
                i+=1
                required = f"обязательный" if params[param]["required"] == True else f"необязательный"
                default_value = config[param] if config[param] else "Не задано"
                desc = "· " + "\n· ".join(params[param]["desc"])
                print(f"\n{Fore.LIGHTWHITE_EX}⚙️ {i}. Введите значение параметра {Fore.LIGHTYELLOW_EX}{param}."
                      f"\n{Fore.WHITE}Значение по умолчанию: {Fore.LIGHTYELLOW_EX}{default_value}"
                      f"\n{Fore.WHITE}Описание параметра: \n{Fore.LIGHTYELLOW_EX}{desc}"
                      f"\n{Fore.WHITE}Ввод {required}")
                if not params[param]["required"]:
                    print(f"{Fore.LIGHTWHITE_EX}Нажмите Enter, чтобы пропустить и использовать значение по умолчанию: {Fore.LIGHTYELLOW_EX}{default_value}")
                a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")
                
                if params[param]["type"] is int:
                    try:
                        if int(a) > 0:
                            print(f"{Fore.WHITE}Значение параметра {Fore.LIGHTWHITE_EX}{param} {Fore.WHITE}было изменено на {Fore.LIGHTYELLOW_EX}{a}")
                            answers[param] = int(a)
                            continue
                        elif int(a) <= 0:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: слишком низкое значение")
                            break
                    except:
                        if not a and not params[param]["required"]:
                            answers[param] = default_value
                            print(f"Будет использоваться значение по умолчанию: {Fore.LIGHTYELLOW_EX}{default_value}")
                        elif not a and params[param]["required"]:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: это значение обязательное")
                            break
                        else:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: значение должно быть числовым")
                            break
                elif params[param]["type"] is str:
                    try:
                        if len(a) > 0:
                            print(f"{Fore.WHITE}Значение параметра {Fore.LIGHTWHITE_EX}{param} {Fore.WHITE}было изменено на {Fore.LIGHTYELLOW_EX}{a}")
                            answers[param] = str(a)
                            continue
                        elif not a and params[param]["required"]:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: это значение обязательное")
                            break
                        elif not a and not params[param]["required"]:
                            answers[param] = default_value
                            print(f"{Fore.WHITE}Будет использоваться значение по умолчанию: {Fore.LIGHTYELLOW_EX}{default_value}")
                    except:
                        print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: значение должно быть строчным")
                        break
        else:
            print(f"\n{Fore.LIGHTWHITE_EX}✓ Отлично, настройка была завершена.")
            print(f"{Fore.WHITE}Ваши ответы:")
            print(f"{Fore.WHITE}Параметр: {Fore.LIGHTYELLOW_EX}*ваш ответ*{Fore.WHITE} | {Fore.LIGHTYELLOW_EX}*значение по умолчанию*")
            print(f"{Fore.LIGHTWHITE_EX}——————")
            for answer_param in answers.keys():
                default_value = config[answer_param] if config[answer_param] else "Не задано"
                print(f"{Fore.WHITE}{answer_param}: {Fore.LIGHTYELLOW_EX}{answers[answer_param]}{Fore.WHITE} | {Fore.LIGHTYELLOW_EX}{default_value}")
            print(f"\n{Fore.WHITE}💾 Применяем и сохраняем конфиг с текущими, указанными вами значениями? +/-")
            a = input(f"{Fore.WHITE}> ")

            if a == "+":
                for answer_param in answers.keys():
                    config[answer_param] = answers[answer_param]
                    Config().update(config)
                print(f"{Fore.LIGHTWHITE_EX}✅ Настройки были применены и сохранены в конфиг\n")
                return True
            else:
                print(f"\n{Fore.WHITE}Вы отказались от сохранения введённых вами значений в конфиг. Давайте настроим их с начала...")
                return self.configure_config()
        print(f"{Fore.WHITE}К сожалению, вы ввели неверное значение для одного из параметров, и поэтому настройка начнётся с самого начала")
        return self.configure_config()
    
class Messages:
    def __init__(self):
        self.messages_path = 'bot_settings/messages.json'

    def default_messages(self) -> dict:
        """ Возвращает стандартную структуру сообщений """
        return {
            "new_order": [
                "👋 Привет, я бот-помощник.",
                "",
                "· 👀 Вижу, вы только что оплатили заказ #{order_id}.",
                "",
                "· 🗨️ Сейчас продавец возможно не в сети, поэтому чтобы позвать его, напишите команду !продавец и я приглашу его в этот диалог.",
                "",
                "· 🕹️ А вообще, чтобы узнать все мои команды, напишите !команды"
            ],
            "user_not_initialized": [
                "👋 Привет {buyer_username}, я бот-помощник.",
                "",
                "· 🗨️ Если вы хотите поговорить с продавцом, напишите команду !продавец, чтобы я пригласил его в этот диалог.",
                "",
                "· 🕹️ А вообще, чтобы узнать все мои команды, напишите !команды"
            ],
            "command_error": [
                "✗ При вводе команды произошла непредвиденная ошибка"
            ],
            "command_incorrect_use_error": [
                "✗ Неверное использование команды. Используйте {correct_use}"
            ],
            "buyer_command_commands": [
                "🕹️ Основные команды:",
                "→ !продавец — уведомить и позвать продавца в этот чат"
            ],
            "buyer_command_seller": [
                "💬 Продавец был вызван в этот чат. Ожидайте, пока он подключиться к диалогу..."
            ],
            "order_confirmed": [
                "🌟 Спасибо за успешную сделку. Буду рад, если оставите отзыв. Жду вас в своём магазине в следующий раз, удачи!"
            ],
            "order_review_reply_text": [
                "📅 Дата отзыва: {review_date}",
                "",
                "🛍️ Товар: {order_title}",
                "",
                "🔢 Количество: {order_amount} шт."
            ]
        }
    
    def get(self) -> dict:
        """ Возвращает сообщения в JSON формате """
        try:
            with open(self.messages_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except:
            with open(self.messages_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_messages(), f, indent=4, ensure_ascii=False)
            with open(self.messages_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        finally:
            return messages
        
    def update(self, new_data) -> None:
        """
        Перезаписывает данные в сообщения

        :param new_data: Новый экземпляр сообщений
        """
        with open(self.messages_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)

class CustomCommands:
    def __init__(self):
        self.custom_commands_path = 'bot_settings/custom_commands.json'

    def default_custom_commands(self) -> dict:
        """ Возвращает стандартную структуру пользовательских команд """
        return {
            "!тест": [
                "Привет, друг 👋. Это тестовое сообщение, которое можно изменить в настройках пользовательских команд.",
                "©️ 𝐅𝐮𝐧𝐏𝐚𝐲 𝐔𝐧𝐢𝐯𝐞𝐫𝐬𝐚𝐥",
            ]
        }
    
    def get(self) -> dict:
        """ Возвращает пользовательские команды в JSON формате """
        try:
            with open(self.custom_commands_path, 'r', encoding='utf-8') as f:
                custom_commands = json.load(f)
        except:
            with open(self.custom_commands_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_custom_commands(), f, indent=4, ensure_ascii=False)
            with open(self.custom_commands_path, 'r', encoding='utf-8') as f:
                custom_commands = json.load(f)
        finally:
            return custom_commands
        
    def update(self, new_data) -> None:
        """
        Перезаписывает данные в пользовательские команды

        :param new_data: Новый экземпляр пользовательских команд
        """
        with open(self.custom_commands_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)

class AutoDeliveries:
    def __init__(self):
        self.auto_deliveries_path = 'bot_settings/auto_deliveries.json'

    def default_auto_deliveries(self) -> dict:
        """ Возвращает стандартную структуру авто-выдач """
        return {
            "1234567890": [
                "Вот ваш аккаунт:",
                "- Логин: login123",
                "- Пароль: password123",
                "©️ 𝐅𝐮𝐧𝐏𝐚𝐲 𝐔𝐧𝐢𝐯𝐞𝐫𝐬𝐚𝐥"
            ]
        }
    
    def get(self) -> dict:
        """ Возвращает авто-выдачи в JSON формате """
        try:
            with open(self.auto_deliveries_path, 'r', encoding='utf-8') as f:
                auto_deliveries = json.load(f)
        except:
            with open(self.auto_deliveries_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_auto_deliveries(), f, indent=4, ensure_ascii=False)
            with open(self.auto_deliveries_path, 'r', encoding='utf-8') as f:
                auto_deliveries = json.load(f)
        finally:
            return auto_deliveries
        
    def update(self, new_data) -> None:
        """
        Перезаписывает данные в авто-выдачи

        :param new_data: Новый экземпляр авто-выдач
        """
        with open(self.auto_deliveries_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)