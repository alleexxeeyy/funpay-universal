import os
import json
import uuid
from colorama import Fore, Style
from .meta import NAME


class Config():
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        self.config_path = os.path.join(current_dir, 'module_settings', 'config.json')
    
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
            "some_bool_value": True,
            "some_first_int_value": 0,
            "some_second_int_value": 321
        }
    
    def configure_config(self):
        """ Начинает настройку конфига """
        params = {
            "some_first_int_value": {
                "required": True,
                "type": int,
                "desc": [
                    "Первое числовое значение."
                ]
            },
            "some_second_int_value": {
                "required": False,
                "type": int,
                "desc": [
                    "Второе числовое значение."
                ]
            }
        }

        config = self.get()
        answers = {}
        print(f"\n{Fore.LIGHTWHITE_EX}↓ Всего {Fore.LIGHTCYAN_EX}{len(params.keys())} {Fore.LIGHTWHITE_EX}параметра(-ов), ничего сложного ( ͡° ͜ʖ ͡°)")
        i=0
        for param in params.keys():
            if param in config:
                i+=1
                default_value = config[param] if config[param] else "Не задано"
                desc = "· " + "\n· ".join(params[param]["desc"])
                print(f"\n{Fore.LIGHTWHITE_EX}⚙️ {i}. Введите значение параметра {Fore.LIGHTCYAN_EX}{param}."
                      f"\n{Fore.WHITE}Значение по умолчанию: {Fore.LIGHTCYAN_EX}{default_value}"
                      f"\n{Fore.WHITE}Описание параметра: \n{Fore.LIGHTCYAN_EX}{desc}"
                      f'\n{Fore.WHITE}Ввод {"обязательный" if params[param]["required"] == True else "необязательный"}')
                if not params[param]["required"]:
                    print(f"{Fore.LIGHTWHITE_EX}Нажмите Enter, чтобы пропустить и использовать значение по умолчанию: {Fore.LIGHTCYAN_EX}{default_value}")
                a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")
                
                if params[param]["type"] is int:
                    try:
                        if int(a) > 0:
                            print(f"{Fore.WHITE}Значение параметра {Fore.LIGHTWHITE_EX}{param} {Fore.WHITE}было изменено на {Fore.LIGHTCYAN_EX}{a}")
                            answers[param] = int(a)
                            continue
                        elif int(a) <= 0:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: слишком низкое значение")
                            break
                    except:
                        if not a and not params[param]["required"]:
                            answers[param] = default_value
                            print(f"Будет использоваться значение по умолчанию: {Fore.LIGHTCYAN_EX}{default_value}")
                        elif not a and params[param]["required"]:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: это значение обязательное")
                            break
                        else:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: значение должно быть числовым")
                            break
                elif params[param]["type"] is str:
                    try:
                        if len(a) > 0:
                            print(f"{Fore.WHITE}Значение параметра {Fore.LIGHTWHITE_EX}{param} {Fore.WHITE}было изменено на {Fore.LIGHTCYAN_EX}{a}")
                            answers[param] = str(a)
                            continue
                        elif not a and params[param]["required"]:
                            print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: это значение обязательное")
                            break
                        elif not a and not params[param]["required"]:
                            answers[param] = default_value
                            print(f"{Fore.WHITE}Будет использоваться значение по умолчанию: {Fore.LIGHTCYAN_EX}{default_value}")
                    except:
                        print(f"{Fore.LIGHTRED_EX}✗ Ошибка ввода: значение должно быть строчным")
                        break
        else:
            print(f"\n{Fore.LIGHTWHITE_EX}✓ Отлично, настройка была завершена.")
            print(f"{Fore.WHITE}Ваши ответы:")
            print(f"{Fore.WHITE}Параметр: {Fore.LIGHTCYAN_EX}*ваш ответ*{Fore.WHITE} | {Fore.LIGHTCYAN_EX}*значение по умолчанию*")
            print(f"{Fore.LIGHTWHITE_EX}——————")
            for answer_param in answers.keys():
                default_value = config[answer_param] if config[answer_param] else "Не задано"
                print(f"{Fore.WHITE}{answer_param}: {Fore.LIGHTCYAN_EX}{answers[answer_param]}{Fore.WHITE} | {Fore.LIGHTCYAN_EX}{default_value}")
            print(f"\n{Fore.WHITE}💾 Применяем и сохраняем конфиг с текущими, указанными вами значениями? +/-")
            a = input(f"{Fore.WHITE}> ")

            if a == "+":
                for answer_param in answers.keys():
                    config[answer_param] = answers[answer_param]
                    Config().update(config)
                print(f"{Fore.LIGHTYELLOW_EX}✅ Настройки были применены и сохранены в конфиг модуля {NAME}\n")
                return True
            else:
                print(f"\n{Fore.WHITE}Вы отказались от сохранения введённых вами значений в конфиг. Давайте настроим их с начала...")
                return self.configure_config()
        print(f"{Fore.WHITE}К сожалению, вы ввели неверное значение для одного из параметров, и поэтому настройка начнётся с самого начала")
        return self.configure_config()