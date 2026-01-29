import textwrap
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from data import Data as data

from .. import callback_datas as calls


def events_text():
    config = sett.get("config")
    latest_events_times = data.get("latest_events_times")
    
    last_create_tickets = (datetime.fromisoformat(latest_events_times["create_tickets"]).strftime("%d.%m.%Y %H:%M")) if latest_events_times.get("create_tickets") else "❌ Не было"
    next_create_tickets = ((datetime.fromisoformat(latest_events_times["create_tickets"]) if latest_events_times.get("create_tickets") else datetime.now()) + timedelta(seconds=config["funpay"]["auto_tickets"]["interval"])).strftime("%d.%m.%Y %H:%M")
    
    txt = textwrap.dedent(f"""
        <b>🚩 Ивенты</b>

        <b>📆📞 Создание тикетов на закрытие заказов:</b>
        ・ <b>Последнее:</b> {last_create_tickets}
        ・ <b>Следующее:</b> {next_create_tickets}
    """)
    return txt


def events_kb():
    rows = [
        [InlineKeyboardButton(text="📞 Создать тикеты на закрытие заказов", callback_data="confirm_creating_tickets")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def events_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🚩 Ивенты</b>
        \n{placeholder}
    """)
    return txt