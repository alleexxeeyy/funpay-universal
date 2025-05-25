import os
import requests
import zipfile
import io
import shutil
import sys
from colorama import Fore
from bot_settings.app import CURRENT_VERSION


class Updater:
    """ Класс-обновлятор бота. """

    REPO = "alleexxeeyy/funpay-universal"
    API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"

    @staticmethod
    def check_for_updates():
        """ Проверяет бота на наличие обновлений на GitHub. """
        try:
            response = requests.get(Updater.API_URL)
            if response.status_code != 200:
                raise Exception(f"Ошибка запроса к GitHub API: {response.status_code}")
            
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            if latest_version == CURRENT_VERSION:
                print(f"{Fore.WHITE}У вас установлена последняя версия: {Fore.LIGHTWHITE_EX}{CURRENT_VERSION}")
                return False
            print(f"\n{Fore.LIGHTYELLOW_EX}Доступна новая версия: {Fore.LIGHTWHITE_EX}{latest_version}"
                    f"\n{Fore.WHITE}Скачиваем: {Fore.LIGHTWHITE_EX}{latest_release['html_url']}\n")
            return Updater.download_and_install(latest_release)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX} При проверке на наличие обновлений произошла ошибка: {Fore.WHITE}{e}")
        return False

    @staticmethod
    def download_and_install(release_info):
        """
        Скачивает и распаковывает обновление.

        :param release_info: GitHub API response.
        :type release_info: dict
        """
        try:
            zip_url = release_info['zipball_url']
            print(f"{Fore.WHITE}Скачиваем архив обновления...")
            zip_response = requests.get(zip_url)
            if zip_response.status_code != 200:
                raise Exception(f"{Fore.LIGHTRED_EX}При скачивании архива обновления произошла ошибка: {zip_response.status_code}")

            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as zip_file:
                temp_dir = ".temp_update"
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)

                zip_file.extractall(temp_dir)
                extracted_root = next(os.scandir(temp_dir)).path\
                
                print(f"{Fore.WHITE}Устанавливаем архив обновления...")
                for item in os.listdir(extracted_root):
                    src_path = os.path.join(extracted_root, item)
                    dst_path = os.path.join('.', item)
                    if os.path.exists(dst_path):
                        if os.path.isdir(dst_path):
                            shutil.rmtree(dst_path)
                        else:
                            os.remove(dst_path)
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)

                print(f"{Fore.LIGHTYELLOW_EX}✅ Обновление установлено")
                shutil.rmtree(temp_dir)
                print(f"{Fore.WHITE}Перезапуск бота...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
                return True
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX} При установке и распаковке обновления произошла ошибка: {Fore.WHITE}{e}")
        return False
