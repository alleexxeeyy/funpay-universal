import asyncio
import time
from datetime import datetime, timedelta
import time
import traceback
from threading import Thread
from colorama import Fore, Style

from settings import Config, Messages, CustomCommands, AutoDeliveries
from logging import getLogger
from fpbot.utils.stats import get_stats, set_stats
from . import set_funpay_bot

from FunPayAPI import Account, Runner, exceptions as fpapi_exceptions
from FunPayAPI.common.enums import *
from fpbot.data import Data
from FunPayAPI.updater.events import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tgbot.telegrambot import TelegramBot

from bot_settings.app import CURRENT_VERSION
from core.console import set_title, restart
from core.handlers_manager import HandlersManager

PREFIX = F"{Fore.LIGHTWHITE_EX}[funpay bot]{Fore.WHITE}"

class FunPayBot:
    """
    Класс, запускающий и инициализирующий FunPay бота.

    :param tgbot: Объект класса TelegramBot
    :param tgbot_loop: loop, в котором запущен Telegram бот
    """

    def __init__(self, tgbot: 'TelegramBot' = None, 
                 tgbot_loop: asyncio.AbstractEventLoop = None):
        self.config = Config.get()
        self.messages = Messages.get()
        self.custom_commands = CustomCommands.get()
        self.auto_deliveries = AutoDeliveries.get()
        self.logger = getLogger(f"UNIVERSAL.FunPayBot")

        self.tgbot = tgbot
        """ Класс, содержащий данные и методы Telegram бота """
        self.tgbot_loop = tgbot_loop
        """ Объект loop, в котором запущен Telegram бот """

        try:
            self.funpay_account = Account(golden_key=self.config["golden_key"],
                                          user_agent=self.config["user_agent"],
                                          requests_timeout=self.config["funpayapi_requests_timeout"]).get()
            """ Класс, содержащий данные и методы аккаунта FunPay """
        except fpapi_exceptions.UnauthorizedError as e:
            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось подключиться к вашему FunPay аккаунту. Ошибка: {Fore.WHITE}{e.short_str()}")
            print(f"{Fore.LIGHTWHITE_EX}Начать снова настройку конфига? +/-")
            a = input(f"{Fore.WHITE}> {Fore.LIGHTWHITE_EX}")
            if a == "+":
                Config.configure_config()
                restart()
            else:
                self.logger.info(f"{PREFIX} Вы отказались от настройки конфига. Перезагрузим бота и попробуем снова подключиться к вашему аккаунту...")
                restart()

        # Инициализация data классов
        self.initialized_users = Data.get_initialized_users()
        """ Инициализированные пользователи """
        self.categories_raise_time = Data.get_categories_raise_time()
        """ Следующие времена поднятия категорий """
        self.stats = get_stats()
        """ Словарь статистика бота с момента запуска """

        # Эти ивенты событий не записываются в словарь данных, так как их время вычисляется во время работы
        # бота и оно не требуется для дальнейшего отслеживания, пока бот не запущен
        self.lots_raise_next_time = datetime.now()
        """ Время следующего поднятия лотов (изначально текущее) """
        self.refresh_funpay_account_next_time = datetime.now() + timedelta(seconds=3600)
        """ Время следующего обновления FunPay аккаунта (для обновления PHPSESSID) """

        set_funpay_bot(self)

    def msg(self, message_name: str, exclude_watermark: bool = False, **kwargs) -> str:
        """ 
        Получает отформатированное сообщение из словаря сообщений.

        :param message_name: Наименование сообщения в словаре сообщений (ID).
        :type message_name: str

        :param exclude_watermark: Пропустить и не использовать водяной знак.
        :type exclude_watermark: bool
        """

        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"
        
        message_lines: list[str] = self.messages[message_name]
        if message_lines:
            try:
                formatted_lines = [line.format_map(SafeDict(**kwargs)) for line in message_lines]
                msg = "\n".join(formatted_lines)
                if not exclude_watermark:
                    msg += f'\n{self.config["messages_watermark"]}' if self.config["messages_watermark_enabled"] and self.config["messages_watermark"] else ""
                return msg
            except:
                pass
        return "Не удалось получить сообщение"
    
    def get_lot_by_order_title(self, title: str) -> types.LotShortcut:
        """
        Получает лот по названию заказа.

        :param title: Краткое описание заказа.
        :type title: `str`

        :return: Объект лота.
        :rtype: `FunPayAPI.types.LotShortcut`
        """
        profile = self.funpay_account.get_user(self.funpay_account.id)
        lots = profile.get_lots()
        for lot in lots:
            if title in lot.title or lot.title in title or title == lot.title:
                return lot
        return None
    
    def raise_lots(self):
        """
        Поднимает все лоты всех категорий профиля FunPay,
        изменяет время следующего поднятия на наименьшее возможное
        """
        next_time = datetime.now() + timedelta(hours=4)
        raised_categories = []
        profile = self.funpay_account.get_user(self.funpay_account.id)
        for subcategory in list(profile.get_sorted_lots(2).keys()):
            category = subcategory.category
            if subcategory.fullname in self.categories_raise_time:
                if datetime.now() < datetime.fromisoformat(self.categories_raise_time[subcategory.fullname]):
                    continue
            try:
                self.funpay_account.raise_lots(category.id)
                raised_categories.append(category.name)
                # Если удалось поднять эту категорию, то снова отправляем запрос на её поднятие,
                # чтобы словить ошибку и получить время её следующего поднятия
                self.funpay_account.raise_lots(category.id)
            except fpapi_exceptions.RaiseError as e:
                if e.wait_time is not None:
                    self.categories_raise_time[subcategory.fullname] = (datetime.now() + timedelta(seconds=e.wait_time)).isoformat()
                else:
                    del self.categories_raise_time[subcategory.fullname]
            except fpapi_exceptions.RequestFailedError as e:
                if e.status_code == 429:
                    self.logger.error(f"{PREFIX} При поднятии лотов произошла ошибка 429 слишком частых запросов. Попытаюсь поднять лоты снова через 5 минут")
                    self.lots_raise_next_time = datetime.now() + timedelta(minutes=5)
                    return
            time.sleep(1)

        for category in self.categories_raise_time:
            if datetime.fromisoformat(self.categories_raise_time[category]) < next_time:
                next_time = datetime.fromisoformat(self.categories_raise_time[category])
        self.lots_raise_next_time = next_time

        if len(raised_categories) > 0:
            self.logger.info(f'{PREFIX} {Fore.LIGHTYELLOW_EX}↑ Подняты категории: {Fore.LIGHTWHITE_EX}{f"{Fore.WHITE}, {Fore.LIGHTWHITE_EX}".join(map(str, raised_categories))}')

    async def run_bot(self) :
        """ Основная функция-запускатор бота. """

        # --- задаём начальные хендлеры бота ---
        def handler_on_funpay_bot_init(fpbot: FunPayBot):
            """ Начальный хендлер ON_INIT """
            def endless_loop(cycle_delay=5):
                """ Действия, которые должны выполняться в другом потоке, вне цикла раннера """
                while True:
                    try:
                        set_funpay_bot(fpbot)
                        set_title(f"FunPay Universal v{CURRENT_VERSION} | {self.funpay_account.username}: {self.funpay_account.total_balance} {self.funpay_account.currency.name}. Активных заказов: {self.funpay_account.active_sales}")
                        if Data.get_initialized_users() != fpbot.initialized_users:
                            Data.set_initialized_users(fpbot.initialized_users)
                        if Data.get_categories_raise_time() != fpbot.categories_raise_time:
                            Data.set_categories_raise_time(fpbot.categories_raise_time)
                        if Config.get() != fpbot.config:
                            fpbot.config = Config.get()
                        if Messages.get() != fpbot.messages:
                            fpbot.messages = Messages.get()
                        if CustomCommands.get() != fpbot.custom_commands:
                            fpbot.custom_commands = CustomCommands.get()
                        if AutoDeliveries.get() != fpbot.auto_deliveries:
                            fpbot.auto_deliveries = AutoDeliveries.get()

                        if datetime.now() > self.refresh_funpay_account_next_time:
                            self.funpay_account = Account(golden_key=self.config["golden_key"],
                                                          user_agent=self.config["user_agent"],
                                                          requests_timeout=self.config["funpayapi_requests_timeout"]).get()
                            self.refresh_funpay_account_next_time = datetime.now() + timedelta(seconds=3600)

                        if fpbot.config["auto_raising_lots_enabled"]:
                            if datetime.now() > fpbot.lots_raise_next_time:
                                fpbot.raise_lots()
                    except fpapi_exceptions.RequestFailedError as e:
                        if e.status_code == 429:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                            time.sleep(10)
                        else:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка запроса {e.status_code}: {Fore.WHITE}\n{e}")
                    except Exception:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка: {Fore.WHITE}")
                        traceback.print_exc()
                    time.sleep(cycle_delay)

            endless_loop_thread = Thread(target=endless_loop, daemon=True)
            endless_loop_thread.start()
        
        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        bot_event_handlers["ON_FUNPAY_BOT_INIT"].insert(0, handler_on_funpay_bot_init)
        HandlersManager.set_bot_event_handlers(bot_event_handlers)

        async def handler_new_message(fpbot: FunPayBot, event: NewMessageEvent):
            """ Начальный хендлер новых сообщений """
            try:
                this_chat = fpbot.funpay_account.get_chat_by_id(event.message.chat_id, True)
                if self.config["first_message_enabled"]:
                    if this_chat.name not in fpbot.initialized_users:
                        try:
                            if event.message.type is MessageTypes.NON_SYSTEM and event.message.author == this_chat.name:
                                fpbot.funpay_account.send_message(this_chat.id, fpbot.msg("user_not_initialized",
                                                                                          buyer_username=event.message.author))
                            fpbot.initialized_users.append(this_chat.name)
                        except Exception as e:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При отправке приветственного сообщения для {event.message.author} произошла ошибка: {Fore.WHITE}{e}")

                if event.message.author == this_chat.name:
                    if self.config["custom_commands_enabled"]:
                        if event.message.text in self.custom_commands.keys():
                            try:
                                message = "\n".join(self.custom_commands[event.message.text])
                                fpbot.funpay_account.send_message(this_chat.id, message)
                            except Exception as e:
                                self.logger.info(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе пользовательской команды \"{event.message.text}\" у {event.message.author} произошла ошибка: {Fore.WHITE}{e}")
                                fpbot.funpay_account.send_message(this_chat.id, fpbot.msg("command_error"))
                    if str(event.message.text).lower() == "!команды" or str(event.message.text).lower() == "!commands":
                        try:
                            fpbot.funpay_account.send_message(this_chat.id, fpbot.msg("buyer_command_commands"))
                        except Exception as e:
                            self.logger.info(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе команды \"!команды\" у {event.message.author} произошла ошибка: {Fore.WHITE}{e}")
                            fpbot.funpay_account.send_message(this_chat.id, fpbot.msg("command_error"))
                    if str(event.message.text).lower() == "!продавец" or str(event.message.text).lower() == "!seller":
                        try:
                            asyncio.run_coroutine_threadsafe(fpbot.tgbot.call_seller(event.message.author, this_chat.id), self.tgbot_loop)
                            fpbot.funpay_account.send_message(this_chat.id, fpbot.msg("buyer_command_seller"))
                        except Exception as e:
                            self.logger.log(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе команды \"!продавец\" у {event.message.author} произошла ошибка: {Fore.WHITE}{e}")
                            fpbot.funpay_account.send_message(this_chat.id, fpbot.msg("command_error"))

                if event.message.type is MessageTypes.NEW_FEEDBACK:
                    review_author = event.message.text.split(' ')[1]
                    review_order_id = event.message.text.split(' ')[-1].replace('#', '').replace('.', '')
                    if fpbot.config["auto_reviews_replies_enabled"]:
                        try:
                            order = fpbot.funpay_account.get_order(review_order_id)
                            fpbot.funpay_account.send_review(review_order_id, fpbot.msg("order_review_reply_text",
                                                                                        review_date=datetime.now().strftime("%d.%m.%Y"),
                                                                                        order_title=order.title,
                                                                                        order_amount=order.amount,
                                                                                        order_price=order.sum))
                        except Exception as e:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При оставлении ответа на отзыв заказа произошла ошибка: {Fore.WHITE}{e}")
            except fpapi_exceptions.RequestFailedError as e:
                if e.status_code == 429:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                    time.sleep(10)
                else:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка {e.status_code}: {Fore.WHITE}\n{e}")
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_new_order(fpbot: FunPayBot, event: NewOrderEvent):
            """ Начальный хендлер нового заказа """
            try:
                this_chat = fpbot.funpay_account.get_chat_by_id(event.order.chat_id, True)
                try:
                    self.logger.info(f"{PREFIX} 🛒  Новый заказ {Fore.LIGHTYELLOW_EX}{event.order.id}{Fore.WHITE} от {Fore.LIGHTYELLOW_EX}{event.order.buyer_username}{Fore.WHITE} на сумму {Fore.LIGHTYELLOW_EX}{event.order.price} р.")
                    if self.config["auto_deliveries_enabled"]:
                        order = self.funpay_account.get_order(event.order.id)
                        lot = self.get_lot_by_order_title(order.title)
                        if lot:
                            if str(lot.id) in self.auto_deliveries.keys():
                                self.funpay_account.send_message(this_chat.id, "\n".join(self.auto_deliveries[str(lot.id)]))
                                self.logger.info(f"{PREFIX} 🚀  На заказ {Fore.LIGHTYELLOW_EX}{event.order.id}{Fore.WHITE} от покупателя {Fore.LIGHTYELLOW_EX}{event.order.buyer_username}{Fore.WHITE} было автоматически выдано пользовательское сообщение после покупки")
                except Exception as e:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке нового заказа для {event.order.buyer_username} произошла ошибка: {Fore.WHITE}{e}")
            except fpapi_exceptions.RequestFailedError as e:
                if e.status_code == 429:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых заказов произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                    time.sleep(10)
                else:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых заказов произошла ошибка {e.status_code}: {Fore.WHITE}\n{e}")
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых заказов произошла ошибка: {Fore.WHITE}{traceback.print_exc()}")
            
        async def handler_order_status_changed(fpbot: FunPayBot, event: OrderStatusChangedEvent):
            """ Начальный хендлер изменения статуса заказа """
            try:
                try:
                    if event.order.status is OrderStatuses.CLOSED:
                        fpbot.stats["earned_money"] += event.order.price
                        fpbot.stats["earned_money"] = round(fpbot.stats["earned_money"], 2)
                    elif event.order.status is OrderStatuses.REFUNDED:
                        fpbot.stats["orders_refunded"] += 1
                except Exception as e:
                    self.logger.info(f"{PREFIX} {Fore.LIGHTRED_EX}При подсчёте статистики произошла ошибка: {Fore.WHITE}{e}")
                finally:
                    set_stats(fpbot.stats)

                if event.order.status is OrderStatuses.CLOSED or event.order.status is OrderStatuses.REFUNDED:
                    if event.order.status is OrderStatuses.CLOSED:
                        chat = fpbot.funpay_account.get_chat_by_id(event.order.chat_id, True)
                        fpbot.funpay_account.send_message(chat.id, fpbot.msg("order_confirmed"))
            except fpapi_exceptions.RequestFailedError as e:
                if e.status_code == 429:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента смены статуса заказа произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                    time.sleep(10)
                else:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента смены статуса заказа произошла ошибка {e.status_code}: {Fore.WHITE}\n{e}")
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента смены статуса заказа произошла ошибка: {Fore.WHITE}{traceback.print_exc()}")
            
        funpay_event_handlers = HandlersManager.get_funpay_event_handlers()
        funpay_event_handlers[EventTypes.NEW_MESSAGE].insert(0, handler_new_message)
        funpay_event_handlers[EventTypes.NEW_ORDER].insert(0, handler_new_order)
        funpay_event_handlers[EventTypes.ORDER_STATUS_CHANGED].insert(0, handler_order_status_changed)
        HandlersManager.set_funpay_event_handlers(funpay_event_handlers)

        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        def handle_on_funpay_bot_init():
            """ 
            Запускается при инициализации FunPay бота.
            Запускает за собой все хендлеры ON_FUNPAY_BOT_INIT 
            """
            if "ON_FUNPAY_BOT_INIT" in bot_event_handlers:
                for handler in bot_event_handlers["ON_FUNPAY_BOT_INIT"]:
                    try:
                        handler(self)
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_FUNPAY_BOT_INIT: {Fore.WHITE}{e}")
        handle_on_funpay_bot_init()

        self.logger.info(f"{PREFIX} FunPay бот запущен и активен")
        runner = Runner(self.funpay_account)
        for event in runner.listen(requests_delay=self.config["funpayapi_runner_requests_delay"]):
            funpay_event_handlers = HandlersManager.get_funpay_event_handlers() # чтобы каждый раз брать свежие хендлеры, ибо модули могут отключаться/включаться
            if event.type in funpay_event_handlers:
                for handler in funpay_event_handlers[event.type]:
                    try:
                        await handler(self, event)
                    except fpapi_exceptions.RequestFailedError as e:
                        if e.status_code == 429:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка 429 слишком частых запросов при обработке хендлера {handler} в ивенте {event.type.name}. Ждём 10 секунд и пробуем снова")
                            time.sleep(10)
                        else:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка {e.status_code} слишком частых запросов при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}\n{e}")
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}{e}")