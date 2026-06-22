from __future__ import annotations
import asyncio
import time
import pytz
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
    log_new_review_kb,
    destroy_kb
)
from support_api import FunPaySupportAPI


logger = getLogger("universal.funpay")


def get_funpay_bot() -> FunPayBot | None:
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

        self.initialized_users = data.get("initialized_users")
        self.categories_raise_time = data.get("categories_raise_time")
        self.cached_orders = data.get("cached_orders")

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
            
        logger.error(f"{Fore.LIGHTRED_EX}Не удалось получить лот по названию «{title}»")
    
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
                mess = self.account.send_message(
                    chat_id, text, chat_name, interlocutor_id, 
                    image_id, add_to_ignore_list, 
                    update_last_saved_message, leave_as_unread
                )
                return mess
            except (MessageNotDeliveredError, RequestFailedError) as e:
                continue
            except Exception as e:
                text = text.replace('\n', ' ').strip()
                logger.error(f"{Fore.LIGHTRED_EX}Ошибка при отправке сообщения {Fore.WHITE}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.WHITE}{chat_id} {Fore.LIGHTRED_EX}: {Fore.WHITE}{e}")
                return None
        text = text.replace('\n', ' ').strip()
        logger.error(f"{Fore.LIGHTRED_EX}Не удалось отправить сообщение {Fore.WHITE}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.WHITE}{chat_id} {Fore.LIGHTRED_EX}")


    def log_to_tg(self, text, kb=None):
        asyncio.run_coroutine_threadsafe(
            get_telegram_bot().log_event(text=text, kb=kb), 
            get_telegram_bot_loop()
        )

    
    def refresh_account(self):
        self.account = self.funpay_account = (self.account or self.funpay_account).get()

    def check_banned(self):
        try: 
            banned = self.account.get_user(self.account.id).banned
        except AttributeError: 
            banned = True
            
        if banned:
            logger.critical(f"")
            logger.critical(f"{Fore.LIGHTRED_EX}Ваш FunPay аккаунт был заблокирован! К сожалению, я не могу продолжать работу на заблокированном аккаунте...")
            logger.critical(f"Напишите в тех. поддержку FunPay, чтобы узнать причину бана и как можно быстрее решить эту проблему.")
            logger.critical(f"")
            shutdown()

    def raise_lots(self) -> int:
        try:
            next_time = 14400
            raised_categories = []
            profile = self.account.get_user(self.account.id)

            subcats = list(profile.get_sorted_lots(2).keys())
            great_subcats = []
            for subcat in subcats:
                iso_dt = self.categories_raise_time.get(str(subcat.id))
                if not iso_dt or datetime.now() >= datetime.fromisoformat(iso_dt):
                    great_subcats.append(subcat)
            
            for subcat in great_subcats:
                try:
                    wait_time = self.account.raise_lots(subcat.category.id) or 14400
                    raised_categories.append(subcat.category.name)
                    time.sleep(1)
                except RaiseError as e:
                    if e.wait_time is not None:
                        wait_time = e.wait_time
                        logger.warning(
                            f"Категорию «{subcat.name}» "
                            f"можно будет поднять через {wait_time} сек."
                        )
                    else:
                        error_text = e.error_message or "неизвестная ошибка"
                        self.categories_raise_time.pop(str(subcat.id), None)
                        logger.error(
                            f"{Fore.LIGHTRED_EX}Ошибка поднятия категории "
                            f"«{subcat.name}»: {Fore.LIGHTWHITE_EX}{error_text}"
                        )
                        time.sleep(10)
                        continue

                self.categories_raise_time[str(subcat.id)] = (
                    datetime.now() + timedelta(seconds=wait_time)
                ).isoformat()

            for iso_dt in self.categories_raise_time.values():
                current_next_time = max(0, int((datetime.fromisoformat(iso_dt) - datetime.now()).total_seconds()))
                next_time = current_next_time if current_next_time < next_time else next_time
           
            if len(raised_categories) > 0:
                raised_frmtd = f"{Fore.WHITE}, {Fore.LIGHTWHITE_EX}".join(map(str, raised_categories))
                logger.info(
                    f"{Fore.YELLOW}Подняты категории: {Fore.LIGHTWHITE_EX}{raised_frmtd}"
                )
            
            return next_time
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при поднятии лотов: {Fore.WHITE}{e}")
            return 0

    def create_ticket(self):
        last_time = datetime.now()
        self.config["funpay"]["auto_tickets"]["last_time"] = last_time.isoformat()
        sett.set("config", self.config)
        
        support_api = FunPaySupportAPI(self.account).get()
        logger.info(f"{Fore.WHITE}Создаю тикеты в тех. поддержку на закрытие заказов...")

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
        
        per_ticket = self.config["funpay"]["auto_tickets"]["orders_per_ticket"]
        order_ids = [id_ for id_ in all_order_ids][:per_ticket]
        resp = {}
        frmtd_order_ids = ", ".join(order_ids)
        
        resp = support_api.create_ticket(
            frmtd_order_ids, 
            f"Здравствуйте! Прошу подтвердить заказы, ожидающие подтверждения: {frmtd_order_ids}. С уважением, {self.account.username}!"
        )

        error = resp.get("error")
        action = resp.get("action")

        if not order_ids:
            error = "Нет подходящих заказов"
        
        if error or not action or resp["action"]["message"] != "Ваша заявка отправлена.":
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при создании тикетов в тех. поддержку: {Fore.WHITE}{error}")
            if (
                self.config["funpay"]["notifications"]["enabled"] 
                and self.config["funpay"]["notifications"]["events"]["ticket_created"]
            ):
                self.log_to_tg(
                    log_text(
                        f"❌ Ошибка при создании тикета в поддержку",
                        f"<blockquote>{error}</blockquote>"
                    ),
                    destroy_kb()
                )
            return False, "", 0, error
        
        url = f"https://support.funpay.com{action['url']}"
    
        logger.info(
            f"{Fore.YELLOW}Создал тикет на закрытие {Fore.LIGHTYELLOW_EX}{len(order_ids)} заказов "
            f"{Fore.WHITE}— {Fore.LIGHTWHITE_EX}{url}"
        )
        if (
            self.config["funpay"]["notifications"]["enabled"] 
            and self.config["funpay"]["notifications"]["events"]["new_review"]
        ):
            self.log_to_tg(
                log_text(f'📞 Создан <a href="{url}">тикет</a> на закрытие {len(order_ids)} заказов'),
                destroy_kb()
            )

        next_time = last_time + timedelta(seconds=self.config["funpay"]["auto_tickets"]["interval"])
        dm = next_time.strftime('%d.%m')
        hm = next_time.strftime('%H:%M')
        
        logger.info(
            f"Следующая попытка будет "
            f"{Fore.LIGHTWHITE_EX}{dm}{Fore.WHITE} в {Fore.LIGHTWHITE_EX}{hm}"
        )

        return True, url, len(order_ids), ""

    
    def log_new_message(self, message: types.Message):
        ch_header = f"Новое сообщение в чате с {message.chat_name}:"
        logger.info(f"{ACCENT_COLOR}{ch_header.replace(message.chat_name, f'{Fore.LIGHTCYAN_EX}{message.chat_name}')}")
        logger.info(f"{ACCENT_COLOR}│ {Fore.LIGHTWHITE_EX}{message.author}:")
        max_width = shutil.get_terminal_size((80, 20)).columns - 40
        longest_line_len = 0
        text = ""
        if message.text is not None: text = message.text
        elif message.image_link is not None: text = f"{Fore.LIGHTMAGENTA_EX}Изображение {Fore.WHITE}({message.image_link})"
        for raw_line in text.split("\n"):
            if not raw_line.strip():
                logger.info(f"{ACCENT_COLOR}│")
                continue
            wrapped_lines = textwrap.wrap(raw_line, width=max_width)
            for wrapped in wrapped_lines:
                logger.info(f"{ACCENT_COLOR}│ {Fore.WHITE}{wrapped}")
                longest_line_len = max(longest_line_len, len(wrapped.strip()))
        underline_len = max(len(ch_header)-1, longest_line_len+2)
        logger.info(f"{ACCENT_COLOR}└{'─'*underline_len}")
    
    def log_new_order(self, order: types.OrderShortcut):
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        logger.info(f"{Fore.YELLOW}Новый заказ #{order.id}:")
        logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{order.buyer_username}")
        logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{order.description}")
        logger.info(f" · Количество: {Fore.LIGHTWHITE_EX}{order.amount or '?'}")
        logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{order.price} {self.account.currency.name}")
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
    
    def log_order_status_changed(self, order: types.OrderShortcut, status_frmtd: str = "Неизвестный"):
        logger.info(f"{Fore.WHITE}───────────────────────────────────────")
        logger.info(f"{Fore.WHITE}Статус заказа {Fore.LIGHTWHITE_EX}#{order.id} {Fore.WHITE}изменился:")
        logger.info(f" · Статус: {Fore.LIGHTWHITE_EX}{status_frmtd}")
        logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{order.buyer_username}")
        logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{order.description}")
        logger.info(f" · Количество: {Fore.LIGHTWHITE_EX}{order.amount or order.parse_amount() or 0}")
        logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{order.price} {self.account.currency.name}")
        logger.info(f"{Fore.WHITE}───────────────────────────────────────")
    
    def log_new_review(self, review: types.Review):
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        logger.info(f"{Fore.YELLOW}Новый отзыв по заказу #{review.order_id}:")
        logger.info(f" · Оценка: {Fore.LIGHTYELLOW_EX}{'★' * review.stars or 5} ({review.stars or 5})")
        logger.info(f" · Текст: {Fore.LIGHTWHITE_EX}{review.text}")
        logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{review.author}")
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")


    def _event_datetime(self, latest_event_time, event_interval):
        if latest_event_time:
            return (
                datetime.fromisoformat(latest_event_time) 
                + timedelta(seconds=event_interval)
            )
        else:
            return datetime.now()

    async def _on_funpay_bot_init(self):

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

                if self.initialized_users != data.get("initialized_users"): 
                    data.set("initialized_users", self.initialized_users)
                if self.categories_raise_time != data.get("categories_raise_time"): 
                    data.set("categories_raise_time", self.categories_raise_time)
                if data.get("cached_orders") != self.cached_orders: 
                    data.set("cached_orders", self.cached_orders)
                
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
                if self.config["funpay"]["auto_raise_lots"]:
                    seconds = self.raise_lots()
                    time.sleep(seconds)
                time.sleep(3)

        def create_ticket_loop():
            while True:
                if (
                    self.config["funpay"]["auto_tickets"]["enabled"]
                    and datetime.now() >= self._event_datetime(
                        self.config["funpay"]["auto_tickets"]["last_time"], 
                        self.config["funpay"]["auto_tickets"]["interval"]
                    )
                ):
                    self.create_ticket()
                time.sleep(3)

        Thread(target=check_config_loop, daemon=True).start()
        Thread(target=refresh_account_loop, daemon=True).start()    
        Thread(target=check_banned_loop, daemon=True).start()
        Thread(target=raise_lots_loop, daemon=True).start()
        Thread(target=create_ticket_loop, daemon=True).start()

    async def _on_new_review(self, event: NewMessageEvent):
        review_order_id = event.message.text.split(' ')[-1].replace('#', '').replace('.', '')
        order = self.account.get_order(review_order_id)
        review = order.review

        if review.author == self.account.username:
            return
        
        self.log_new_review(review)
        if (
            self.config["funpay"]["notifications"]["enabled"] 
            and self.config["funpay"]["notifications"]["events"]["new_review"]
        ):
            text_frmtd = f"<blockquote>{review.text}</blockquote>" if review.text else "<i>Без текста</i>"
            self.log_to_tg(
                log_text(
                    f'🌟 Новый отзыв на заказ <a href="https://funpay.com/orders/{review_order_id}/">#{review_order_id}</a>', 
                    (f"<b>👤 Оставил:</b> {review.author}"
                    f"\n<b>✨ Оценка:</b> {'⭐' * review.stars}"
                    f"\n<b>🏷️ Текст:</b> {text_frmtd}")
                ),
                log_new_review_kb(event.message.chat_name, review_order_id)
            )

        order_title = order.full_description
        if not order_title:
            short_order = self.account.get_order_shortcut(review_order_id)
            order_title = short_order.description

        if (
            order.buyer_id != self.account.id
            and self.config["funpay"]["auto_review_replies"]
        ):
            self.account.send_review(
                order_id=review_order_id, 
                text=self.msg(
                    "order_review_reply", 
                    review_date=datetime.now().strftime("%d.%m.%Y"), 
                    order_title=order_title or "?", 
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
            self.config["funpay"]["notifications"]["enabled"] 
            and (
                self.config["funpay"]["notifications"]["events"]["new_user_message"] 
                or self.config["funpay"]["notifications"]["events"]["new_system_message"]
            )
        ):
            if (
                self.config["funpay"]["notifications"]["events"]["new_user_message"] and event.message.author.lower() != "funpay"
                or self.config["funpay"]["notifications"]["events"]["new_system_message"] and event.message.author.lower() == "funpay"
            ):
                text = event.message.text or ""
                text += f'<b><a href="{event.message.image_link}">{event.message.image_name}</a></b>' if event.message.image_link else ""
                
                self.log_to_tg(
                    log_text(
                        f'💬 Новое сообщение в <a href="https://funpay.com/chat/?node={event.message.chat_id}">чате</a>', 
                        f"<b>{event.message.author}:</b> <blockquote>{text.strip()}</blockquote>"
                    ),
                    log_new_mess_kb(event.message.chat_name)
                )

        if event.message.text is None:
            return
        if this_chat.name not in self.initialized_users:
            if event.message.type is MessageTypes.NON_SYSTEM:
                self.send_message(this_chat.id, self.msg("first_message", username=event.message.author))
            self.initialized_users.append(this_chat.name)

        if str(event.message.text).lower() in ("!продавец", "!seller"):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().call_seller(event.message.author, this_chat.id), 
                get_telegram_bot_loop()
            )
            self.send_message(this_chat.id, self.msg("cmd_seller"))
        
        if event.message.text.lower() in [key.lower() for key in self.custom_commands.keys()]:
            message = "\n".join(self.custom_commands[event.message.text])
            self.send_message(this_chat.id, message)

    async def _on_new_order(self, event: NewOrderEvent):
        if event.order.buyer_username == self.account.username:
            return
        this_chat = self.account.get_chat_by_name(event.order.buyer_username, True)

        self.cached_orders[event.order.id] = {
            "id": event.order.id,
            "price": event.order.price,
            "amount": event.order.amount,
            "status": event.order.status.name,
            "date": datetime.now(pytz.timezone("Europe/Moscow")).isoformat(),
            "description": event.order.description
        }
        
        self.log_new_order(event.order)
        if (
            self.config["funpay"]["notifications"]["enabled"] 
            and self.config["funpay"]["notifications"]["events"]["new_order"]
        ):
            self.log_to_tg(
                log_text(
                    f'📋 Новый заказ <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a>', 
                    (f"<b>👤 Покупатель:</b> {event.order.buyer_username}"
                    f"\n<b>🛍️ Товар:</b> {event.order.description}"
                    f"\n<b>🛒 Количество:</b> {event.order.amount}"
                    f"\n<b>💰 Сумма:</b> {event.order.price or '?'} {self.account.currency.name}")
                ),
                log_new_order_kb(this_chat.name, event.order.id)
            )

        self.send_message(this_chat.id, self.msg("new_order", 
            order_id=event.order.id, 
            order_title=event.order.description, 
            order_amount=event.order.amount
        ))
        
        lot = self.get_lot_by_order_title(event.order.description, event.order.subcategory)
        if lot and str(getattr(lot, "id")) in self.auto_deliveries.keys():
            self.send_message(this_chat.id, "\n".join(self.auto_deliveries[str(lot.id)]))

    async def _on_order_status_changed(self, event: OrderStatusChangedEvent):
        if event.order.buyer_username == self.account.username:
            return
        
        if event.order.status and event.order.id in self.cached_orders:
            self.cached_orders[event.order.id]["status"] = event.order.status.name
        
        this_chat = self.account.get_chat_by_name(event.order.buyer_username, True)
        
        status_frmtd = "Неизвестный"
        if event.order.status is OrderStatuses.PAID: status_frmtd = "Оплачен"
        elif event.order.status is OrderStatuses.CLOSED: status_frmtd = "Закрыт"
        elif event.order.status is OrderStatuses.REFUNDED: status_frmtd = "Возврат"

        self.log_order_status_changed(event.order, status_frmtd)
        if (
            self.config["funpay"]["notifications"]["enabled"] 
            and self.config["funpay"]["notifications"]["events"]["order_status_changed"]
        ):
            self.log_to_tg(
                log_text(f'🔄️ Статус заказа <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a> изменился на «{status_frmtd}»'),
                destroy_kb()
            )

        if event.order.status is OrderStatuses.CLOSED:
            self.send_message(this_chat.id, self.msg("order_confirmed", 
                order_id=event.order.id, 
                order_title=event.order.description, 
                order_amount=event.order.amount
            ))
        elif event.order.status is OrderStatuses.REFUNDED:
            self.send_message(this_chat.id, self.msg("order_refunded", 
                order_id=event.order.id, 
                order_title=event.order.description, 
                order_amount=event.order.amount
            ))


    async def run_bot(self):
        logger.info("")
        logger.info(f"{Fore.YELLOW}FunPay бот запущен и активен")
        logger.info("")

        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        logger.info(f"{Fore.YELLOW}Информация об аккаунте:")
        logger.info(f" · ID: {Fore.LIGHTWHITE_EX}{self.account.id}")
        logger.info(f" · Никнейм: {Fore.LIGHTWHITE_EX}{self.account.username}")
        logger.info(f" · Баланс: {Fore.LIGHTWHITE_EX}{self.account.total_balance} {self.account.currency.name if self.account.currency != Currency.UNKNOWN else 'RUB'}")
        logger.info(f" · Активные продажи: {Fore.LIGHTWHITE_EX}{self.account.active_sales}")
        logger.info(f" · Активные покупки: {Fore.LIGHTWHITE_EX}{self.account.active_purchases}")
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        
        proxy = self.config["funpay"]["api"]["proxy"]
        if proxy:
            if "@" in proxy:
                user, password = proxy.split("@")[0].split(":")
                ip, port = proxy.split("@")[1].split(":")
            else:
                user, password = None, None
                ip, port = proxy.split(":")
            
            ip = ".".join([("*" * len(nums)) if i >= 3 else nums for i, nums in enumerate(ip.split("."), start=1)])
            port = f"{port[:3]}**"
            user = f"{user[:3]}*****" if user else "-"
            password = f"{password[:3]}*****" if password else "-"

            logger.info("")
            logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
            logger.info(f"{Fore.YELLOW}Информация о прокси:")
            logger.info(f" · IP: {Fore.LIGHTWHITE_EX}{ip}:{port}")
            logger.info(f" · Юзер: {Fore.LIGHTWHITE_EX}{user}")
            logger.info(f" · Пароль: {Fore.LIGHTWHITE_EX}{password}")
            logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
            logger.info("")
            
        add_bot_event_handler("ON_FUNPAY_BOT_INIT", FunPayBot._on_funpay_bot_init, 0)
        add_funpay_event_handler(EventTypes.NEW_MESSAGE, FunPayBot._on_new_message, 0)
        add_funpay_event_handler(EventTypes.NEW_ORDER, FunPayBot._on_new_order, 0) 
        add_funpay_event_handler(EventTypes.ORDER_STATUS_CHANGED, FunPayBot._on_order_status_changed, 0)

        async def runner_loop():
            runner = Runner(self.account)
            Thread(target=runner.loop, daemon=True).start()
            for event in runner.listen(requests_delay=self.config["funpay"]["api"]["runner_requests_delay"]):
                await call_funpay_event(event.type, [self, event])

        run_async_in_thread(runner_loop)

        await call_bot_event("ON_FUNPAY_BOT_INIT", [self])