from datetime import datetime
from colorama import Fore, Style

class Logger:
    """ 
    Класс логгера (кастомный для удобства)

    :param name: Имя логгера
    """

    def __init__(self, name: str):
        self.name = name

    def debug(self, mess):
        """ Логирует DEBUG сообщение в консоль """
        print(f"{Fore.WHITE}[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] (ОТКЛАДКА) {Style.RESET_ALL}{mess}")

    def info(self, mess):
        """ Логирует INFO сообщение в консоль """
        print(f"{Fore.WHITE}[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] (ИНФО) {Style.RESET_ALL}{mess}")

    def error(self, mess):
        """ Логирует ERROR сообщение в консоль """
        print(f"{Fore.LIGHTRED_EX}[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] (ОШИБКА) {Style.RESET_ALL}{mess}")

    def warn(self, mess):
        """ Логирует WARNING сообщение в консоль """
        print(f"{Fore.LIGHTYELLOW_EX}[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] (ПРЕДУПРЕЖДЕНИЕ) {Style.RESET_ALL}{mess}")

    def critical(self, mess):
        """ Логирует CRITICAL сообщение в консоль """
        print(f"{Fore.RED}[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] (КРИТИЧЕСКОЕ) {Style.RESET_ALL}{mess}")

def get_logger(name: str):
    return Logger(name)