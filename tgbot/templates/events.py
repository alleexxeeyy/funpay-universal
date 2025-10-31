import textwrap
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from data import Data as data

from .. import callback_datas as calls


def events_text():
    config = sett.get("config")
    auto_tickets = data.get("auto_tickets")
    last_auto_tickets_create = (datetime.fromisoformat(auto_tickets["last_time"]).strftime("%d.%m.%Y %H:%M")) if auto_tickets.get("last_time") else "❌ Не было"
    next_auto_tickets_create = ((datetime.fromisoformat(auto_tickets["last_time"]) if auto_tickets.get("last_time") else datetime.now()) + timedelta(seconds=config["funpay"]["auto_tickets"]["interval"])).strftime("%d.%m.%Y %H:%M")
    txt = textwrap.dedent(f"""
        🚩 <b>Ивенты</b>

        📆📞 <b>Создание тикетов на закрытие заказов:</b>
        ┣ <b>Последнее:</b> {last_auto_tickets_create}
        ┗ <b>Следующее:</b> {next_auto_tickets_create}

        Выберите действие ↓
    """)
    return txt


def events_kb():
    rows = [
        [InlineKeyboardButton(text="📞 Создать тикеты на закрытие заказов", callback_data="confirm_creating_tickets")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()), 
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MenuNavigation(to="events").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def events_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        🚩 <b>Ивенты</b>
        \n{placeholder}
    """)
    return txt