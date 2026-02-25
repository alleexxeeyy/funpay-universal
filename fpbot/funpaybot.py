from __future__ import annotations
import asyncio
import time
from datetime import datetime, timedelta
from typing import  Optional
import time
from threading import Thread
from colorama import Fore
import textwrap
import shutil
import re

from FunPayAPI import Account, Runner
from FunPayAPI.common.exceptions import *
from FunPayAPI.common.enums import *
from FunPayAPI.updater.events import *

from __init__ import ACCENT_COLOR, VERSION
from core.utils import (
    set_title, 
    shutdown, 
    run_async_in_thread
)
from core.handlers import (
    add_bot_event_handler, 
    add_funpay_event_handler, 
    call_bot_event, 
    call_funpay_event
)
from settings import DATA, Settings as sett
from data import Data as data
from logging import getLogger
from tgbot.telegrambot import get_telegram_bot, get_telegram_bot_loop
from tgbot.templates import (
    log_text, 
    log_new_mess_kb, 
    log_new_order_kb, 
    log_new_review_kb
)
from support_api import FunPaySupportAPI

from .stats import get_stats, set_stats


def get_funpay_bot() -> FunPayBot | None:
    if hasattr(FunPayBot, "instance"):
        return getattr(FunPayBot, "instance")


class FunPayBot:
    def __new__(cls, *args, **kwargs) -> FunPayBot:
        if not hasattr(cls, "instance"):
            cls.instance = super(FunPayBot, cls).__new__(cls)
        return getattr(cls, "instance")
    
    def __init__(self):
        self.logger = getLogger("universal.funpay")

        self.config = sett.get("config")
        self.messages = sett.get("messages")
        self.custom_commands = sett.get("custom_commands")
        self.auto_deliveries = sett.get("auto_deliveries")
        self.auto_raise_lots = sett.get("auto_raise_lots")

        self.initialized_users = data.get("initialized_users")
        self.categories_raise_time = data.get("categories_raise_time")
        self.latest_events_times = data.get("latest_events_times")
        self.stats = get_stats()

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
        
        
    def msg(self, message_name: str, messages_config_name: str = "messages", 
            messages_data: dict = DATA, **kwargs) -> str | None:
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
            return msg
        except:
            pass
        return f"Не удалось получить сообщение {message_name}"
    
    def get_lot_by_title(self, title: str, subcategory: types.SubCategory | None = None,
                         subcategory_id: int | None = None, max_attempts: int = 3) -> types.LotShortcut:
        """
        Получает лот по названию.

        :param title: Название лота.
        :type title: `str`

        :param subcategory: Подкатегория лота, _опционально_.
        :type subcategory: `FunPayAPI.types.SubCategory` or `None`

        :param subcategory_id: ID подкатегории лота, _опционально_.
        :type subcategory_id: `FunPayAPI.types.SubCategory` or `None`

        :return: Объект лота.
        :rtype: `FunPayAPI.types.LotShortcut`
        """
        subcat_id = subcategory_id if subcategory_id else subcategory.id if subcategory else None
        
        if any((subcategory, subcategory_id)):
            lots = self.account.get_my_subcategory_lots(subcat_id)
        else:
            user = self.account.get_user(self.account.id)
            lots = user.get_lots()
        cleaned_title = (" ".join(re.sub(r"[^\w\s]", " ", title).split())).lower()

        for lot in lots:
            if subcat_id and lot.subcategory.id != subcat_id:
                continue

            cleaned_lot_title = (" ".join(re.sub(r"[^\w\s]", " ", lot.title).split())).lower()
            if (
                cleaned_lot_title in cleaned_title
                or cleaned_title in cleaned_lot_title
                or cleaned_lot_title == cleaned_title
            ):
                return lot
            
        self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось получить лот по названию «{title}»")
    
    def get_lot_by_order_title(self, title: str, subcategory: types.SubCategory | None = None,
                               subcategory_id: int | None = None) -> types.LotShortcut:
        """Эквивалент метода `get_lot_by_title()`"""
        return self.get_lot_by_title(title, subcategory, subcategory_id)

    def send_message(self, chat_id: int | str, text: Optional[str] = None, chat_name: Optional[str] = None,
                     interlocutor_id: Optional[int] = None, image_id: Optional[int] = None, add_to_ignore_list: bool = True,
                     update_last_saved_message: bool = False, leave_as_unread: bool = False, exclude_watermark: bool = False, 
                     max_attempts: int = 3) -> types.Message | None:
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

        :param exclude_watermark: Пропустить и не использовать водяной знак под сообщением?
        :type exclude_watermark: `bool`

        :return: Экземпляр отправленного сообщения или None, если сообщение не отправилось.
        :rtype: :class:`FunPayAPI.types.Message` or `None`
        """
        if not text and not image_id:
            return None
        for _ in range(max_attempts):
            try:
                if (
                    text 
                    and self.config["funpay"]["watermark"]["enabled"]
                    and self.config["funpay"]["watermark"]["value"]
                    and not exclude_watermark
                ):
                    text += f"\n{self.config['funpay']['watermark']['value']}"
                mess = self.account.send_message(chat_id, text, chat_name, interlocutor_id, 
                                                        image_id, add_to_ignore_list, 
                                                        update_last_saved_message, leave_as_unread)
                return mess
            except (MessageNotDeliveredError, RequestFailedError) as e:
                continue
            except Exception as e:
                text = text.replace('\n', ' ').strip()
                self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при отправке сообщения {Fore.WHITE}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.WHITE}{chat_id} {Fore.LIGHTRED_EX}: {Fore.WHITE}{e}")
                return None
        text = text.replace('\n', ' ').strip()
        self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось отправить сообщение {Fore.WHITE}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.WHITE}{chat_id} {Fore.LIGHTRED_EX}")

    
    def refresh_account(self):
        self.account = self.funpay_account = (self.account or self.funpay_account).get()

    def check_banned(self):
        user = self.account.get_user(self.account.id)
        if user.banned:
            self.logger.critical(f"")
            self.logger.critical(f"{Fore.LIGHTRED_EX}Ваш FunPay аккаунт был заблокирован! К сожалению, я не могу продолжать работу на заблокированном аккаунте...")
            self.logger.critical(f"Напишите в тех. поддержку FunPay, чтобы узнать причину бана и как можно быстрее решить эту проблему.")
            self.logger.critical(f"")
            shutdown()

    def raise_lots(self) -> int:
        try:
            next_time = 14400
            raised_categories = []
            profile = self.account.get_user(self.account.id)
            for subcategory in list(profile.get_sorted_lots(2).keys()):
                category = subcategory.category
                if str(subcategory.id) in self.categories_raise_time:
                    if datetime.now() < datetime.fromisoformat(self.categories_raise_time[str(subcategory.id)]):
                        continue
                
                try:
                    self.account.raise_lots(category.id)
                    raised_categories.append(category.name)
                    time.sleep(0.5)
                    # Если удалось поднять эту категорию, то снова отправляем запрос на её поднятие,
                    # чтобы словить ошибку и получить время её следующего поднятия
                    self.account.raise_lots(category.id)
                except RaiseError as e:
                    if e.wait_time is not None:
                        self.categories_raise_time[str(subcategory.id)] = (datetime.now() + timedelta(seconds=e.wait_time)).isoformat()
                    else:
                        del self.categories_raise_time[str(subcategory.id)]
                time.sleep(1)

            for category in self.categories_raise_time:
                current_next_time = (datetime.fromisoformat(self.categories_raise_time[category]) - datetime.now()).seconds
                next_time = current_next_time if current_next_time < next_time else next_time
            if len(raised_categories) > 0:
                self.logger.info(f"{Fore.YELLOW}Подняты лоты категорий: {Fore.LIGHTWHITE_EX}{f'{Fore.WHITE}, {Fore.LIGHTWHITE_EX}'.join(map(str, raised_categories))}")
            return next_time
        except Exception as e:
            self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при поднятии лотов: {Fore.WHITE}{e}")
            return 0

    def create_tickets(self):
        last_time = datetime.now()
        self.latest_events_times["create_tickets"] = last_time.isoformat()
        data.set("latest_events_times", self.latest_events_times)
        support_api = FunPaySupportAPI(self.account).get()
        self.logger.info(f"{Fore.WHITE}Создаю тикеты в тех. поддержку на закрытие заказов...")

        def calculate_orders(all_orders, orders_per_ticket=25):
            return [all_orders[i:i+orders_per_ticket] for i in range(0, len(all_orders), orders_per_ticket)]

        all_order_ids: list[str] = []
        next_start_from = None
        while len(all_order_ids) < self.account.active_sales:
            sales = self.account.get_sales(start_from=next_start_from, include_paid=True, include_closed=False, include_refunded=False)
            for sale in sales[1]:
                if sale.date + timedelta(seconds=self.config["funpay"]["auto_tickets"]["min_order_age"]) <= datetime.now():
                    if sale.id not in all_order_ids:
                        all_order_ids.append(sale.id)
            next_start_from = sales[0]
            if not next_start_from:
                break
            time.sleep(0.5)
        
        order_ids = calculate_orders([order_id for order_id in all_order_ids], self.config["funpay"]["auto_tickets"]["orders_per_ticket"])
        ticketed_orders = []
        resp = {}
        for order_ids_per_ticket in order_ids:
            formatted_order_ids = ", ".join(order_ids_per_ticket)
            resp: dict = support_api.create_ticket(formatted_order_ids, f"Здравствуйте! Прошу подтвердить заказы, ожидающие подтверждения: {formatted_order_ids}. С уважением, {self.account.username}!")
            if resp.get("error") or not resp.get("action") or resp["action"]["message"] != "Ваша заявка отправлена.":
                break
            ticketed_orders.extend(order_ids_per_ticket)
            self.logger.info(f"{Fore.LIGHTWHITE_EX}{resp['action']['url'].split('/')[-1]} (https://support.funpay.com{resp['action']['url']}) {Fore.WHITE}— тикет создан для {Fore.LIGHTCYAN_EX}{len(order_ids_per_ticket)} заказов")
        self.latest_events_times["create_tickets"] = datetime.now().isoformat()
        
        if len(ticketed_orders) == 0:
            self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось создать тикеты в тех. поддержку по причине: {Fore.WHITE}{resp.get('error', 'Неизвестная ошибка.')}")
        elif len(ticketed_orders) >= 0:
            self.logger.info(f"{ACCENT_COLOR}Создал {Fore.LIGHTCYAN_EX}{len(calculate_orders(ticketed_orders))} тикета(-ов) в тех. поддержку {ACCENT_COLOR}на закрытие {Fore.LIGHTCYAN_EX}{len(ticketed_orders)} заказов")
        next_time = last_time + timedelta(seconds=self.config["funpay"]["auto_tickets"]["interval"])
        
        dm = next_time.strftime('%d.%m в %H:%M')
        hm = next_time.strftime('%H:%M')
        self.logger.info(
            f"Следующая попытка будет "
            f"{Fore.LIGHTWHITE_EX}{dm}{Fore.WHITE} в {Fore.LIGHTWHITE_EX}{hm}"
        )

    
    def log_new_message(self, message: types.Message):
        ch_header = f"Новое сообщение в чате с {message.chat_name}:"
        self.logger.info(f"{ACCENT_COLOR}{ch_header.replace(message.chat_name, f'{Fore.LIGHTCYAN_EX}{message.chat_name}')}")
        self.logger.info(f"{ACCENT_COLOR}│ {Fore.LIGHTWHITE_EX}{message.author}:")
        max_width = shutil.get_terminal_size((80, 20)).columns - 40
        longest_line_len = 0
        text = ""
        if message.text is not None: text = message.text
        elif message.image_link is not None: text = f"{Fore.LIGHTMAGENTA_EX}Изображение {Fore.WHITE}({message.image_link})"
        for raw_line in text.split("\n"):
            if not raw_line.strip():
                self.logger.info(f"{ACCENT_COLOR}│")
                continue
            wrapped_lines = textwrap.wrap(raw_line, width=max_width)
            for wrapped in wrapped_lines:
                self.logger.info(f"{ACCENT_COLOR}│ {Fore.WHITE}{wrapped}")
                longest_line_len = max(longest_line_len, len(wrapped.strip()))
        underline_len = max(len(ch_header)-1, longest_line_len+2)
        self.logger.info(f"{ACCENT_COLOR}└{'─'*underline_len}")
    
    def log_new_order(self, order: types.OrderShortcut):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новый заказ #{order.id}:")
        self.logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{order.buyer_username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{order.description}")
        self.logger.info(f" · Количество: {Fore.LIGHTWHITE_EX}{order.amount or '?'}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{order.price} {self.account.currency.name}")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
    
    def log_order_status_changed(self, order: types.OrderShortcut, status_frmtd: str = "Неизвестный"):
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")
        self.logger.info(f"{Fore.WHITE}Статус заказа {Fore.LIGHTWHITE_EX}#{order.id} {Fore.WHITE}изменился:")
        self.logger.info(f" · Статус: {Fore.LIGHTWHITE_EX}{status_frmtd}")
        self.logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{order.buyer_username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{order.description}")
        self.logger.info(f" · Количество: {Fore.LIGHTWHITE_EX}{order.amount or order.parse_amount() or 0}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{order.price} {self.account.currency.name}")
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")
    
    def log_new_review(self, review: types.Review):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новый отзыв по заказу #{review.order_id}:")
        self.logger.info(f" · Оценка: {Fore.LIGHTYELLOW_EX}{'★' * review.stars or 5} ({review.stars or 5})")
        self.logger.info(f" · Текст: {Fore.LIGHTWHITE_EX}{review.text}")
        self.logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{review.author}")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")


    def _event_datetime(self, latest_event_time, event_interval):
        if latest_event_time:
            return (
                datetime.fromisoformat(latest_event_time) 
                + timedelta(seconds=event_interval)
            )
        else:
            return datetime.now()

    async def _on_funpay_bot_init(self):
        self.stats.bot_launch_time = datetime.now()
        
        def check_config_loop():
            while True:
                cur_name = self.account.currency.name if self.account.currency != Currency.UNKNOWN else 'RUB'
                set_title(
                    f"FunPay Universal v{VERSION} | {self.account.username}: "
                    f"{self.account.total_balance} {cur_name}. "
                    f"Активных заказов: {self.account.active_sales}"
                )
                
                if self.config != sett.get("config"):
                    self.config = sett.get("config")
                if self.messages != sett.get("messages"):
                    self.messages = sett.get("messages")
                if self.custom_commands != sett.get("custom_commands"):
                    self.custom_commands = sett.get("custom_commands")
                if self.auto_deliveries != sett.get("auto_deliveries"):
                    self.auto_deliveries = sett.get("auto_deliveries")
                if self.auto_raise_lots != sett.get("auto_raise_lots"):
                    self.auto_raise_lots = sett.get("auto_raise_lots")

                if self.initialized_users != data.get("initialized_users"): 
                    data.set("initialized_users", self.initialized_users)
                if self.categories_raise_time != data.get("categories_raise_time"): 
                    data.set("categories_raise_time", self.categories_raise_time)
                if self.latest_events_times != data.get("latest_events_times"): 
                    self.latest_events_times = data.get("latest_events_times")
                
                if self.stats != get_stats(): 
                    set_stats(self.stats)
                
                time.sleep(3)

        def refresh_account_loop():
            while True:
                self.refresh_account()
                time.sleep(2400)

        def check_banned_loop():
            while True:
                self.check_banned()
                time.sleep(900)

        def raise_lots_loop():            
            while True:
                if self.config["funpay"]["auto_raise_lots"]["enabled"]:
                    seconds = self.raise_lots()
                    time.sleep(seconds)
                time.sleep(3)

        def create_tickets_loop():
            while True:
                if (
                    self.config["funpay"]["auto_tickets"]["enabled"]
                    and datetime.now() >= self._event_datetime(
                        self.latest_events_times["create_tickets"], 
                        self.config["funpay"]["auto_tickets"]["interval"]
                    )
                ):
                    self.create_tickets()
                time.sleep(3)

        Thread(target=check_config_loop, daemon=True).start()
        Thread(target=refresh_account_loop, daemon=True).start()    
        Thread(target=check_banned_loop, daemon=True).start()
        Thread(target=raise_lots_loop, daemon=True).start()
        Thread(target=create_tickets_loop, daemon=True).start()
    
    async def _on_new_review(self, event: NewMessageEvent):
        if event.message.author == self.account.username:
            return
        review_order_id = event.message.text.split(' ')[-1].replace('#', '').replace('.', '')
        order = self.account.get_order(review_order_id)
        review = order.review
        
        self.log_new_review(order.review)
        if (
            self.config["funpay"]["tg_logging"]["enabled"] 
            and self.config["funpay"]["tg_logging"]["events"]["new_review"]
        ):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().log_event(
                    text=log_text(
                        f'<b>✨💬 Новый отзыв на заказ <a href="https://funpay.com/orders/{review_order_id}/">#{review_order_id}</a></b>', 
                        f"· Оценка: {'⭐' * review.stars}\n· Оставил: {review.author}\n· Текст: {review.text}"
                    ),
                    kb=log_new_review_kb(event.message.chat_name, review_order_id)
                ), 
                get_telegram_bot_loop()
            )

        if (
            order.buyer_id != self.account.id
            and self.config["funpay"]["auto_review_replies"]["enabled"]
        ):
            self.account.send_review(
                order_id=review_order_id, 
                text=self.msg("order_review_reply", 
                    review_date=datetime.now().strftime("%d.%m.%Y"), 
                    order_title=order.short_description or "?", 
                    order_amount=order.amount or "?", 
                    order_price=order.sum or "?"
                )
            )

    async def _on_new_message(self, event: NewMessageEvent):
        if event.message.type is MessageTypes.NEW_FEEDBACK:
            return await FunPayBot._on_new_review(self, event)
        self.log_new_message(event.message)

        if event.message.author == self.account.username:
            return
        this_chat = self.account.get_chat_by_name(event.message.chat_name, True)

        if (
            self.config["funpay"]["tg_logging"]["enabled"] 
            and (self.config["funpay"]["tg_logging"]["events"]["new_user_message"] 
            or self.config["funpay"]["tg_logging"]["events"]["new_system_message"])
        ):
            do = False
            if self.config["funpay"]["tg_logging"]["events"]["new_user_message"] and event.message.author.lower() != "funpay": do = True 
            if self.config["funpay"]["tg_logging"]["events"]["new_system_message"] and event.message.author.lower() == "funpay": do = True 
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

        if event.message.text is None:
            return
        if this_chat.name not in self.initialized_users:
            if event.message.type is MessageTypes.NON_SYSTEM:
                self.send_message(this_chat.id, self.msg("first_message", username=event.message.author))
            self.initialized_users.append(this_chat.name)

        if str(event.message.text).lower() in ("!команды", "!commands"):
            self.send_message(this_chat.id, self.msg("cmd_commands"))
        elif str(event.message.text).lower() in ("!продавец", "!seller"):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().call_seller(event.message.author, this_chat.id), 
                get_telegram_bot_loop()
            )
            self.send_message(this_chat.id, self.msg("cmd_seller"))
        elif self.config["funpay"]["custom_commands"]["enabled"]:
            if event.message.text.lower() in [key.lower() for key in self.custom_commands.keys()]:
                message = "\n".join(self.custom_commands[event.message.text])
                self.send_message(this_chat.id, message)

    async def _on_new_order(self, event: NewOrderEvent):
        if event.order.buyer_username == self.account.username:
            return
        this_chat = self.account.get_chat_by_name(event.order.buyer_username, True)
        
        self.log_new_order(event.order)
        if (
            self.config["funpay"]["tg_logging"]["enabled"] 
            and self.config["funpay"]["tg_logging"]["events"]["new_order"]
        ):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().log_event(
                    text=log_text(
                        f'<b>📋 Новый заказ <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a></b>', 
                        f"· Покупатель: {event.order.buyer_username}\n· Товар: {event.order.description}\n· Количество: {event.order.amount}\n· Сумма: {event.order.price} {self.account.currency.name}"
                    ),
                    kb=log_new_order_kb(this_chat.name, event.order.id)
                ), 
                get_telegram_bot_loop()
            )

        self.send_message(this_chat.id, self.msg("new_order", 
            order_id=event.order.id, 
            order_title=event.order.description, 
            order_amount=event.order.amount
        ))
        
        if self.config["funpay"]["auto_deliveries"]["enabled"]:
            lot = self.get_lot_by_order_title(event.order.description, event.order.subcategory)
            if lot and str(getattr(lot, "id")) in self.auto_deliveries.keys():
                self.send_message(this_chat.id, "\n".join(self.auto_deliveries[str(lot.id)]))

    async def _on_order_status_changed(self, event: OrderStatusChangedEvent):
        if event.order.buyer_username == self.account.username:
            return
        this_chat = self.account.get_chat_by_name(event.order.buyer_username, True)
        
        status_frmtd = "Неизвестный"
        if event.order.status is OrderStatuses.PAID: status_frmtd = "Оплачен"
        elif event.order.status is OrderStatuses.CLOSED: status_frmtd = "Закрыт"
        elif event.order.status is OrderStatuses.REFUNDED: status_frmtd = "Возврат"

        self.log_order_status_changed(event.order, status_frmtd)
        if (
            self.config["funpay"]["tg_logging"]["enabled"] 
            and self.config["funpay"]["tg_logging"]["events"]["order_status_changed"]
        ):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().log_event(
                    text=log_text(
                        f'<b>🔄️📋 Статус заказа <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a> изменился</b>', 
                        f"· Новый статус: {status_frmtd}"
                    )
                ), 
                get_telegram_bot_loop()
            )

        if event.order.status is OrderStatuses.CLOSED:
            self.stats.orders_completed += 1
            self.stats.earned_money += round(event.order.price, 2)
            self.send_message(this_chat.id, self.msg("order_confirmed", 
                order_id=event.order.id, 
                order_title=event.order.description, 
                order_amount=event.order.amount
            ))
        elif event.order.status is OrderStatuses.REFUNDED:
            self.stats.orders_refunded += 1
            self.send_message(this_chat.id, self.msg("order_refunded", 
                order_id=event.order.id, 
                order_title=event.order.description, 
                order_amount=event.order.amount
            ))


    async def run_bot(self):
        self.logger.info("")
        self.logger.info(f"{ACCENT_COLOR}───────────────────────────────────────")
        self.logger.info(f"{ACCENT_COLOR}Информация об аккаунте:")
        self.logger.info(f" · ID: {Fore.LIGHTWHITE_EX}{self.account.id}")
        self.logger.info(f" · Никнейм: {Fore.LIGHTWHITE_EX}{self.account.username}")
        self.logger.info(f" · Баланс: {Fore.LIGHTWHITE_EX}{self.account.total_balance} {self.account.currency.name if self.account.currency != Currency.UNKNOWN else 'RUB'}")
        self.logger.info(f" · Активные продажи: {Fore.LIGHTWHITE_EX}{self.account.active_sales}")
        self.logger.info(f" · Активные покупки: {Fore.LIGHTWHITE_EX}{self.account.active_purchases}")
        self.logger.info(f"{ACCENT_COLOR}───────────────────────────────────────")
        self.logger.info("")
        if self.config["funpay"]["api"]["proxy"]:
            user, password = self.config["funpay"]["api"]["proxy"].split("@")[0].split(":") if "@" in self.config["funpay"]["api"]["proxy"] else self.config["funpay"]["api"]["proxy"]
            ip, port = self.config["funpay"]["api"]["proxy"].split("@")[1].split(":") if "@" in self.config["funpay"]["api"]["proxy"] else self.config["funpay"]["api"]["proxy"]
            ip = ".".join([("*" * len(nums)) if i >= 3 else nums for i, nums in enumerate(ip.split("."), start=1)])
            port = f"{port[:3]}**"
            user = f"{user[:3]}*****" if user else "Без авторизации"
            password = f"{password[:3]}*****" if password else "Без авторизации"
            self.logger.info(f"{ACCENT_COLOR}───────────────────────────────────────")
            self.logger.info(f"{ACCENT_COLOR}Информация о прокси:")
            self.logger.info(f" · IP: {Fore.LIGHTWHITE_EX}{ip}:{port}")
            self.logger.info(f" · Юзер: {Fore.LIGHTWHITE_EX}{user}")
            self.logger.info(f" · Пароль: {Fore.LIGHTWHITE_EX}{password}")
            self.logger.info(f"{ACCENT_COLOR}───────────────────────────────────────")
            self.logger.info("")
            
        add_bot_event_handler("ON_FUNPAY_BOT_INIT", FunPayBot._on_funpay_bot_init, 0)
        add_funpay_event_handler(EventTypes.NEW_MESSAGE, FunPayBot._on_new_message, 0)
        add_funpay_event_handler(EventTypes.NEW_ORDER, FunPayBot._on_new_order, 0) 
        add_funpay_event_handler(EventTypes.ORDER_STATUS_CHANGED, FunPayBot._on_order_status_changed, 0)

        async def runner_loop():
            runner = Runner(self.account)
            for event in runner.listen(requests_delay=self.config["funpay"]["api"]["runner_requests_delay"]):
                await call_funpay_event(event.type, [self, event])

        run_async_in_thread(runner_loop)
        self.logger.info(f"{Fore.YELLOW}FunPay бот запущен и активен")

        await call_bot_event("ON_FUNPAY_BOT_INIT", [self])