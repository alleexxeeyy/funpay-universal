from bot_settings.app import CURRENT_VERSION
import requests
from colorama import Fore

class Updater:
    """ Класс-обновлятор бота """

    def check_for_updates():
        """ Проверяет бота на наличие обновлений на GithHub """
        try:
            response = requests.get(f"https://api.github.com/repos/alleexxeeyy/funpay-universal/releases/latest")
            if response.status_code == 200:
                latest_release = response.json()
                print(latest_release)
                latest_version = latest_release["tag_name"]
                if latest_version != CURRENT_VERSION:
                    print(f"\n{Fore.LIGHTYELLOW_EX}Доступна новая версия: {Fore.LIGHTWHITE_EX}{latest_version}"
                          f"{Fore.WHITE}Скачать: {Fore.LIGHTWHITE_EX}{latest_release['html_url']}\n")
                    return True
                else:
                    return False
            else:
                print(f"{Fore.LIGHTRED_EX}Ошибка запроса при проверке последнего релиза репозитория: {Fore.WHITE}{response.status_code}")
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Ошибка при проверке обновлений: {Fore.WHITE}{e}")
        return False