from __future__ import annotations
import asyncio
import time
from datetime import datetime, timedelta
from typing import  Optional
import time
import traceback
from threading import Thread
from colorama import Fore
from rapidfuzz import fuzz
from aiogram.types import InlineKeyboardMarkup
import textwrap
import shutil
import re

from __init__ import VERSION
from FunPayAPI import Account, Runner, exceptions as fpapi_exceptions, types as fpapi_types
from FunPayAPI.common.enums import *
from FunPayAPI.updater.events import *
from core.utils import set_title
from core.handlers import get_bot_event_handlers, set_bot_event_handlers, get_funpay_event_handlers, set_funpay_event_handlers
from settings import Settings as sett
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
        proxy = {"https": "http://" + self.config["funpay"]["api"]["proxy"], "http": "http://" + self.config["funpay"]["api"]["proxy"]} if self.config["funpay"]["api"]["proxy"] else None
        self.funpay_account = Account(golden_key=self.config["funpay"]["api"]["golden_key"],
                                      user_agent=self.config["funpay"]["api"]["user_agent"],
                                      requests_timeout=self.config["funpay"]["api"]["requests_timeout"],
                                      proxy=proxy or None).get()

        self.initialized_users = data.get("initialized_users")
        self.categories_raise_time = data.get("categories_raise_time")
        self.auto_support_tickets = data.get("auto_support_tickets")
        self.stats = get_stats()

        self.lots_raise_next_time = datetime.now()


    def msg(self, message_name: str, exclude_watermark: bool = False,
            messages_config_name: str = "messages", messages_data: dict | None = None,
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
        mess: dict = messages.get(message_name, {})
        if mess.get("enabled") is False:
            return None
        message_lines: list[str] = mess.get("text", [])
        if message_lines and message_lines:
            try:
                formatted_lines = [line.format_map(SafeDict(**kwargs)) for line in message_lines]
                msg = "\n".join(formatted_lines)
                if not exclude_watermark and self.config["funpay"]["bot"]["messages_watermark_enabled"]:
                    msg += f'\n{self.config["funpay"]["bot"]["messages_watermark"]}' or ""
                return msg
            except:
                pass
        return "Не удалось получить сообщение"
    
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
        def extract_numbers(s: str):
            return re.findall(r"\d+", s)

        title_norm = title.strip().lower()
        title_nums = extract_numbers(title_norm)
        for _ in range(max_attempts):
            try:
                profile = self.funpay_account.get_user(self.funpay_account.id)
                lots = profile.get_sorted_lots(2)
                subcat_id = subcategory.id if subcategory else subcategory_id
                best = (0, None)
                for lot_subcat, lot_data in lots.items():
                    if subcat_id and lot_subcat.id != subcat_id:
                        continue
                    for _, lot in lot_data.items():
                        lot_title = (lot.title or "").strip().lower()
                        if not lot_title:
                            continue
                        if lot_title == title_norm:
                            return lot
                        score = max(
                            fuzz.partial_ratio(title_norm, lot_title),
                            fuzz.token_set_ratio(title_norm, lot_title)
                        )
                        lot_nums = extract_numbers(lot_title)
                        if title_nums and lot_nums:
                            score = (score + 10) if title_nums == lot_nums else (score - 10)
                        elif title_nums and not lot_nums:
                            score -= 5
                        if score > best[0]:
                            best = (score, lot)
                if best[1] and best[0] >= 70:
                    return best[1]
            except Exception:
                continue
        self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось получить лот по названию заказа «{title}»")
    
    def get_lot_by_order_title(self, title: str, subcategory: types.SubCategory | None = None,
                               subcategory_id: int | None = None) -> types.LotShortcut:
        return self.get_lot_by_title(title, subcategory, subcategory_id)

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
                    self.logger.error(f"{Fore.LIGHTRED_EX}При поднятии лотов произошла ошибка 429 слишком частых запросов. Попытаюсь поднять лоты снова через 5 минут")
                    self.lots_raise_next_time = datetime.now() + timedelta(minutes=5)
                    return
            time.sleep(1)

        for category in self.categories_raise_time:
            if datetime.fromisoformat(self.categories_raise_time[category]) < self.lots_raise_next_time:
                self.lots_raise_next_time = datetime.fromisoformat(self.categories_raise_time[category])
        if len(raised_categories) > 0:
            self.logger.info(f'{Fore.YELLOW}Подняты категории: {Fore.LIGHTWHITE_EX}{f"{Fore.WHITE}, {Fore.LIGHTWHITE_EX}".join(map(str, raised_categories))}')

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
        if text is None:
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

    def log_to_tg(self, text: str, kb: InlineKeyboardMarkup | None = None):
        """
        Отправляет сообщение всем авторизованным в боте пользователям.

        :param text: Текст сообщения.
        :type text: `str`
        
        :param kb: Клавиатура сообщения, _опционально_.
        :type kb: `aiogram.types.InlineKeyboardMarkup` or `None`
        """
        asyncio.run_coroutine_threadsafe(get_telegram_bot().log_event(text, kb), get_telegram_bot_loop())
    
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
    
    def log_order_status_changed(self, order: types.OrderShortcut):
        status = "Неизвестный"
        if order.status is OrderStatuses.PAID: status = "Оплачен"
        elif order.status is OrderStatuses.CLOSED: status = "Закрыт"
        elif order.status is OrderStatuses.REFUNDED: status = "Возврат"
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")
        self.logger.info(f"{Fore.WHITE}Статус заказа {Fore.LIGHTWHITE_EX}#{order.id} {Fore.WHITE}изменился:")
        self.logger.info(f" · Статус: {Fore.LIGHTWHITE_EX}{status}")
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
    
    def create_support_tickets(self):
        try:
            last_time = datetime.now()
            self.auto_support_tickets["last_time"] = last_time.isoformat()
            data.set("auto_support_tickets", self.auto_support_tickets)
            fpbot = get_funpay_bot()
            support_api = FunPaySupportAPI(self.funpay_account).get()
            self.logger.info(f"{Fore.WHITE}Создаю тикеты в тех. поддержку на закрытие заказов...")

            def calculate_orders(all_orders, orders_per_ticket=25):
                return [all_orders[i:i+orders_per_ticket] for i in range(0, len(all_orders), orders_per_ticket)]

            all_sales: list[fpapi_types.OrderShortcut] = []
            start_from = self.auto_support_tickets["next_start_from"] if self.auto_support_tickets["next_start_from"] != None else None
            while len(all_sales) < self.funpay_account.active_sales:
                sales = self.funpay_account.get_sales(start_from=start_from, include_paid=True, include_closed=False, include_refunded=False)
                for sale in sales[1]:
                    all_sales.append(sale)
                start_from = sales[0]
                time.sleep(0.5)
            
            order_ids = calculate_orders([order.id for order in all_sales], self.config["funpay"]["bot"]["auto_support_tickets_orders_per_ticket"])
            ticketed_orders = []
            for order_ids_per_ticket in order_ids:
                formatted_order_ids = ", ".join(order_ids_per_ticket)
                resp: dict = support_api.create_ticket(formatted_order_ids, f"Здравствуйте! Прошу подтвердить заказы, ожидающие подтверждения: {formatted_order_ids}. С уважением, {self.funpay_account.username}!")
                if resp.get("error") or not resp.get("action") or resp["action"]["message"] != "Ваша заявка отправлена.":
                    self.auto_support_tickets["next_start_from"] = order_ids_per_ticket[0]
                    break
                ticketed_orders.extend(order_ids_per_ticket)
                self.logger.info(f"{Fore.LIGHTWHITE_EX}{resp['action']['url'].split('/')[-1]} (https://support.funpay.com{resp['action']['url']}) {Fore.WHITE}— тикет создан для {Fore.LIGHTCYAN_EX}{len(order_ids_per_ticket)} заказов")
            else:
                self.auto_support_tickets["next_start_from"] = None
            self.auto_support_tickets["last_time"] = (datetime.now() + timedelta(seconds=self.config["funpay"]["bot"]["auto_support_tickets_create_interval"])).isoformat()
            
            if len(ticketed_orders) == 0 and self.auto_support_tickets["next_start_from"] is not None:
                self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось создать тикеты в тех. поддержку по причине: {Fore.WHITE}{resp.get('error') if resp else 'Неизвестная ошибка.'}")
            elif len(ticketed_orders) >= 0:
                self.logger.info(f"{Fore.CYAN}Создал {Fore.LIGHTCYAN_EX}{len(calculate_orders(ticketed_orders))} тикета(-ов) в тех. поддержку {Fore.CYAN}на закрытие {Fore.LIGHTCYAN_EX}{len(ticketed_orders)} заказов")
            next_time = last_time + timedelta(seconds=self.config["funpay"]["bot"]["auto_support_tickets_create_interval"])
            self.logger.info(f"Следующая попытка будет {Fore.LIGHTWHITE_EX}{next_time.strftime(f'%d.%m{Fore.WHITE} в {Fore.LIGHTWHITE_EX}%H:%M')}")
        except Exception as e:
            self.logger.error(f"{Fore.LIGHTRED_EX}При отправке тикетов на закрытие произошла ошибка: {Fore.WHITE}")
            traceback.print_exc()
    
    async def run_bot(self):
        self.logger.info(f"{Fore.GREEN}FunPay бот запущен и активен")
        self.logger.info("")
        self.logger.info(f"{Fore.CYAN}───────────────────────────────────────")
        self.logger.info(f"{Fore.CYAN}Информация об аккаунте:")
        self.logger.info(f" · ID: {Fore.LIGHTWHITE_EX}{self.funpay_account.id}")
        self.logger.info(f" · Никнейм: {Fore.LIGHTWHITE_EX}{self.funpay_account.username}")
        self.logger.info(f" · Баланс: {Fore.LIGHTWHITE_EX}{self.funpay_account.total_balance} {self.funpay_account.currency.name}")
        self.logger.info(f" · Активные продажи: {Fore.LIGHTWHITE_EX}{self.funpay_account.active_sales}")
        self.logger.info(f" · Активные покупки: {Fore.LIGHTWHITE_EX}{self.funpay_account.active_purchases}")
        self.logger.info(f"{Fore.CYAN}───────────────────────────────────────")
        self.logger.info("")
        if self.config["funpay"]["api"]["proxy"]:
            user, password = self.config["funpay"]["api"]["proxy"].split("@")[0].split(":") if "@" in self.config["funpay"]["api"]["proxy"] else self.config["funpay"]["api"]["proxy"]
            ip, port = self.config["funpay"]["api"]["proxy"].split("@")[1].split(":") if "@" in self.config["funpay"]["api"]["proxy"] else self.config["funpay"]["api"]["proxy"]
            self.logger.info(f"{Fore.CYAN}───────────────────────────────────────")
            self.logger.info(f"{Fore.CYAN}Информация о прокси:")
            self.logger.info(f" · IP: {Fore.LIGHTWHITE_EX}{ip}:{port}")
            self.logger.info(f" · Юзер: {(f'{Fore.LIGHTWHITE_EX}{user[:3]}' + '*' * 5) if user else f'Без авторизации'}")
            self.logger.info(f" · Пароль: {(f'{Fore.LIGHTWHITE_EX}{password[:3]}' + '*' * 5) if password else f'Без авторизации'}")
            self.logger.info(f"{Fore.CYAN}───────────────────────────────────────")
            self.logger.info("")
            
        def on_funpay_bot_init(fpbot: FunPayBot):
            self.stats.bot_launch_time = datetime.now()
            
            def endless_loop():
                while True:
                    try:
                        set_title(f"FunPay Universal v{VERSION} | {self.funpay_account.username}: {self.funpay_account.total_balance} {self.funpay_account.currency.name}. Активных заказов: {self.funpay_account.active_sales}")
                        if self.initialized_users != data.get("initialized_users"): data.set("initialized_users", self.initialized_users)
                        if self.categories_raise_time != data.get("categories_raise_time"): data.set("categories_raise_time", self.categories_raise_time)
                        if self.auto_support_tickets != data.get("auto_support_tickets"): self.auto_support_tickets = data.get("auto_support_tickets")
                        if self.stats != get_stats(): set_stats(self.stats)
                        self.config = sett.get("config") if self.config != sett.get("config") else self.config
                        self.messages = sett.get("messages") if self.messages != sett.get("messages") else self.messages
                        self.custom_commands = sett.get("custom_commands") if self.custom_commands != sett.get("custom_commands") else self.custom_commands
                        self.auto_deliveries = sett.get("auto_deliveries") if self.auto_deliveries != sett.get("auto_deliveries") else self.auto_deliveries
                    except Exception as e:
                        self.logger.error(f"{Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка: {Fore.WHITE}{e}")
                    time.sleep(3)

            def refresh_funpay_account_loop():
                while True:
                    try:
                        proxy = {"https": "http://" + self.config["funpay"]["api"]["proxy"], "http": "http://" + self.config["funpay"]["api"]["proxy"]} if self.config["funpay"]["api"]["proxy"] else None
                        self.funpay_account = Account(golden_key=self.config["funpay"]["api"]["golden_key"],
                                                      user_agent=self.config["funpay"]["api"]["user_agent"],
                                                      requests_timeout=self.config["funpay"]["api"]["requests_timeout"],
                                                      proxy=proxy or None).get(update_phpsessid=True)
                        time.sleep(2400)
                    except Exception as e:
                        self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обновлении данных аккаунта FunPay: {Fore.WHITE}{e}")
                        time.sleep(60)

            def raise_lots_loop():
                while True:
                    try:
                        if self.config["funpay"]["bot"]["auto_raising_lots_enabled"] and datetime.now() > self.lots_raise_next_time:
                            self.raise_lots()
                        time.sleep(3)
                    except Exception as e:
                        self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при поднятии лотов: {Fore.WHITE}{e}")
                        time.sleep(30)

            def create_support_tickets_loop():
                while True:
                    try:
                        if self.config["funpay"]["bot"]["auto_support_tickets_enabled"]:
                            if datetime.now() >= (datetime.fromisoformat(self.auto_support_tickets["last_time"]) + timedelta(seconds=self.config["funpay"]["bot"]["auto_support_tickets_create_interval"])) if self.auto_support_tickets["last_time"] else datetime.now():
                                self.auto_support_tickets["last_time"] = datetime.now().isoformat()
                                data.set("auto_support_tickets", self.auto_support_tickets)
                                self.create_support_tickets()
                        time.sleep(3)
                    except Exception as e:
                        self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при создании тикетов: {Fore.WHITE}{e}")
                        time.sleep(30)

            Thread(target=endless_loop, daemon=True).start()
            Thread(target=refresh_funpay_account_loop, daemon=True).start()
            Thread(target=raise_lots_loop, daemon=True).start()
            Thread(target=create_support_tickets_loop, daemon=True).start()
        
        bot_event_handlers = get_bot_event_handlers()
        bot_event_handlers["ON_FUNPAY_BOT_INIT"].insert(0, on_funpay_bot_init)
        set_bot_event_handlers(bot_event_handlers)

        async def on_new_review(fpbot: FunPayBot, event: NewMessageEvent):
            try:
                review_order_id = event.message.text.split(' ')[-1].replace('#', '').replace('.', '')
                order = self.funpay_account.get_order(review_order_id)
                review = order.review
                if order.buyer_username != self.funpay_account.username:
                    self.log_new_review(order.review)
                    if self.config["funpay"]["bot"]["tg_logging_enabled"] and self.config["funpay"]["bot"]["tg_logging_events"]["new_review"]:
                        self.log_to_tg(text=log_text(f'✨💬 Новый отзыв на заказ <a href="https://funpay.com/orders/{review_order_id}/">#{review_order_id}</a>', f"<b>┏ Оценка:</b> {'⭐' * review.stars}\n<b>┣ Оставил:</b> {review.author}\n<b>┗ Текст отзыва:</b> {review.text}"),
                                       kb=log_new_review_kb(event.message.chat_name, review_order_id))
                    if self.config["funpay"]["bot"]["auto_reviews_replies_enabled"]:
                        self.funpay_account.send_review(review_order_id, self.msg("order_review_reply", review_date=datetime.now().strftime("%d.%m.%Y"), order_title=order.title, order_amount=order.amount, order_price=order.sum))
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента новых отзывов произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()
        
        async def on_new_message(fpbot: FunPayBot, event: NewMessageEvent):
            try:
                this_chat = self.funpay_account.get_chat_by_name(event.message.chat_name, True)
                if event.message.type is not MessageTypes.NEW_FEEDBACK:
                    self.log_new_message(event.message)
                if self.config["funpay"]["bot"]["tg_logging_enabled"] and (self.config["funpay"]["bot"]["tg_logging_events"]["new_user_message"] or self.config["funpay"]["bot"]["tg_logging_events"]["new_system_message"]):
                    if event.message.author != self.funpay_account.username:
                        do = False
                        if self.config["funpay"]["bot"]["tg_logging_events"]["new_user_message"] and event.message.author.lower() != "funpay": do = True 
                        if self.config["funpay"]["bot"]["tg_logging_events"]["new_system_message"] and event.message.author.lower() == "funpay": do = True 
                        if do:
                            text = f"<b>{event.message.author}:</b> {event.message.text or ''}"
                            if event.message.image_link:
                                text += f' <b><a href="{event.message.image_link}">{event.message.image_name}</a></b>'
                            self.log_to_tg(text=log_text('💬 Новое сообщение в <a href="https://funpay.com/chat/?node={event.message.chat_id}">чате</a>', text.strip()),
                                            kb=log_new_mess_kb(event.message.chat_name))

                if event.message.author == this_chat.name:
                    if this_chat.name not in self.initialized_users:
                        if event.message.type is MessageTypes.NON_SYSTEM:
                            self.send_message(this_chat.id, self.msg("first_message", username=event.message.author))
                        self.initialized_users.append(this_chat.name)
                    
                    if self.config["funpay"]["bot"]["custom_commands_enabled"]:
                        if event.message.text in self.custom_commands.keys():
                            message = "\n".join(self.custom_commands[event.message.text])
                            self.send_message(this_chat.id, message)
                    if str(event.message.text).lower() == "!команды" or str(event.message.text).lower() == "!commands":
                        self.send_message(this_chat.id, self.msg("cmd_commands"))
                    elif str(event.message.text).lower() == "!продавец" or str(event.message.text).lower() == "!seller":
                        asyncio.run_coroutine_threadsafe(get_telegram_bot().call_seller(event.message.author, this_chat.id), get_telegram_bot_loop())
                        self.send_message(this_chat.id, self.msg("cmd_seller"))

                if event.message.type is MessageTypes.NEW_FEEDBACK:
                    await on_new_review(fpbot, event)
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def on_new_order(fpbot: FunPayBot, event: NewOrderEvent):
            try:
                this_chat = self.funpay_account.get_chat_by_name(event.order.buyer_username, True)
                if event.order.buyer_username != self.funpay_account.username:
                    self.log_new_order(event.order)
                    if self.config["funpay"]["bot"]["tg_logging_enabled"] and self.config["funpay"]["bot"]["tg_logging_events"]["new_order"]:
                        self.log_to_tg(text=log_text(f'📋 Новый заказ <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a>', f"<b>┏ Покупатель:</b> {event.order.buyer_username}\n<b>┣ Товар:</b> {event.order.description}\n<b>┣ Количество:</b> {event.order.amount}\n<b>┗ Сумма:</b> {event.order.price} {self.funpay_account.currency.name}"),
                                        kb=log_new_order_kb(this_chat.name, event.order.id))
                    self.send_message(this_chat.id, self.msg("new_order", order_id=event.order.id, order_title=event.order.description, order_amount=event.order.amount))
                    if self.config["funpay"]["bot"]["auto_deliveries_enabled"]:
                        lot = self.get_lot_by_order_title(event.order.description, event.order.subcategory)
                        if lot:
                            if str(lot.id) in self.auto_deliveries.keys():
                                self.send_message(this_chat.id, "\n".join(self.auto_deliveries[str(lot.id)]))
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента новых заказов произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()
            
        async def on_order_status_changed(fpbot: FunPayBot, event: OrderStatusChangedEvent):
            try:
                this_chat = self.funpay_account.get_chat_by_name(event.order.buyer_username, True)
                if event.order.buyer_username != self.funpay_account.username:
                    self.log_order_status_changed(event.order)
                    status = "Неизвестный"
                    if event.order.status is OrderStatuses.PAID: status = "Оплачен"
                    elif event.order.status is OrderStatuses.CLOSED: status = "Закрыт"
                    elif event.order.status is OrderStatuses.REFUNDED: status = "Возврат"
                    if self.config["funpay"]["bot"]["tg_logging_enabled"] and self.config["funpay"]["bot"]["tg_logging_events"]["order_status_changed"]:
                        self.log_to_tg(log_text(f'🔄️📋 Статус заказа <a href="https://funpay.com/orders/{event.order.id}/">#{event.order.id}</a> изменился', f"<b>Новый статус:</b> {status}"))
                    if event.order.status is OrderStatuses.CLOSED:
                        self.stats.orders_completed = 1
                        self.stats.earned_money = round(self.stats.earned_money + event.order.price, 2)
                        self.send_message(this_chat.id, self.msg("order_confirmed", order_id=event.order.id, order_title=event.order.description, order_amount=event.order.amount))
                    elif event.order.status is OrderStatuses.REFUNDED:
                        self.stats.orders_refunded = self.stats.orders_refunded + 1
                        self.send_message(this_chat.id, self.msg("order_refunded", order_id=event.order.id, order_title=event.order.description, order_amount=event.order.amount))
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента смены статуса заказа произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()
            
        funpay_event_handlers = get_funpay_event_handlers()
        funpay_event_handlers[EventTypes.NEW_MESSAGE].insert(0, on_new_message)
        funpay_event_handlers[EventTypes.NEW_ORDER].insert(0, on_new_order)
        funpay_event_handlers[EventTypes.ORDER_STATUS_CHANGED].insert(0, on_order_status_changed)
        set_funpay_event_handlers(funpay_event_handlers)

        bot_event_handlers = get_bot_event_handlers()
        def handle_on_funpay_bot_init():
            """ 
            Запускается при инициализации FunPay бота.
            Запускает за собой все хендлеры ON_FUNPAY_BOT_INIT 
            """
            for handler in bot_event_handlers.get("ON_FUNPAY_BOT_INIT", []):
                try:
                    handler(self)
                except Exception as e:
                    self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_FUNPAY_BOT_INIT: {Fore.WHITE}{e}")
        handle_on_funpay_bot_init()

        self.logger.info(f"Слушатель событий запущен")
        runner = Runner(self.funpay_account)
        for event in runner.listen(requests_delay=self.config["funpay"]["api"]["runner_requests_delay"]):
            funpay_event_handlers = get_funpay_event_handlers() # чтобы каждый раз брать свежие хендлеры, ибо модули могут отключаться/включаться
            if event.type in funpay_event_handlers:
                for handler in funpay_event_handlers[event.type]:
                    try:
                        await handler(self, event)
                    except Exception as e:
                        self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}{e}")