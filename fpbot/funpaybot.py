import asyncio
import time
from datetime import datetime, timedelta
from typing import  Optional
import time
import traceback
from threading import Thread
from colorama import Fore
import queue
from rapidfuzz import fuzz


import settings
from settings import Settings as sett
from data import Data as data
from logging import getLogger
from fpbot.stats import get_stats, set_stats
from . import set_funpay_bot
from tgbot import get_telegram_bot, get_telegram_bot_loop
from tgbot.templates import log_text
from fpbot import get_funpay_bot

from FunPayAPI import Account, Runner, exceptions as fpapi_exceptions, types as fpapi_types
from FunPayAPI.common.enums import *
from FunPayAPI.updater.events import *

from __init__ import VERSION, ACCENT_COLOR
from core.console import set_title, restart
from core.handlers_manager import HandlersManager

from services.fp_support import FunPaySupportAPI

PREFIX = F"{Fore.CYAN}[FP]{Fore.WHITE}"



class FunPayBot:
    """
    Класс, описывающий FunPay бота.
    """

    def __init__(self):
        self.config = sett.get("config")
        self.messages = sett.get("messages")
        self.custom_commands = sett.get("custom_commands")
        self.auto_deliveries = sett.get("auto_deliveries")
        self.logger = getLogger(f"universal.funpay")

        try:
            proxy = {"https": "http://" + self.config["funpay"]["api"]["proxy"].replace("https://", "").replace("http://", ""), "http": "http://" + self.config["funpay"]["api"]["proxy"].replace("https://", "").replace("http://", "")} if self.config["funpay"]["api"]["proxy"] else None
            self.funpay_account = Account(golden_key=self.config["funpay"]["api"]["golden_key"],
                                          user_agent=self.config["funpay"]["api"]["user_agent"],
                                          requests_timeout=self.config["funpay"]["api"]["requests_timeout"],
                                          proxy=proxy or None).get()
            """ Класс, содержащий данные и методы FunPay аккаунта. """
        except fpapi_exceptions.UnauthorizedError as e:
            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось подключиться к вашему FunPay аккаунту. Ошибка: {Fore.WHITE}{e.short_str()}")
            print(f"{Fore.WHITE}🔑  Указать новый {Fore.YELLOW}golden_key{Fore.WHITE}? +/-")
            a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")
            if a == "+":
                param = {"funpay": {"api": {"golden_key": settings.DATA["config"]["params"]["funpay"]["api"]["golden_key"]}}}
                sett.configure("config", ACCENT_COLOR, params=param)
                restart()
            else:
                self.logger.info(f"{PREFIX} Вы отказались от настройки конфига. Перезагрузим бота и попробуем снова подключиться к вашему аккаунту...")
                restart()
        except AttributeError as e:
            if "proxy" in traceback.format_exc():
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось подключиться к вашему FunPay аккаунту. Ошибка: {Fore.WHITE}Не удалось подключиться к прокси. Возможно он указан неверно?")
                print(f"{Fore.WHITE}🌐  Убрать {Fore.LIGHTCYAN_EX}прокси{Fore.WHITE} и попробовать подключиться без него? +/-")
                a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")
                if a == "+":
                    self.config["funpay"]["api"]["proxy"] = ""
                    sett.set("config", self.config)
                    restart()
                else:
                    self.logger.info(f"{PREFIX} Вы отказались от очистки прокси. Перезагрузим бота и попробуем снова подключиться к вашему аккаунту...")
                    restart()

        self.initialized_users = data.get("initialized_users")
        """ Инициализированные в диалоге пользователи. """
        self.categories_raise_time = data.get("categories_raise_time")
        """ Следующие времена поднятия категорий. """
        self.auto_support_tickets = data.get("auto_support_tickets")
        """ Данные об автоматическом написании тикетов в поддержку. """
        self.stats = get_stats()
        """ Словарь статистика бота с момента запуска. """
        self.task_queue = queue.Queue()
        """ Очередь задач на выполнение. """

        # Эти ивенты событий не записываются в словарь данных, так как их время вычисляется во время работы
        # бота и оно не требуется для дальнейшего отслеживания, пока бот не запущен
        self.lots_raise_next_time = datetime.now()
        """ Время следующего поднятия лотов (изначально текущее). """
        self.refresh_funpay_account_next_time = datetime.now() + timedelta(seconds=3600)
        """ Время следующего обновления FunPay аккаунта (для обновления PHPSESSID) """

        set_funpay_bot(self) # сохранения текущего объекта бота

    def msg(self, message_name: str, exclude_watermark: bool = False, **kwargs) -> str:
        """ 
        Получает отформатированное сообщение из словаря сообщений.

        :param message_name: Наименование сообщения в словаре сообщений (ID).
        :type message_name: `str`

        :param exclude_watermark: Пропустить и не использовать водяной знак.
        :type exclude_watermark: `bool`
        """

        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"
        
        message_lines: list[str] = self.messages[message_name]
        if message_lines:
            try:
                formatted_lines = [line.format_map(SafeDict(**kwargs)) for line in message_lines]
                msg = "\n".join(formatted_lines)
                if not exclude_watermark and self.config["funpay"]["bot"]["messages_watermark_enabled"]:
                    msg += f'\n{self.config["funpay"]["bot"]["messages_watermark"]}' or ""
                return msg
            except:
                pass
        return "Не удалось получить сообщение"
    
    def get_lot_by_order_title(self, title: str, subcategory: types.SubCategory,
                               max_attempts: int = 3) -> types.LotShortcut:
        """
        Получает лот по названию заказа.

        :param title: Краткое описание заказа.
        :type title: `str`

        :param subcategory: Подкатегория товара заказа.
        :type subcategory: `FunPayAPI.types.SubCategory`

        :return: Объект лота.
        :rtype: `FunPayAPI.types.LotShortcut`
        """
        for _ in range(max_attempts-1):
            try:
                profile = self.funpay_account.get_user(self.funpay_account.id)
                lots = profile.get_sorted_lots(2)
                candidates = []
                for lot_subcat, lot_data in lots.items():
                    if subcategory and lot_subcat.id != subcategory.id:
                        continue
                    for _, lot in lot_data.items():
                        if not lot.title:
                            continue
                        if lot.title.strip() == title.strip():
                            return lot
                        score = fuzz.partial_ratio(title, lot.title)
                        token_score = fuzz.token_set_ratio(title, lot.title)
                        score = max(score, token_score)
                        candidates.append((score, lot))
                if not candidates:
                    return None
                candidates.sort(key=lambda x: x[0], reverse=True)
                best_score, best_lot = candidates[0]
                result = best_lot if best_score >= 70 else None
                if not result:
                    continue
                return result
            except:
                continue
        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось получить лот по названию заказа {Fore.LIGHTWHITE_EX}«{title}»")
    
    def raise_lots(self):
        """
        Поднимает все лоты всех категорий профиля FunPay,
        изменяет время следующего поднятия на наименьшее возможное
        """
        self.lots_raise_next_time = datetime.now() + timedelta(hours=4)
        raised_categories = []
        profile = self.funpay_account.get_user(self.funpay_account.id)
        for subcategory in list(profile.get_sorted_lots(2).keys()):
            category = subcategory.category
            if str(subcategory.id) in self.categories_raise_time:
                if datetime.now() < datetime.fromisoformat(self.categories_raise_time[str(subcategory.id)]):
                    continue
            try:
                self.funpay_account.raise_lots(category.id)
                raised_categories.append(category.name)
                # Если удалось поднять эту категорию, то снова отправляем запрос на её поднятие,
                # чтобы словить ошибку и получить время её следующего поднятия
                self.funpay_account.raise_lots(category.id)
            except fpapi_exceptions.RaiseError as e:
                if e.wait_time is not None:
                    self.categories_raise_time[str(subcategory.id)] = (datetime.now() + timedelta(seconds=e.wait_time)).isoformat()
                else:
                    del self.categories_raise_time[str(subcategory.id)]
            except fpapi_exceptions.RequestFailedError as e:
                if e.status_code == 429:
                    self.logger.error(f"{PREFIX} При поднятии лотов произошла ошибка 429 слишком частых запросов. Попытаюсь поднять лоты снова через 5 минут")
                    self.lots_raise_next_time = datetime.now() + timedelta(minutes=5)
                    return
            time.sleep(1)

        for category in self.categories_raise_time:
            if datetime.fromisoformat(self.categories_raise_time[category]) < self.lots_raise_next_time:
                self.lots_raise_next_time = datetime.fromisoformat(self.categories_raise_time[category])
        if len(raised_categories) > 0:
            self.logger.info(f'{PREFIX} {Fore.LIGHTYELLOW_EX}↑ Подняты категории: {Fore.LIGHTWHITE_EX}{f"{Fore.WHITE}, {Fore.LIGHTWHITE_EX}".join(map(str, raised_categories))}')

    def send_message(self, chat_id: int | str, text: Optional[str] = None, chat_name: Optional[str] = None,
                     interlocutor_id: Optional[int] = None, image_id: Optional[int] = None, add_to_ignore_list: bool = True,
                     update_last_saved_message: bool = False, leave_as_unread: bool = False, max_attempts: int = 3) -> types.Message:
        """
        Кастомный метод отправки сообщения в чат FunPay.
        Пытается отправить за 3 попытки, если не удаётся.
        
        :param chat_id: ID чата.
        :type chat_id: :obj:`int` or :obj:`str`

        :param text: текст сообщения.
        :type text: :obj:`str` or :obj:`None`, опционально

        :param chat_name: название чата (для возвращаемого объекта сообщения) (не нужно для отправки сообщения в публичный чат).
        :type chat_name: :obj:`str` or :obj:`None`, опционально

        :param interlocutor_id: ID собеседника (не нужно для отправки сообщения в публичный чат).
        :type interlocutor_id: :obj:`int` or :obj:`None`, опционально

        :param image_id: ID изображения. Доступно только для личных чатов.
        :type image_id: :obj:`int` or :obj:`None`, опционально

        :param add_to_ignore_list: добавлять ли ID отправленного сообщения в игнорируемый список Runner'а?
        :type add_to_ignore_list: :obj:`bool`, опционально

        :param update_last_saved_message: обновлять ли последнее сохраненное сообщение на отправленное в Runner'е?
        :type update_last_saved_message: :obj:`bool`, опционально.

        :param leave_as_unread: оставлять ли сообщение непрочитанным при отправке?
        :type leave_as_unread: :obj:`bool`, опционально

        :return: экземпляр отправленного сообщения.
        :rtype: :class:`FunPayAPI.types.Message`
        """
        for _ in range(max_attempts-1):
            try:
                mess = self.funpay_account.send_message(chat_id, text, chat_name, interlocutor_id, 
                                                        image_id, add_to_ignore_list, 
                                                        update_last_saved_message, leave_as_unread)
                return mess
            except:
                continue
        self.logger.error(f"{PREFIX} Не удалось отправить сообщение {Fore.LIGHTWHITE_EX}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.WHITE}{chat_id} {Fore.LIGHTRED_EX}")

    def log_to_tg(self, text: str):
        """
        Логгирует ивент в Telegram бота.

        :param text: Текст лога.
        :type text: `str`
        """
        asyncio.run_coroutine_threadsafe(get_telegram_bot().log_event(text), get_telegram_bot_loop())
    
    
    def create_support_tickets(self):
        try:
            last_time = datetime.now()
            self.auto_support_tickets["last_time"] = last_time.isoformat()
            data.set("auto_support_tickets", self.auto_support_tickets)
            fpbot = get_funpay_bot()
            support_api = FunPaySupportAPI(fpbot.funpay_account).get()
            self.logger.info(f"{PREFIX} 📞  Создаю тикеты в тех. поддержку на закрытие заказов...")

            def calculate_orders(all_orders, orders_per_ticket=25):
                return [all_orders[i:i+orders_per_ticket] for i in range(0, len(all_orders), orders_per_ticket)]

            all_sales: list[fpapi_types.OrderShortcut] = []
            start_from = self.auto_support_tickets["next_start_from"] if self.auto_support_tickets["next_start_from"] != None else None
            while len(all_sales) < fpbot.funpay_account.active_sales:
                sales = fpbot.funpay_account.get_sales(start_from=start_from, include_paid=True, include_closed=False, include_refunded=False)
                for sale in sales[1]:
                    all_sales.append(sale)
                start_from = sales[0]
                time.sleep(0.5)
            
            order_ids = calculate_orders([order.id for order in all_sales], self.config["funpay"]["bot"]["auto_support_tickets_orders_per_ticket"])
            ticketed_orders = []
            for order_ids_per_ticket in order_ids:
                formatted_order_ids = ", ".join(order_ids_per_ticket)
                resp: dict = support_api.create_ticket(formatted_order_ids, f"Здравствуйте! Прошу подтвердить заказы, ожидающие подтверждения: {formatted_order_ids}. С уважением, {fpbot.funpay_account.username}!")
                if resp.get("error") or not resp.get("action") or resp["action"]["message"] != "Ваша заявка отправлена.":
                    self.auto_support_tickets["next_start_from"] = order_ids_per_ticket[0]
                    break
                ticketed_orders.extend(order_ids_per_ticket)
                self.logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}{resp['action']['url'].split('/')[-1]} (https://support.funpay.com{resp['action']['url']}) {Fore.WHITE}— тикет создан для {Fore.LIGHTYELLOW_EX}{len(order_ids_per_ticket)} заказов")
            else:
                self.auto_support_tickets["next_start_from"] = None
            self.auto_support_tickets["last_time"] = (datetime.now() + timedelta(seconds=fpbot.config["funpay"]["bot"]["auto_support_tickets_create_interval"])).isoformat()
            
            if len(ticketed_orders) == 0 and self.auto_support_tickets["next_start_from"] is not None:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось создать тикеты в тех. поддержку по причине: {Fore.WHITE}{resp.get('error') if resp else 'Неизвестная ошибка.'}")
            elif len(ticketed_orders) >= 0:
                self.logger.info(f"{PREFIX} {Fore.LIGHTYELLOW_EX}📞✅  Создал {Fore.LIGHTWHITE_EX}{len(calculate_orders(ticketed_orders))} тикета(-ов) в тех. поддержку {Fore.LIGHTYELLOW_EX}на закрытие {Fore.LIGHTWHITE_EX}{len(ticketed_orders)} заказов")
            next_time = last_time + timedelta(seconds=self.config["funpay"]["bot"]["auto_support_tickets_create_interval"])
            self.logger.info(f"{PREFIX} Следующая попытка будет {Fore.LIGHTWHITE_EX}{next_time.strftime(f'%d.%m{Fore.WHITE} в {Fore.LIGHTWHITE_EX}%H:%M')}")
        except Exception as e:
            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При отправке тикетов на закрытие произошла ошибка: {Fore.WHITE}")
            traceback.print_exc()
    
    async def run_bot(self):

        self.logger.info(f"{PREFIX} FunPay бот запущен и активен на аккаунте {Fore.LIGHTWHITE_EX}{self.funpay_account.username}{Fore.WHITE}, баланс {Fore.LIGHTWHITE_EX}{self.funpay_account.total_balance} {self.funpay_account.currency.name}{Fore.WHITE}")
        if self.config["funpay"]["api"]["proxy"]:
            ip_port = self.config['funpay']['api']['proxy'].split("@")[1] if "@" in self.config['funpay']['api']['proxy'] else self.config['funpay']['api']['proxy']
            self.logger.info(f"{PREFIX} FunPay бот подключен к прокси {Fore.LIGHTWHITE_EX}{ip_port}")

        def handler_on_funpay_bot_init(fpbot: FunPayBot):
            """ Начальный хендлер ON_INIT """

            def worker():
                while True:
                    func, args, kwargs = self.task_queue.get()
                    func(*args, **kwargs)
                    self.task_queue.task_done()
            Thread(target=worker, daemon=True).start()

            def endless_loop(cycle_delay=5):
                while True:
                    try:
                        set_funpay_bot(fpbot)
                        set_title(f"FunPay Universal v{VERSION} | {self.funpay_account.username}: {self.funpay_account.total_balance} {self.funpay_account.currency.name}. Активных заказов: {self.funpay_account.active_sales}")
                        
                        if fpbot.initialized_users != data.get("initialized_users"): data.set("initialized_users", fpbot.initialized_users)
                        if fpbot.categories_raise_time != data.get("categories_raise_time"): data.set("categories_raise_time", fpbot.categories_raise_time)
                        if fpbot.auto_support_tickets != data.get("auto_support_tickets"): fpbot.auto_support_tickets = data.get("auto_support_tickets")
                        fpbot.config = sett.get("config") if fpbot.config != sett.get("config") else fpbot.config
                        fpbot.messages = sett.get("messages") if fpbot.messages != sett.get("messages") else fpbot.messages
                        fpbot.custom_commands = sett.get("custom_commands") if fpbot.custom_commands != sett.get("custom_commands") else fpbot.custom_commands
                        fpbot.auto_deliveries = sett.get("auto_deliveries") if fpbot.auto_deliveries != sett.get("auto_deliveries") else fpbot.auto_deliveries

                        if datetime.now() > self.refresh_funpay_account_next_time:
                            proxy = {"https": "http://" + self.config["funpay"]["api"]["proxy"].replace("https://", "").replace("http://", ""), "http": "http://" + self.config["funpay"]["api"]["proxy"].replace("https://", "").replace("http://", "")} if self.config["funpay"]["api"]["proxy"] else None
                            self.funpay_account = Account(golden_key=self.config["funpay"]["api"]["golden_key"],
                                                          user_agent=self.config["funpay"]["api"]["user_agent"],
                                                          requests_timeout=self.config["funpay"]["api"]["requests_timeout"],
                                                          proxy=proxy or None).get(update_phpsessid=True)
                            self.refresh_funpay_account_next_time = datetime.now() + timedelta(seconds=2400)

                        # --- Автоматическое поднятие лотов ---
                        if fpbot.config["funpay"]["bot"]["auto_raising_lots_enabled"] and datetime.now() > fpbot.lots_raise_next_time:
                            self.task_queue.put((fpbot.raise_lots, (), {}))

                        # --- Автоматическое создание тикетов в поддержку на закрытие заказов ---
                        if datetime.now() >= (datetime.fromisoformat(self.auto_support_tickets["last_time"]) + timedelta(seconds=self.config["funpay"]["bot"]["auto_support_tickets_create_interval"])) if self.auto_support_tickets["last_time"] else datetime.now():
                            self.auto_support_tickets["last_time"] = datetime.now().isoformat()
                            data.set("auto_support_tickets", self.auto_support_tickets)
                            self.task_queue.put((fpbot.create_support_tickets, (), {}))
                    except Exception:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка: {Fore.WHITE}")
                        traceback.print_exc()
                    time.sleep(cycle_delay)

            Thread(target=endless_loop, daemon=True).start()
        
        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        bot_event_handlers["ON_FUNPAY_BOT_INIT"].insert(0, handler_on_funpay_bot_init)
        HandlersManager.set_bot_event_handlers(bot_event_handlers)

        async def handler_new_message(fpbot: FunPayBot, event: NewMessageEvent):
            try:
                this_chat = fpbot.funpay_account.get_chat_by_name(event.message.chat_name, True)
                if fpbot.config["funpay"]["bot"]["tg_logging_enabled"] and (fpbot.config["funpay"]["bot"]["tg_logging_events"]["new_user_message"] or fpbot.config["funpay"]["bot"]["tg_logging_events"]["new_system_message"]):
                    if event.message.author != fpbot.funpay_account.username:
                        do = False
                        if fpbot.config["funpay"]["bot"]["tg_logging_events"]["new_user_message"] and event.message.author.lower() != "funpay": do = True 
                        if fpbot.config["funpay"]["bot"]["tg_logging_events"]["new_system_message"] and event.message.author.lower() == "funpay": do = True 
                        if do:
                            text = f"<b>{event.message.author}:</b> {event.message.text or ''}"
                            if event.message.image_link:
                                text += f' <b><a href="{event.message.image_link}">{event.message.image_name}</a></b>'
                            fpbot.log_to_tg(log_text(f'💬 Новое сообщение в <a href="https://funpay.com/chat/?node={event.message.chat_id}">чате</a>', text.strip()))

                if this_chat.name not in fpbot.initialized_users:
                    try:
                        if self.config["funpay"]["bot"]["first_message_enabled"]:
                            if event.message.type is MessageTypes.NON_SYSTEM and event.message.author == this_chat.name:
                                fpbot.send_message(this_chat.id, fpbot.msg("user_not_initialized", username=event.message.author))
                        fpbot.initialized_users.append(this_chat.name)
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При отправке приветственного сообщения для {event.message.author} произошла ошибка: {Fore.WHITE}{e}")

                if event.message.author == this_chat.name:
                    if self.config["funpay"]["bot"]["custom_commands_enabled"]:
                        if event.message.text in self.custom_commands.keys():
                            try:
                                message = "\n".join(self.custom_commands[event.message.text])
                                fpbot.send_message(this_chat.id, message)
                            except Exception as e:
                                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе пользовательской команды \"{event.message.text}\" у {event.message.author} произошла ошибка: {Fore.WHITE}{e}")
                                fpbot.send_message(this_chat.id, fpbot.msg("command_error"))
                    if str(event.message.text).lower() == "!команды" or str(event.message.text).lower() == "!commands":
                        try:
                            fpbot.send_message(this_chat.id, fpbot.msg("buyer_command_commands"))
                        except Exception as e:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе команды \"!команды\" у {event.message.author} произошла ошибка: {Fore.WHITE}{e}")
                            fpbot.send_message(this_chat.id, fpbot.msg("command_error"))
                    elif str(event.message.text).lower() == "!продавец" or str(event.message.text).lower() == "!seller":
                        try:
                            asyncio.run_coroutine_threadsafe(get_telegram_bot().call_seller(event.message.author, this_chat.id), get_telegram_bot_loop())
                            fpbot.send_message(this_chat.id, fpbot.msg("buyer_command_seller"))
                        except Exception as e:
                            self.logger.log(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе команды \"!продавец\" у {event.message.author} произошла ошибка: {Fore.WHITE}{e}")
                            fpbot.send_message(this_chat.id, fpbot.msg("command_error"))

                if event.message.type is MessageTypes.NEW_FEEDBACK:
                    review_author = event.message.text.split(' ')[1]
                    review_order_id = event.message.text.split(' ')[-1].replace('#', '').replace('.', '')
                    order = fpbot.funpay_account.get_order(review_order_id)
                    review = order.review
                    self.logger.info(f"{PREFIX} {Fore.LIGHTYELLOW_EX}✨💬 Новый {'⭐' * review.stars} отзыв на заказ {Fore.LIGHTWHITE_EX}{order.id}{Fore.LIGHTYELLOW_EX} от {Fore.LIGHTWHITE_EX}{order.buyer_username}{Fore.LIGHTYELLOW_EX}")
                    if fpbot.config["funpay"]["bot"]["tg_logging_enabled"] and fpbot.config["funpay"]["bot"]["tg_logging_events"]["new_review"]:
                        fpbot.log_to_tg(log_text(f'✨💬 Новый отзыв на заказ <a href="https://funpay.com/orders/{review_order_id}/">#{review_order_id}</a>', f"<b>┏ Оценка:</b> {'⭐' * review.stars}\n<b>┣ Оставил:</b> {review.author}\n<b>┗ Текст отзыва:</b> {review.text}"))
                    if fpbot.config["funpay"]["bot"]["auto_reviews_replies_enabled"]:
                        try:
                            fpbot.funpay_account.send_review(review_order_id, fpbot.msg("order_review_reply_text",
                                                                                        review_date=datetime.now().strftime("%d.%m.%Y"),
                                                                                        order_title=order.title,
                                                                                        order_amount=order.amount,
                                                                                        order_price=order.sum))
                        except Exception as e:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При оставлении ответа на отзыв заказа произошла ошибка: {Fore.WHITE}{e}")
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_new_order(fpbot: FunPayBot, event: NewOrderEvent):
            try:
                this_chat = fpbot.funpay_account.get_chat_by_name(event.order.buyer_username, True)
                self.logger.info(f"{PREFIX} {Fore.LIGHTYELLOW_EX}📋  Новый заказ {Fore.LIGHTWHITE_EX}{event.order.id}{Fore.LIGHTYELLOW_EX} от {Fore.LIGHTWHITE_EX}{event.order.buyer_username}{Fore.LIGHTYELLOW_EX} на сумму {Fore.LIGHTWHITE_EX}{event.order.price} {fpbot.funpay_account.currency.name}")
                if fpbot.config["funpay"]["bot"]["tg_logging_enabled"] and fpbot.config["funpay"]["bot"]["tg_logging_events"]["new_order"]:
                    fpbot.log_to_tg(log_text(f'📋 Новый заказ <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a>', f"<b>┏ Покупатель:</b> {event.order.buyer_username}\n<b>┣ Товар:</b> {event.order.description}\n<b>┣ Количество:</b> {event.order.amount}\n<b>┗ Сумма:</b> {event.order.price} {fpbot.funpay_account.currency.name}"))
                if self.config["funpay"]["bot"]["auto_deliveries_enabled"]:
                    lot = self.get_lot_by_order_title(event.order.description, event.order.subcategory)
                    if lot:
                        if str(lot.id) in self.auto_deliveries.keys():
                            fpbot.send_message(this_chat.id, "\n".join(self.auto_deliveries[str(lot.id)]))
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых заказов произошла ошибка: {Fore.WHITE}{traceback.print_exc()}")
            
        async def handler_order_status_changed(fpbot: FunPayBot, event: OrderStatusChangedEvent):
            try:
                status = "Неизвестный"
                if event.order.status is OrderStatuses.REFUNDED: status = "Возврат"
                elif event.order.status is OrderStatuses.CLOSED: status = "Закрыт"
                self.logger.info(f"{PREFIX} {Fore.LIGHTYELLOW_EX}🔄️📋  Статус заказа {Fore.LIGHTWHITE_EX}{event.order.id}{Fore.LIGHTYELLOW_EX} от {Fore.LIGHTWHITE_EX}{event.order.buyer_username}{Fore.LIGHTYELLOW_EX} изменился на {Fore.LIGHTWHITE_EX}«{status}»")
                if fpbot.config["funpay"]["bot"]["tg_logging_enabled"] and fpbot.config["funpay"]["bot"]["tg_logging_events"]["order_status_changed"]:
                    fpbot.log_to_tg(log_text(f'🔄️📋 Статус заказа <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a> изменился', f"<b>Новый статус:</b> {status}"))
                try:
                    if event.order.status is OrderStatuses.CLOSED:
                        fpbot.stats.earned_money = round(fpbot.stats.earned_money + event.order.price, 2)
                    elif event.order.status is OrderStatuses.REFUNDED:
                        fpbot.stats.orders_refunded = fpbot.stats.orders_refunded + 1
                except Exception as e:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При подсчёте статистики произошла ошибка: {Fore.WHITE}{e}")
                finally:
                    set_stats(fpbot.stats)

                if event.order.status is OrderStatuses.CLOSED or event.order.status is OrderStatuses.REFUNDED:
                    if event.order.status is OrderStatuses.CLOSED:
                        chat = fpbot.funpay_account.get_chat_by_name(event.order.buyer_username, True)
                        fpbot.send_message(chat.id, fpbot.msg("order_confirmed"))
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

        self.stats.bot_launch_time = datetime.now()
        set_stats(self.stats)
        self.logger.info(f"{PREFIX} Слушатель событий запущен")
        runner = Runner(self.funpay_account)
        for event in runner.listen(requests_delay=self.config["funpay"]["api"]["runner_requests_delay"]):
            funpay_event_handlers = HandlersManager.get_funpay_event_handlers() # чтобы каждый раз брать свежие хендлеры, ибо модули могут отключаться/включаться
            if event.type in funpay_event_handlers:
                for handler in funpay_event_handlers[event.type]:
                    try:
                        await handler(self, event)
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}{e}")