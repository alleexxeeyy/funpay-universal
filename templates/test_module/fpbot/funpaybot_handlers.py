from ..meta import PREFIX, NAME
from utils.logger import get_logger
logger = get_logger(f"{NAME}.FunPayBot")
from ..settings import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fpbot.funpaybot import FunPayBot
    
from FunPayAPI import exceptions as fpapiexceptions, enums
from FunPayAPI.updater.events import *
from FunPayAPI.common.enums import *
from FunPayAPI.account import *

from .data import Data
from ..settings import Config


class FunPayBotHandlers:
    """ Класс, содержащий хендлеры ивентов FunPay бота """

    def __init__(self) -> None:
        self.data = Data()
        self.some_data = self.data.get_some_data()
        
    def get_params_from_lot_desc(self, lot_desc: str) -> dict[str: str]:
        """
        Получает параметры #test_module из описания лота.
        Если нету, возвращает пустой словарь

        :param lot_desc: Полное описание лота
        """
        try:
            params = {}
            if "#test_module" in lot_desc:
                matches = [line for line in lot_desc.splitlines() if "#test_module" in line.lower()]
                line_params = matches[0].replace("#test_module:", "").strip().split(",")
                for param in line_params:
                    param = param.strip()
                    key = param.split("=")[0].strip()
                    value = param.split("=")[1].strip()
                    params[key] = value
            return params
        except Exception as e:
            print(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка при получении параметров лота по описанию: {Fore.WHITE}{e}")

    def get_params_from_lot(self, funpay_account: Account, lot_id: int = 0) -> dict[str: str]:
        """
        Получает параметры #test_module из лота.
        Если нету, возвращает пустой словарь

        :param funpay_account: Класс аккаунта FunPay
        :param lot_id: ID лота
        """
        try:
            lot_page = funpay_account.get_lot_page(lot_id)
            params = self.get_params_from_lot_desc(lot_page.full_description)
            return params
        except Exception as e:
            print(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка при получении параметров лота {lot_id}: {Fore.WHITE}{e}")

    def get_params_from_lots(self, funpay_account: Account) -> list[dict[str: str]]:
        """
        Получает параметры #test_module из всех лотов профиля.
        Возвращает массив параметров

        :param funpay_account: Класс аккаунта FunPay
        """
        try:
            funpay_profile = funpay_account.get_user(funpay_account.id)
            my_lots = funpay_profile.get_lots()
            params = []
            for lot in my_lots:
                try:
                    lot_page = funpay_account.get_lot_page(lot.id)
                    lot_params = self.get_params_from_lot_desc(lot_page.full_description)
                    params.append(lot_params)
                    break
                except Exception as e:
                    print(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка при получении параметров лота {lot_page.short_description}: {Fore.WHITE}{e}")
            return params
        except Exception as e:
            print(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка при получении параметров лотов: {Fore.WHITE}{e}")

    def get_smm_lot(self, funpay_account: Account, smm_service: int | str) -> types.LotShortcut:
        """
        Получает SMM лот профиля по ID SMM сервиса,
        если не находит, возвращает None

        :param funpay_account: Класс аккаунта FunPay
        """
        try:
            funpay_profile = funpay_account.get_user(funpay_account.id)
            my_lots = funpay_profile.get_lots()
            smm_service = str(smm_service)
            for lot in my_lots:
                lot_page = funpay_account.get_lot_page(lot.id)
                params = self.get_params_from_lot_desc(lot_page.full_description)
                if "service" in params and params["serivice"] == smm_service:
                    return lot
            return None
        except Exception as e:
            print(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка при получении SMM лота по сервису {smm_service}: {Fore.WHITE}{e}")

    def get_smm_lots(self, funpay_account: Account) -> list[types.LotShortcut]:
        """
        Получает все SMM лоты профиля (в описании которых есть #test_module).
        Если не находит, возвращает пустой массив

        :param funpay_account: Класс аккаунта FunPay
        """
        try:
            funpay_profile = funpay_account.get_user(funpay_account.id)
            my_lots = funpay_profile.get_lots()
            smm_lots = []
            for lot in my_lots:
                try:
                    lot_page = funpay_account.get_lot_page(lot.id)
                    if "#test_module" in lot_page.full_description:
                        smm_lots.append(lot)
                except Exception as e:
                    print(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка при получении SMM лота {lot_page.short_description}: {Fore.WHITE}{e}")
            return smm_lots
        except Exception as e:
            print(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка при получении SMM лотов: {Fore.WHITE}{e}")


    def handler_on_funpay_bot_init(self, fpbot: 'FunPayBot'):
        """ Хендлер инициализации бота """
        logger.info(f"{PREFIX} FunPay бот инициализирован")

    async def handler_new_message(self, fpbot: 'FunPayBot', event: NewMessageEvent):
        """ Хендлер нового сообщения на FunPay """
        logger.info(f"{PREFIX} Новое сообщение: {event.message.text}")

    async def handler_new_order(self, fpbot: 'FunPayBot', event: NewOrderEvent):
        """ Хендлер нового заказа на FunPay """
        logger.info(f"{PREFIX} Новый заказ: {event.order.id}")