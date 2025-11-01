from __future__ import annotations
import asyncio
import time
from datetime import datetime, timedelta
from typing import  Optional
import time
from threading import Thread
from colorama import Fore
from rapidfuzz import fuzz
import textwrap
import shutil
import re

from FunPayAPI import Account, Runner, exceptions as fpapi_exceptions, types as fpapi_types
from FunPayAPI.common.enums import *
from FunPayAPI.updater.events import *

from __init__ import VERSION
from core.utils import set_title, shutdown, run_async_in_thread
from core.handlers import add_bot_event_handler, add_funpay_event_handler, call_bot_event, call_funpay_event
from settings import DATA, Settings as sett
from data import Data as data
from logging import getLogger
from tgbot.telegrambot import get_telegram_bot, get_telegram_bot_loop
from tgbot.templates import log_text, log_new_mess_kb, log_new_order_kb, log_new_review_kb
from services.fp_support import FunPaySupportAPI

from .stats import get_stats, set_stats


def get_funpay_bot() -> None | FunPayBot:
    if hasattr(FunPayBot, "instance"):
        return getattr(FunPayBot, "instance")


class FunPayBot:
    def __new__(cls, *args, **kwargs) -> FunPayBot:
        if not hasattr(cls, "instance"):
            cls.instance = super(FunPayBot, cls).__new__(cls)
        return getattr(cls, "instance")
    
    def __init__(self):
        self.config = sett.get("config")
        self.messages = sett.get("messages")
        self.custom_commands = sett.get("custom_commands")
        self.auto_deliveries = sett.get("auto_deliveries")
        self.logger = getLogger(f"universal.funpay")
        
        proxy = {
            "https": "http://" + self.config["funpay"]["api"]["proxy"], 
            "http": "http://" + self.config["funpay"]["api"]["proxy"]
        } if self.config["funpay"]["api"]["proxy"] else None
        self.account = self.funpay_account = Account(
            golden_key=self.config["funpay"]["api"]["golden_key"],
            user_agent=self.config["funpay"]["api"]["user_agent"],
            requests_timeout=self.config["funpay"]["api"]["requests_timeout"],
            proxy=proxy
        ).get()

        self.initialized_users = data.get("initialized_users")
        self.categories_raise_time = data.get("categories_raise_time")
        self.auto_tickets = data.get("auto_tickets")
        self.stats = get_stats()

        self.__lots_raise_next_time = datetime.now()
        
        
    def msg(self, message_name: str, exclude_watermark: bool = False,
            messages_config_name: str = "messages", messages_data: dict = DATA,
            **kwargs) -> str | None:
        """ 
        Получает отформатированное сообщение из словаря сообщений.

        :param message_name: Наименование сообщения в словаре сообщений (ID).
        :type message_name: `str`

        :param exclude_watermark: Пропустить и не использовать водяной знак.
        :type exclude_watermark: `bool`

        :param messages_config_name: Имя файла конфигурации сообщений.
        :type messages_config_name: `str`

        :param messages_data: Словарь данных конфигурационных файлов.
        :type messages_data: `dict` or `None`

        :return: Отформатированное сообщение или None, если сообщение выключено.
        :rtype: `str` or `None`
        """
        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"

        messages = sett.get(messages_config_name, messages_data) or {}
        mess = messages.get(message_name, {})
        if not mess.get("enabled"):
            return None
        message_lines: list[str] = mess.get("text", [])
        if not message_lines:
            return f"Сообщение {message_name} пустое"
        try:
            msg = "\n".join([line.format_map(SafeDict(**kwargs)) for line in message_lines])
            if not exclude_watermark and self.config["funpay"]["watermark"]["enabled"]:
                msg += f'\n{self.config["funpay"]["watermark"]["value"]}' or ""
            return msg
        except:
            pass
        return f"Не удалось получить сообщение {message_name}"
    
    def get_lot_by_title(self, title: str, subcategory: types.SubCategory | None = None,
                         subcategory_id: int | None = None, max_attempts: int = 3) -> types.LotShortcut:
        """
        Получает лот по названию заказа.

        :param title: Краткое описание заказа.
        :type title: `str`

        :param subcategory: Подкатегория товара, _опционально_.
        :type subcategory: `FunPayAPI.types.SubCategory` or `None`

        :param subcategory_id: ID подкатегории товара, _опционально_.
        :type subcategory_id: `FunPayAPI.types.SubCategory` or `None`

        :return: Объект лота.
        :rtype: `FunPayAPI.types.LotShortcut`
        """
        user = self.account.get_user(self.account.id)
        lots = user.get_lots()
        subcategory_id = subcategory_id if subcategory_id else subcategory.id if subcategory else None
        cleaned_title = (" ".join(re.sub(r"[^\w\s]", " ", title).split())).lower()

        for lot in lots:
            if subcategory_id and lot.subcategory.id != subcategory_id:
                continue

            cleaned_lot_title = (" ".join(re.sub(r"[^\w\s]", " ", lot.title).split())).lower()
            if (
                cleaned_lot_title in cleaned_title
                or cleaned_lot_title == cleaned_title
            ):
                return lot
            
        self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось получить лот по названию заказа «{title}»")
    
    def get_lot_by_order_title(self, title: str, subcategory: types.SubCategory | None = None,
                               subcategory_id: int | None = None) -> types.LotShortcut:
        """Эквивалент метода `get_lot_by_title()`"""
        return self.get_lot_by_title(title, subcategory, subcategory_id)

    def send_message(self, chat_id: int | str, text: Optional[str] = None, chat_name: Optional[str] = None,
                     interlocutor_id: Optional[int] = None, image_id: Optional[int] = None, add_to_ignore_list: bool = True,
                     update_last_saved_message: bool = False, leave_as_unread: bool = False, max_attempts: int = 3) -> types.Message | None:
        """
        Кастомный метод отправки сообщения в чат FunPay.
        Пытается отправить за 3 попытки, если не удалось - выдаёт ошибку в консоль.
        
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

        :return: Экземпляр отправленного сообщения или None, если сообщение не отправилось.
        :rtype: :class:`FunPayAPI.types.Message` or `None`
        """
        if text is None and not image_id:
            return None
        for _ in range(max_attempts):
            try:
                mess = self.funpay_account.send_message(chat_id, text, chat_name, interlocutor_id, 
                                                        image_id, add_to_ignore_list, 
                                                        update_last_saved_message, leave_as_unread)
                return mess
            except (fpapi_exceptions.MessageNotDeliveredError, fpapi_exceptions.RequestFailedError):
                continue
            except Exception as e:
                text = text.replace('\n', '').strip()
                self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при отправке сообщения {Fore.LIGHTWHITE_EX}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.LIGHTWHITE_EX}{chat_id} {Fore.LIGHTRED_EX}: {Fore.WHITE}{e}")
                return None
        text = text.replace('\n', '').strip()
        self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось отправить сообщение {Fore.LIGHTWHITE_EX}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.LIGHTWHITE_EX}{chat_id} {Fore.LIGHTRED_EX}")


    def raise_lots(self):
        """
        Поднимает все лоты всех категорий профиля FunPay,
        изменяет время следующего поднятия на наименьшее возможное
        """
        self.__lots_raise_next_time = datetime.now() + timedelta(hours=4)
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
                time.sleep(0.5)
                # Если удалось поднять эту категорию, то снова отправляем запрос на её поднятие,
                # чтобы словить ошибку и получить время её следующего поднятия
                self.funpay_account.raise_lots(category.id)
            except fpapi_exceptions.RaiseError as e:
                if e.wait_time is not None:
                    self.categories_raise_time[str(subcategory.id)] = (datetime.now() + timedelta(seconds=e.wait_time)).isoformat()
                else:
                    del self.categories_raise_time[str(subcategory.id)]
            time.sleep(1)

        for category in self.categories_raise_time:
            if datetime.fromisoformat(self.categories_raise_time[category]) < self.__lots_raise_next_time:
                self.__lots_raise_next_time = datetime.fromisoformat(self.categories_raise_time[category])
        if len(raised_categories) > 0:
            self.logger.info(f"{Fore.YELLOW}Подняты категории: {Fore.LIGHTWHITE_EX}{f'{Fore.WHITE}, {Fore.LIGHTWHITE_EX}'.join(map(str, raised_categories))}")

    def create_tickets(self):
        """Создаёт тикеты в тех. поддержку на закрытие неподтверждённых заказов."""
        last_time = datetime.now()
        self.auto_tickets["last_time"] = last_time.isoformat()
        data.set("auto_tickets", self.auto_tickets)
        support_api = FunPaySupportAPI(self.funpay_account).get()
        self.logger.info(f"{Fore.WHITE}Создаю тикеты в тех. поддержку на закрытие заказов...")

        def calculate_orders(all_orders, orders_per_ticket=25):
            return [all_orders[i:i+orders_per_ticket] for i in range(0, len(all_orders), orders_per_ticket)]

        all_sales: list[fpapi_types.OrderShortcut] = []
        start_from = self.auto_tickets["next_start_from"] if self.auto_tickets["next_start_from"] != None else None
        while len(all_sales) < self.funpay_account.active_sales:
            sales = self.funpay_account.get_sales(start_from=start_from, include_paid=True, include_closed=False, include_refunded=False)
            for sale in sales[1]:
                if sale.date + timedelta(seconds=self.config["funpay"]["auto_tickets"]["min_order_age"]) <= datetime.now():
                    all_sales.append(sale)
            start_from = sales[0]
            time.sleep(0.5)
        
        order_ids = calculate_orders([order.id for order in all_sales], self.config["funpay"]["auto_tickets"]["enabled"])
        ticketed_orders = []
        for order_ids_per_ticket in order_ids:
            formatted_order_ids = ", ".join(order_ids_per_ticket)
            resp: dict = support_api.create_ticket(formatted_order_ids, f"Здравствуйте! Прошу подтвердить заказы, ожидающие подтверждения: {formatted_order_ids}. С уважением, {self.funpay_account.username}!")
            if resp.get("error") or not resp.get("action") or resp["action"]["message"] != "Ваша заявка отправлена.":
                self.auto_tickets["next_start_from"] = order_ids_per_ticket[0]
                break
            ticketed_orders.extend(order_ids_per_ticket)
            self.logger.info(f"{Fore.LIGHTWHITE_EX}{resp['action']['url'].split('/')[-1]} (https://support.funpay.com{resp['action']['url']}) {Fore.WHITE}— тикет создан для {Fore.LIGHTCYAN_EX}{len(order_ids_per_ticket)} заказов")
        else:
            self.auto_tickets["next_start_from"] = None
        self.auto_tickets["last_time"] = datetime.now().isoformat()
        
        if len(ticketed_orders) == 0 and self.auto_tickets["next_start_from"] is not None:
            self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось создать тикеты в тех. поддержку по причине: {Fore.WHITE}{resp.get('error') if resp else 'Неизвестная ошибка.'}")
        elif len(ticketed_orders) >= 0:
            self.logger.info(f"{Fore.CYAN}Создал {Fore.LIGHTCYAN_EX}{len(calculate_orders(ticketed_orders))} тикета(-ов) в тех. поддержку {Fore.CYAN}на закрытие {Fore.LIGHTCYAN_EX}{len(ticketed_orders)} заказов")
        next_time = last_time + timedelta(seconds=self.config["funpay"]["auto_tickets"]["interval"])
        self.logger.info(f"Следующая попытка будет {Fore.LIGHTWHITE_EX}{next_time.strftime(f'%d.%m{Fore.WHITE} в {Fore.LIGHTWHITE_EX}%H:%M')}")

    
    def log_new_message(self, message: types.Message):
        ch_header = f"Новое сообщение в чате с {message.chat_name}:"
        self.logger.info(f"{Fore.CYAN}{ch_header.replace(message.chat_name, f'{Fore.LIGHTCYAN_EX}{message.chat_name}')}")
        self.logger.info(f"{Fore.CYAN}│ {Fore.LIGHTWHITE_EX}{message.author}:")
        max_width = shutil.get_terminal_size((80, 20)).columns - 40
        longest_line_len = 0
        text = ""
        if message.text is not None: text = message.text
        elif message.image_link is not None: text = f"{Fore.LIGHTMAGENTA_EX}Изображение {Fore.WHITE}({message.image_link})"
        for raw_line in text.split("\n"):
            if not raw_line.strip():
                self.logger.info(f"{Fore.CYAN}│")
                continue
            wrapped_lines = textwrap.wrap(raw_line, width=max_width)
            for wrapped in wrapped_lines:
                self.logger.info(f"{Fore.CYAN}│ {Fore.WHITE}{wrapped}")
                longest_line_len = max(longest_line_len, len(wrapped.strip()))
        underline_len = max(len(ch_header)-1, longest_line_len+2)
        self.logger.info(f"{Fore.CYAN}└{'─'*underline_len}")
    
    def log_new_order(self, order: types.OrderShortcut):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новый заказ #{order.id}:")
        self.logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{order.buyer_username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{order.description}")
        self.logger.info(f" · Количество: {Fore.LIGHTWHITE_EX}{order.amount or order.parse_amount() or 0}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{order.price} {self.funpay_account.currency.name}")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
    
    def log_order_status_changed(self, order: types.OrderShortcut, status_frmtd: str = "Неизвестный"):
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")
        self.logger.info(f"{Fore.WHITE}Статус заказа {Fore.LIGHTWHITE_EX}#{order.id} {Fore.WHITE}изменился:")
        self.logger.info(f" · Статус: {Fore.LIGHTWHITE_EX}{status_frmtd}")
        self.logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{order.buyer_username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{order.description}")
        self.logger.info(f" · Количество: {Fore.LIGHTWHITE_EX}{order.amount or order.parse_amount() or 0}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{order.price} {self.funpay_account.currency.name}")
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")
    
    def log_new_review(self, review: types.Review):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новый отзыв по заказу #{review.order_id}:")
        self.logger.info(f" · Оценка: {Fore.LIGHTYELLOW_EX}{'★' * review.stars or 5} ({review.stars or 5})")
        self.logger.info(f" · Текст: {Fore.LIGHTWHITE_EX}{review.text}")
        self.logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{review.author}")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
    

    async def _on_funpay_bot_init(fpbot: FunPayBot):
        fpbot.stats.bot_launch_time = datetime.now()
        
        def check_config_loop():
            def _check_config():
                set_title(f"FunPay Universal v{VERSION} | {fpbot.funpay_account.username}: {fpbot.funpay_account.total_balance} {fpbot.funpay_account.currency.name if fpbot.funpay_account.currency != Currency.UNKNOWN else 'RUB'}. Активных заказов: {fpbot.funpay_account.active_sales}")
                if fpbot.initialized_users != data.get("initialized_users"): data.set("initialized_users", fpbot.initialized_users)
                if fpbot.categories_raise_time != data.get("categories_raise_time"): data.set("categories_raise_time", fpbot.categories_raise_time)
                if fpbot.auto_tickets != data.get("auto_tickets"): fpbot.auto_tickets = data.get("auto_tickets")
                if fpbot.stats != get_stats(): set_stats(fpbot.stats)
                fpbot.config = sett.get("config") if fpbot.config != sett.get("config") else fpbot.config
                fpbot.messages = sett.get("messages") if fpbot.messages != sett.get("messages") else fpbot.messages
                fpbot.custom_commands = sett.get("custom_commands") if fpbot.custom_commands != sett.get("custom_commands") else fpbot.custom_commands
                fpbot.auto_deliveries = sett.get("auto_deliveries") if fpbot.auto_deliveries != sett.get("auto_deliveries") else fpbot.auto_deliveries

            while True:
                Thread(target=_check_config, daemon=True).start()
                time.sleep(3)

        def refresh_account_loop():
            def _refresh_account():
                proxy = {
                    "https": "http://" + fpbot.config["funpay"]["api"]["proxy"], 
                    "http": "http://" + fpbot.config["funpay"]["api"]["proxy"]
                } if fpbot.config["funpay"]["api"]["proxy"] else None
                fpbot.account = fpbot.funpay_account = Account(
                    golden_key=fpbot.config["funpay"]["api"]["golden_key"],
                    user_agent=fpbot.config["funpay"]["api"]["user_agent"],
                    requests_timeout=fpbot.config["funpay"]["api"]["requests_timeout"],
                    proxy=proxy
                ).get()

            while True:
                Thread(target=_refresh_account, daemon=True).start()
                time.sleep(2400)

        def check_banned_loop():
            def _check_banned():
                user = fpbot.account.get_user(fpbot.account.id)
                if user.banned:
                    fpbot.logger.critical(f"")
                    fpbot.logger.critical(f"{Fore.LIGHTRED_EX}Ваш FunPay аккаунт был заблокирован! К сожалению, я не могу продолжать работу на заблокированном аккаунте...")
                    fpbot.logger.critical(f"Напишите в тех. поддержку FunPay, чтобы узнать причину бана и как можно быстрее решить эту проблему.")
                    fpbot.logger.critical(f"")
                    shutdown()

            while True:
                Thread(target=_check_banned, daemon=True).start()
                time.sleep(900)

        def raise_lots_loop():
            while True:
                if (
                    fpbot.config["funpay"]["auto_raising_lots"]["enabled"] 
                    and datetime.now() > fpbot.__lots_raise_next_time
                ):
                    Thread(target=fpbot.raise_lots, daemon=True).start()
                time.sleep(3)

        def create_tickets_loop():
            while True:
                if (
                    fpbot.config["funpay"]["auto_tickets"]["enabled"]
                    and datetime.now() >= (datetime.fromisoformat(fpbot.auto_tickets["last_time"]) + timedelta(seconds=fpbot.config["funpay"]["auto_tickets"]["interval"])) if fpbot.auto_tickets["last_time"] else datetime.now()
                ):
                    Thread(target=fpbot.create_tickets, daemon=True).start()
                time.sleep(3)

        Thread(target=check_config_loop, daemon=True).start()
        Thread(target=refresh_account_loop, daemon=True).start()    
        Thread(target=check_banned_loop, daemon=True).start()
        Thread(target=raise_lots_loop, daemon=True).start()
        Thread(target=create_tickets_loop, daemon=True).start()
    
    async def _on_new_review(fpbot: FunPayBot, event: NewMessageEvent):
        review_order_id = event.message.text.split(' ')[-1].replace('#', '').replace('.', '')
        order = fpbot.funpay_account.get_order(review_order_id)
        review = order.review
        
        if order.buyer_username != fpbot.funpay_account.username:
            fpbot.log_new_review(order.review)
            if fpbot.config["funpay"]["tg_logging"]["enabled"] and fpbot.config["funpay"]["tg_logging"]["events"]["new_review"]:
                asyncio.run_coroutine_threadsafe(
                    get_telegram_bot().log_event(
                        text=log_text(f'✨💬 Новый отзыв на заказ <a href="https://funpay.com/orders/{review_order_id}/">#{review_order_id}</a>', f"<b>┏ Оценка:</b> {'⭐' * review.stars}\n<b>┣ Оставил:</b> {review.author}\n<b>┗ Текст:</b> {review.text}"),
                        kb=log_new_review_kb(event.message.chat_name, review_order_id)
                    ), 
                    get_telegram_bot_loop()
                )

            if fpbot.config["funpay"]["auto_reviews_replies"]["enabled"]:
                fpbot.funpay_account.send_review(
                    order_id=review_order_id, 
                    text=fpbot.msg("order_review_reply", review_date=datetime.now().strftime("%d.%m.%Y"), order_title=order.title, order_amount=order.amount, order_price=order.sum)
                )

    async def _on_new_message(fpbot: FunPayBot, event: NewMessageEvent):
        this_chat = fpbot.funpay_account.get_chat_by_name(event.message.chat_name, True)
        if event.message.type is MessageTypes.NEW_FEEDBACK:
            return await FunPayBot._on_new_review(fpbot, event)
            
        fpbot.log_new_message(event.message)
        if fpbot.config["funpay"]["tg_logging"]["enabled"] and (fpbot.config["funpay"]["tg_logging"]["events"]["new_user_message"] or fpbot.config["funpay"]["tg_logging"]["events"]["new_system_message"]):
            if event.message.author != fpbot.funpay_account.username:
                do = False
                if fpbot.config["funpay"]["tg_logging"]["events"]["new_user_message"] and event.message.author.lower() != "funpay": do = True 
                if fpbot.config["funpay"]["tg_logging"]["events"]["new_system_message"] and event.message.author.lower() == "funpay": do = True 
                if do:
                    text = f"<b>{event.message.author}:</b> "
                    text += event.message.text or ""
                    text += f'<b><a href="{event.message.image_link}">{event.message.image_name}</a></b>' if event.message.image_link else ""
                    asyncio.run_coroutine_threadsafe(
                        get_telegram_bot().log_event(
                            text=log_text(f'💬 Новое сообщение в <a href="https://funpay.com/chat/?node={event.message.chat_id}">чате</a>', text.strip()),
                            kb=log_new_mess_kb(event.message.chat_name)
                        ), 
                        get_telegram_bot_loop()
                    )

        if event.message.author == this_chat.name:
            if this_chat.name not in fpbot.initialized_users:
                if event.message.type is MessageTypes.NON_SYSTEM:
                    fpbot.send_message(this_chat.id, fpbot.msg("first_message", username=event.message.author))
                fpbot.initialized_users.append(this_chat.name)
            
            if fpbot.config["funpay"]["custom_commands"]["enabled"]:
                if event.message.text.lower() in [key.lower() for key in fpbot.custom_commands.keys()]:
                    message = "\n".join(fpbot.custom_commands[event.message.text])
                    fpbot.send_message(this_chat.id, message)

            if str(event.message.text).lower() == "!команды" or str(event.message.text).lower() == "!commands":
                fpbot.send_message(this_chat.id, fpbot.msg("cmd_commands"))
            elif str(event.message.text).lower() == "!продавец" or str(event.message.text).lower() == "!seller":
                asyncio.run_coroutine_threadsafe(
                    get_telegram_bot().call_seller(event.message.author, this_chat.id), 
                    get_telegram_bot_loop()
                )
                fpbot.send_message(this_chat.id, fpbot.msg("cmd_seller"))

    async def _on_new_order(fpbot: FunPayBot, event: NewOrderEvent):
        if event.order.buyer_username != fpbot.funpay_account.username:
            this_chat = fpbot.funpay_account.get_chat_by_name(event.order.buyer_username, True)
            
            fpbot.log_new_order(event.order)
            if fpbot.config["funpay"]["tg_logging"]["enabled"] and fpbot.config["funpay"]["tg_logging"]["events"]["new_order"]:
                asyncio.run_coroutine_threadsafe(
                    get_telegram_bot().log_event(
                        text=log_text(f'📋 Новый заказ <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a>', f"<b>┏ Покупатель:</b> {event.order.buyer_username}\n<b>┣ Товар:</b> {event.order.description}\n<b>┣ Количество:</b> {event.order.amount}\n<b>┗ Сумма:</b> {event.order.price} {fpbot.funpay_account.currency.name}"),
                        kb=log_new_order_kb(this_chat.name, event.order.id)
                    ), 
                    get_telegram_bot_loop()
                )

            fpbot.send_message(this_chat.id, fpbot.msg("new_order", order_id=event.order.id, order_title=event.order.description, order_amount=event.order.amount))
            if fpbot.config["funpay"]["auto_deliveries"]["enabled"]:
                lot = fpbot.get_lot_by_order_title(event.order.description, event.order.subcategory)
                if lot and str(getattr(lot, "id")) in fpbot.auto_deliveries.keys():
                    fpbot.send_message(this_chat.id, "\n".join(fpbot.auto_deliveries[str(lot.id)]))

    async def _on_order_status_changed(fpbot: FunPayBot, event: OrderStatusChangedEvent):
        if event.order.buyer_username != fpbot.funpay_account.username:
            this_chat = fpbot.funpay_account.get_chat_by_name(event.order.buyer_username, True)
            status_frmtd = "Неизвестный"
            if event.order.status is OrderStatuses.PAID: status_frmtd = "Оплачен"
            elif event.order.status is OrderStatuses.CLOSED: status_frmtd = "Закрыт"
            elif event.order.status is OrderStatuses.REFUNDED: status_frmtd = "Возврат"
            fpbot.log_order_status_changed(event.order, status_frmtd)
            
            if fpbot.config["funpay"]["tg_logging"]["enabled"] and fpbot.config["funpay"]["tg_logging"]["events"]["order_status_changed"]:
                asyncio.run_coroutine_threadsafe(
                    get_telegram_bot().log_event(
                        text=log_text(f'🔄️📋 Статус заказа <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a> изменился', f"<b>Новый статус:</b> {status_frmtd}")
                    ), 
                    get_telegram_bot_loop()
                )
            if event.order.status is OrderStatuses.CLOSED:
                fpbot.stats.orders_completed += 1
                fpbot.stats.earned_money += round(event.order.price, 2)
                fpbot.send_message(this_chat.id, fpbot.msg("order_confirmed", order_id=event.order.id, order_title=event.order.description, order_amount=event.order.amount))
            elif event.order.status is OrderStatuses.REFUNDED:
                fpbot.stats.orders_refunded += 1
                fpbot.send_message(this_chat.id, fpbot.msg("order_refunded", order_id=event.order.id, order_title=event.order.description, order_amount=event.order.amount))


    async def run_bot(self):
        self.logger.info(f"{Fore.GREEN}FunPay бот запущен и активен")
        self.logger.info("")
        self.logger.info(f"{Fore.CYAN}───────────────────────────────────────")
        self.logger.info(f"{Fore.CYAN}Информация об аккаунте:")
        self.logger.info(f" · ID: {Fore.LIGHTWHITE_EX}{self.funpay_account.id}")
        self.logger.info(f" · Никнейм: {Fore.LIGHTWHITE_EX}{self.funpay_account.username}")
        self.logger.info(f" · Баланс: {Fore.LIGHTWHITE_EX}{self.funpay_account.total_balance} {self.funpay_account.currency.name if self.funpay_account.currency != Currency.UNKNOWN else 'RUB'}")
        self.logger.info(f" · Активные продажи: {Fore.LIGHTWHITE_EX}{self.funpay_account.active_sales}")
        self.logger.info(f" · Активные покупки: {Fore.LIGHTWHITE_EX}{self.funpay_account.active_purchases}")
        self.logger.info(f"{Fore.CYAN}───────────────────────────────────────")
        self.logger.info("")
        if self.config["funpay"]["api"]["proxy"]:
            user, password = self.config["funpay"]["api"]["proxy"].split("@")[0].split(":") if "@" in self.config["funpay"]["api"]["proxy"] else self.config["funpay"]["api"]["proxy"]
            ip, port = self.config["funpay"]["api"]["proxy"].split("@")[1].split(":") if "@" in self.config["funpay"]["api"]["proxy"] else self.config["funpay"]["api"]["proxy"]
            ip = ".".join([("*" * len(nums)) if i >= 3 else nums for i, nums in enumerate(ip.split("."), start=1)])
            port = f"{port[:3]}**"
            user = f"{user[:3]}*****" if user else "Без авторизации"
            password = f"{password[:3]}*****" if password else "Без авторизации"
            self.logger.info(f"{Fore.CYAN}───────────────────────────────────────")
            self.logger.info(f"{Fore.CYAN}Информация о прокси:")
            self.logger.info(f" · IP: {Fore.LIGHTWHITE_EX}{ip}:{port}")
            self.logger.info(f" · Юзер: {Fore.LIGHTWHITE_EX}{user}")
            self.logger.info(f" · Пароль: {Fore.LIGHTWHITE_EX}{password}")
            self.logger.info(f"{Fore.CYAN}───────────────────────────────────────")
            self.logger.info("")
            
        add_bot_event_handler("ON_FUNPAY_BOT_INIT", FunPayBot._on_funpay_bot_init, 0)
        add_funpay_event_handler(EventTypes.NEW_MESSAGE, FunPayBot._on_new_message, 0)
        add_funpay_event_handler(EventTypes.NEW_ORDER, FunPayBot._on_new_order, 0) 
        add_funpay_event_handler(EventTypes.ORDER_STATUS_CHANGED, FunPayBot._on_order_status_changed, 0)

        async def runner_loop():
            runner = Runner(self.funpay_account)
            for event in runner.listen(requests_delay=self.config["funpay"]["api"]["runner_requests_delay"]):
                await call_funpay_event(event.type, [self, event])

        run_async_in_thread(runner_loop)
        self.logger.info(f"Слушатель событий запущен")

        await call_bot_event("ON_FUNPAY_BOT_INIT", [self])