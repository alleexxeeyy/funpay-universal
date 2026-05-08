import textwrap
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import get_event_next_time

from .. import callback_datas as calls


def tickets_text():
    config = sett.get("config")
    
    enabled = "✅" if config["funpay"]["auto_tickets"]["enabled"] else "❌"
    interval = config["funpay"]["auto_tickets"]["interval"] or "❌ Не задано"
    
    min_order_age = config["funpay"]["auto_tickets"]["min_order_age"] or "❌ Не задано"
    orders_per_ticket = config["funpay"]["auto_tickets"]["orders_per_ticket"] or "❌ Не задано"
    
    last_time_iso = config["funpay"]["auto_tickets"]["last_time"]
    last_time = datetime.fromisoformat(last_time_iso).strftime("%d.%m.%Y %H:%M:%S") if last_time_iso else "никогда"

    if config["funpay"]["auto_tickets"]["enabled"]:
        if not last_time_iso:
            next_time = "прямо сейчас"
        else:
            next_time = get_event_next_time(last_time_iso, config["funpay"]["auto_tickets"]["interval"]).strftime("%d.%m.%Y %H:%M:%S")
    else:
        next_time = "никогда"

    txt = textwrap.dedent(f"""
        <b>📞 Авто-тикеты</b>
        <blockquote><b>(?)</b> Бот будет автоматически создавать тикет в тех. поддержку на закрытие незакрытых заказов каждые 24 часа. Чем больше заказов в одном тикете - тем дольше его будут проверять, 25 заказов - оптимальное значение.</blockquote>

        <b>💡 Включено:</b> {enabled}
        <b>⏰ Интервал:</b> {interval} сек.

        <b>📋 Заказов в тикете:</b> {orders_per_ticket}
        <b>👴 Мин. возраст заказов:</b> {min_order_age} сек.

        ⏮️ Последний раз был создан <b>{last_time}</b>
        ⏭️ Следующий раз будет создан <b>{next_time}</b>
    """)
    return txt


def tickets_kb():
    config = sett.get("config")
    
    enabled = "✅" if config["funpay"]["auto_tickets"]["enabled"] else "❌"
    interval = config["funpay"]["auto_tickets"]["interval"] or "❌ Не задано"
    
    min_order_age = config["funpay"]["auto_tickets"]["min_order_age"] or "❌ Не задано"
    orders_per_ticket = config["funpay"]["auto_tickets"]["orders_per_ticket"] or "❌ Не задано"
    
    rows = [
        [InlineKeyboardButton(text=f"📞 Создать тикет", callback_data="confirm_creating_tickets")],
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_auto_tickets_enabled")],
        [InlineKeyboardButton(text=f"⏰ Интервал: {interval} сек.", callback_data="enter_auto_tickets_create_interval")],
        [InlineKeyboardButton(text=f"📋 Заказов в тикете: {orders_per_ticket}", callback_data="enter_auto_tickets_orders_per_ticket")],
        [InlineKeyboardButton(text=f"👴 Мин. возраст заказов: {min_order_age} сек.", callback_data="enter_auto_tickets_min_order_age")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def tickets_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📞 Авто-тикеты</b>
        \n{placeholder}
    """)
    return txt