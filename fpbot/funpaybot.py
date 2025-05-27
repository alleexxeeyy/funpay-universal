import asyncio
import time
from datetime import datetime, timedelta
import time
import traceback
from threading import Thread
from colorama import Fore, Style

from settings import Config, Messages, CustomCommands, AutoDeliveries
from utils.logger import get_logger
from fpbot.utils.stats import get_stats, set_stats

from FunPayAPI import Account, Runner, exceptions
from FunPayAPI.common.enums import *
from fpbot.data import Data
from FunPayAPI.updater.events import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tgbot.telegrambot import TelegramBot

from bot_settings.app import CURRENT_VERSION
from core.console import set_title
from core.handlers_manager import HandlersManager

PREFIX = F"{Fore.LIGHTWHITE_EX}[funpay bot]{Fore.WHITE}"

class FunPayBot:
    """
    Класс, запускающий и инициализирующий FunPay бота

    :param tgbot: Объект класса TelegramBot
    :param tgbot_loop: Луп, в котором запущен Telegram бот
    """

    def __init__(self, tgbot: 'TelegramBot' = None, 
                 tgbot_loop: asyncio.AbstractEventLoop = None):
        self.config = Config.get()
        self.messages = Messages.get()
        self.custom_commands = CustomCommands.get()
        self.auto_deliveries = AutoDeliveries.get()
        self.data = Data()
        self.logger = get_logger(f"UNIVERSAL.TelegramBot")
        
        self.bot_event_handlers = HandlersManager.get_bot_event_handlers()
        self.funpay_event_handlers = HandlersManager.get_funpay_event_handlers()

        self.tgbot = tgbot
        """ Класс, содержащий данные и методы Telegram бота """
        self.tgbot_loop = tgbot_loop
        """ Объект loop, в котором запущен Telegram бот """

        try:
            self.funpay_account = Account(golden_key=self.config["golden_key"],
                                          user_agent=self.config["user_agent"],
                                          requests_timeout=self.config["funpayapi_timeout"]).get()
            """ Класс, содержащий данные и методы аккаунта FunPay """
        except exceptions.UnauthorizedError as e:
            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось подключиться к вашему FunPay аккаунту. Ошибка: {Fore.WHITE}{e.short_str()}")
            print(f"{Fore.LIGHTWHITE_EX}Начать снова настройку конфига? +/-")
            a = input(f"{Fore.WHITE}> {Fore.LIGHTWHITE_EX}")
            if a == "+":
                Config.configure_config()
                print(f"{Fore.LIGHTWHITE_EX}Перезапустите бота, чтобы продолжить работу.")
                raise SystemExit(1)
            else:
                self.logger.info(f"{PREFIX} Вы отказались от настройки конфига. Пробуем снова подключиться к вашему FunPay аккаунту...")
                return FunPayBot(self.tgbot, self.tgbot_loop).run_bot()
            
        self.funpay_profile = self.funpay_account.get_user(self.funpay_account.id)
        """ Класс, содержащий данные и методы нашего профиля FunPay """

        # Инициализация data классов
        self.initialized_users = self.data.get_initialized_users()
        """ Инициализированные пользователи """
        self.categories_raise_time = self.data.get_categories_raise_time()
        """ Следующие времена поднятия категорий """
        self.events_next_time = self.data.get_events_next_time()
        """ Следующие времена событий, которые нужно будет выполнить """
        self.stats = get_stats()
        """ Словарь статистика бота с момента запуска """

        # Эти ивенты событий не записываются в словарь данных, так как их время вычисляется во время работы
        # бота и оно не требуется для дальнейшего отслеживания, пока бот не запущен
        self.lots_raise_next_time = datetime.now()
        """ Время следующего поднятия лотов (изначально текущее) """
        

    def msg(self, message_name: str, **kwargs) -> str:
        """ 
        Получает отформатированное сообщение из словаря сообщений

        :param message_name: Наименование сообщения в словаре сообщений (ID).
        :type message_name: str
        """

        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"
        
        message_lines = self.messages[message_name]
        if message_lines:
            try:
                formatted_lines = [line.format_map(SafeDict(**kwargs)) for line in message_lines]
                return "\n".join(formatted_lines)
            except:
                pass
        return "Не удалось получить сообщение"
    
    def get_lot_by_order_title(self, title: str) -> types.LotShortcut:
        """
        Получает лот по названию заказа.

        :param title: Краткое описание заказа.
        :type title: str

        :return: Лот.
        :rtype: `FunPayApi.types.LotShortcut`
        """

        lots = self.funpay_profile.get_lots()
        for lot in lots:
            if title in lot.description:
                return lot
        return None
    
    def raise_lots(self):
        """
        Поднимает все лоты всех категорий профиля FunPay,
        изменяет время следующего поднятия на наименьшее возможное
        """

        next_time = datetime.now() + timedelta(hours=4)
        raised_categories = []
        for subcategory in list(self.funpay_profile.get_sorted_lots(2).keys()):
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
            except exceptions.RaiseError as e:
                if e.wait_time is not None:
                    self.categories_raise_time[subcategory.fullname] = (datetime.now() + timedelta(seconds=e.wait_time)).isoformat()
                else:
                    del self.categories_raise_time[subcategory.fullname]
            except exceptions.RequestFailedError as e:
                if e.status_code == 429:
                    self.logger.error(f"{PREFIX} При поднятии лотов произошла ошибка слишком большого кол-во запросов. Попытаюсь поднять лоты снова через 15 минут")
                    self.lots_raise_next_time = datetime.now() + timedelta(minutes=15)
                    return
            time.sleep(1)

        for category in self.categories_raise_time:
            if datetime.fromisoformat(self.categories_raise_time[category]) < next_time:
                next_time = datetime.fromisoformat(self.categories_raise_time[category])
        self.lots_raise_next_time = next_time

        if len(raised_categories) > 0:
            self.logger.info(f'{PREFIX} {Fore.LIGHTYELLOW_EX}↑ Подняты категории: {Fore.LIGHTWHITE_EX}{f"{Fore.WHITE}, {Fore.LIGHTWHITE_EX}".join(map(str, raised_categories))}')

    def save_lots(self) -> bool:
        """ Сохраняет все лоты профиля в Data файл saved_lots.json """

        lots = self.funpay_profile.get_lots()
        saved_lots = self.data.get_saved_lots()
        self.logger.info(f"{PREFIX} Сохранение всех лотов профиля...")
        for lot in lots:
            try:
                if lot.id in saved_lots["inactive"]:
                    saved_lots["inactive"].remove(lot.id)
                if lot.id not in saved_lots["active"]:
                    saved_lots["active"].append(lot.id)
            except Exception as e:
                self.logger.error(f"{PREFIX} При сохранении лота {lot.id} произошла ошибка: {e}")
        else:
            self.data.set_saved_lots(saved_lots)
            self.logger.info(f"{PREFIX} Лоты были сохранены")
            return True

    def activate_lots(self) -> bool:
        """ Активирует все сохранённые лоты профиля """
        saved_lots = self.data.get_saved_lots()
        self.logger.info(f"{PREFIX} Активация всех лотов профиля...")
        for lot_id in list(saved_lots["inactive"]):
            try:
                lot_fields = self.funpay_account.get_lot_fields(lot_id)
                lot_fields.active = True
                self.funpay_account.save_lot(lot_fields)
                
                saved_lots["inactive"].remove(lot_id)
                if lot_id not in saved_lots["active"]:
                    saved_lots["active"].append(lot_id)
            except Exception as e:
                saved_lots["inactive"].remove(lot_id)
        else:
            self.data.set_saved_lots(saved_lots)
            self.logger.info(f"{PREFIX} Все лоты профиля были активированы")
            return True

    def deactivate_lots(self) -> bool:
        """ Деактивирует все сохранённые лоты профиля """

        saved_lots = self.data.get_saved_lots()
        self.logger.info(f"{PREFIX} Деактивация всех лотов профиля...")
        for lot_id in list(saved_lots["active"]):
            try:
                lot_fields = self.funpay_account.get_lot_fields(lot_id)
                lot_fields.active = False
                self.funpay_account.save_lot(lot_fields)

                saved_lots["active"].remove(lot_id)
                if lot_id not in saved_lots["inactive"]:
                    saved_lots["inactive"].append(lot_id)
            except Exception as e:
                saved_lots["active"].remove(lot_id)
        else:
            self.data.set_saved_lots(saved_lots)
            self.logger.info(f"{PREFIX} Все лоты профиля были деактивированы")
            return True

    def find_lot_by_order_title(self, order_title: str) -> types.LotShortcut:
        """ Находит лот по названию заказа. """
        
        lots = self.funpay_profile.get_lots()
        for lot in lots:
            if order_title in lot.title or lot.title in order_title or order_title == lot.title:
                return lot
        return None


    async def run_bot(self) -> None:
        """ Основная функция-запускатор бота """
        
        # --- задаём начальные хендлеры бота ---
        def handler_on_funpay_bot_init(fpbot: FunPayBot):
            """ Начальный хендлер ON_INIT """
            def endless_loop(cycle_delay=5):
                """ Действия, которые должны выполняться в другом потоке, вне цикла раннера """
                while True:
                    try:
                        set_title(f"FunPay Universal v{CURRENT_VERSION} | {self.funpay_profile.username}: {self.funpay_account.total_balance} {self.funpay_account.currency.name}. Активных заказов: {self.funpay_account.active_sales}")
                        if fpbot.data.get_initialized_users() != fpbot.initialized_users:
                            fpbot.data.set_initialized_users(fpbot.initialized_users)
                        if fpbot.data.get_categories_raise_time() != fpbot.categories_raise_time:
                            fpbot.data.set_categories_raise_time(fpbot.categories_raise_time)
                        if fpbot.data.get_events_next_time() != fpbot.events_next_time:
                            fpbot.data.set_events_next_time(fpbot.events_next_time)
                        if Config.get() != fpbot.config:
                            fpbot.config = Config.get()
                        if Messages.get() != fpbot.messages:
                            fpbot.messages = Messages.get()
                        if CustomCommands.get() != fpbot.custom_commands:
                            fpbot.custom_commands = CustomCommands.get()
                        if AutoDeliveries.get() != fpbot.auto_deliveries:
                            fpbot.auto_deliveries = AutoDeliveries.get()

                        # --- Сохранение текущих лотов аккаунта ---
                        if datetime.now() > datetime.fromisoformat(fpbot.events_next_time["save_lots_next_time"]):
                            try:
                                fpbot.save_lots()
                                timedelta_sec = fpbot.config["lots_saving_interval"]
                                fpbot.events_next_time["save_lots_next_time"] = (datetime.now() + timedelta(seconds=timedelta_sec)).isoformat()
                            except Exception as e:
                                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При сохранении лотов произошла ошибка: {Fore.WHITE}{e}")

                        # --- Поднятие всех лотов ---
                        if fpbot.config["auto_raising_lots_enabled"] == True:
                            if datetime.now() > fpbot.lots_raise_next_time:
                                fpbot.raise_lots()
                    except Exception:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка: {Fore.WHITE}{traceback.print_exc()}")
                    time.sleep(cycle_delay)

            endless_loop_thread = Thread(target=endless_loop, daemon=True)
            endless_loop_thread.start()
        
        self.bot_event_handlers["ON_FUNPAY_BOT_INIT"].insert(0, handler_on_funpay_bot_init)
        HandlersManager.set_bot_event_handlers(self.bot_event_handlers)

        async def handler_new_message(fpbot: FunPayBot, event: NewMessageEvent):
            """ Начальный хендлер новых сообщений """
            try:
                this_chat = fpbot.funpay_account.get_chat(event.message.chat_id)
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
                                time.sleep(1)
                                fpbot.funpay_account.send_review(review_order_id, fpbot.msg("order_review_reply_text",
                                                                                            review_date=datetime.now().strftime("%d.%m.%Y"),
                                                                                            order_title=order.title,
                                                                                            order_amount=order.amount,
                                                                                            order_price=order.sum,))
                            except Exception as e:
                                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При оставлении ответа на отзыв заказа произошла ошибка: {Fore.WHITE}{e}")
                    
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}{traceback.print_exc()}")

        async def handler_new_order(fpbot: FunPayBot, event: NewOrderEvent):
            """ Начальный хендлер нового заказа """
            try:
                this_chat = fpbot.funpay_account.get_chat(event.order.chat_id)
                try:
                    self.logger.info(f"{PREFIX} 🛒  Новый заказ {Fore.LIGHTYELLOW_EX}{event.order.id}{Fore.WHITE} от {Fore.LIGHTYELLOW_EX}{event.order.buyer_username}{Fore.WHITE} на сумму {Fore.LIGHTYELLOW_EX}{event.order.price} р.")
                    if self.config["auto_delivery_enabled"]:
                        order = self.funpay_account.get_order(event.order.id)
                        lot = self.find_lot_by_order_title(order.title)
                        if lot:
                            if str(lot.id) in self.auto_deliveries.keys():
                                self.funpay_account.send_message(this_chat.id, "\n".join(self.auto_deliveries[str(lot.id)]))
                                self.logger.info(f"{PREFIX} 🚀  На заказ {Fore.LIGHTYELLOW_EX}{event.order.id}{Fore.WHITE} от покупателя {Fore.LIGHTYELLOW_EX}{event.order.buyer_username}{Fore.WHITE} было автоматически выдано пользовательское сообщение после покупки")
                except Exception as e:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке нового заказа для {event.order.buyer_username} произошла ошибка: {Fore.WHITE}{e}")
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
                        chat = fpbot.funpay_account.get_chat_by_name(event.order.buyer_username, True)
                        fpbot.funpay_account.send_message(chat.id, fpbot.msg("order_confirmed"))
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента смены статуса заказа произошла ошибка: {Fore.WHITE}{traceback.print_exc()}")
            
        self.funpay_event_handlers[EventTypes.NEW_MESSAGE].insert(0, handler_new_message)
        self.funpay_event_handlers[EventTypes.NEW_ORDER].insert(0, handler_new_order)
        self.funpay_event_handlers[EventTypes.ORDER_STATUS_CHANGED].insert(0, handler_order_status_changed)
        HandlersManager.set_funpay_event_handlers(self.funpay_event_handlers)

        def handle_on_funpay_bot_init():
            """ 
            Запускается при инициализации FunPay бота.
            Запускает за собой все хендлеры ON_FUNPAY_BOT_INIT 
            """
            if "ON_FUNPAY_BOT_INIT" in self.funpay_event_handlers:
                for handler in self.funpay_event_handlers["ON_FUNPAY_BOT_INIT"]:
                    try:
                        handler(self)
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_FUNPAY_BOT_INIT: {Fore.WHITE}{e}")
        handle_on_funpay_bot_init()

        self.logger.info(f"{PREFIX} FunPay бот запущен и активен")
        runner = Runner(self.funpay_account)
        for event in runner.listen(requests_delay=self.config["runner_requests_delay"]):
            self.funpay_event_handlers = HandlersManager.get_funpay_event_handlers() # чтобы каждый раз брать свежие хендлеры, ибо модули могут отключаться/включаться
            if event.type in self.funpay_event_handlers:
                for handler in self.funpay_event_handlers[event.type]:
                    try:
                        await handler(self, event)
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}{e}")