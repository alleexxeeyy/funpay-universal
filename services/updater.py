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
                print(f"{Fore.WHITE}У вас установлена последняя версия: {Fore.LIGHTWHITE_EX}{CURRENT_VERSION}\n")
                return False
            print(f"\n{Fore.LIGHTYELLOW_EX}Доступна новая версия: {Fore.LIGHTWHITE_EX}{latest_version}"
                    f"\n{Fore.WHITE}Скачиваем: {Fore.LIGHTWHITE_EX}{latest_release['html_url']}\n")
            bytes = Updater.download_update(latest_release)
            if bytes:
                if Updater.install_update(bytes):
                    print(f"{Fore.LIGHTYELLOW_EX}✅ Обновление {Fore.LIGHTWHITE_EX}{latest_version} {Fore.LIGHTYELLOW_EX}было успешно установлено.")
                    print(f"{Fore.WHITE}Перезапуск бота...")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX} При проверке на наличие обновлений произошла ошибка: {Fore.WHITE}{e}")
        return False

    @staticmethod
    def download_update(release_info: str):
        """ Скачивает архив с обновлением """
        try:
            zip_url = release_info['zipball_url']
            zip_response = requests.get(zip_url)
            if zip_response.status_code != 200:
                raise Exception(f"{Fore.LIGHTRED_EX}При скачивании архива обновления произошла ошибка: {zip_response.status_code}")
            return zip_response.content
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}При скачивании обновления произошла ошибка: {Fore.WHITE}{e}")
            return False
    
    @staticmethod
    def install_update(zip_response_content: bytes):
        """ Устанавливает обновление из архива """
        try:
            current_dir = "."
            temp_dir = ".temp_update"

            with zipfile.ZipFile(io.BytesIO(zip_response_content), 'r') as zip_ref:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)

            inner_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            if not inner_dirs:
                raise Exception("В архиве не найдена вложенная папка.")

            extracted_dir = os.path.join(temp_dir, inner_dirs[0])
            for root, _, files in os.walk(extracted_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, extracted_dir)
                    dst_path = os.path.join(current_dir, rel_path)
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)

            shutil.rmtree(temp_dir)
            return True

        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}При установке обновления произошла ошибка: {Fore.WHITE}{e}")
            return False


