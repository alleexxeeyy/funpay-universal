import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_logger_text():
    config = sett.get("config")
    
    tg_logging_enabled = "🟢 Включено" if config["funpay"]["tg_logging"]["enabled"] else "🔴 Выключено"
    tg_logging_chat_id = config["funpay"]["tg_logging"]["chat_id"] or "✔️ Ваш чат с ботом"
    tg_logging_events = config["funpay"]["tg_logging"]["events"] or {}
    event_new_user_message = "🟢" if tg_logging_events["new_user_message"] else "🔴"
    event_new_system_message = "🟢" if tg_logging_events["new_system_message"] else "🔴"
    event_new_order = "🟢" if tg_logging_events["new_order"] else "🔴"
    event_order_status_changed = "🟢" if tg_logging_events["order_status_changed"] else "🔴"
    event_new_review = "🟢" if tg_logging_events["new_review"] else "🔴"
    
    txt = textwrap.dedent(f"""
        <b>👀 Логгер</b>

        <b>👀 Логгирование ивентов:</b> {tg_logging_enabled}
        <b>💬 ID чата для логов:</b> {tg_logging_chat_id}
        
        <b>📢 Ивенты:</b>
        ・ {event_new_user_message}  👤 Новое сообщение от пользователя
        ・ {event_new_system_message}  ⚙️ Новое системное сообщение
        ・ {event_new_order}  📋 Новый заказ
        ・ {event_order_status_changed}  🔄️ Статус заказа изменился
        ・ {event_new_review}  ✨ Новый отзыв
    """)
    return txt


def settings_logger_kb():
    config = sett.get("config")
    
    tg_logging_enabled = "🟢 Включено" if config["funpay"]["tg_logging"]["enabled"] else "🔴 Выключено"
    tg_logging_chat_id = config["funpay"]["tg_logging"]["chat_id"] or "✔️ Ваш чат с ботом"
    tg_logging_events = config["funpay"]["tg_logging"]["events"] or {}
    event_new_user_message = "🟢" if tg_logging_events["new_user_message"] else "🔴"
    event_new_system_message = "🟢" if tg_logging_events["new_system_message"] else "🔴"
    event_new_order = "🟢" if tg_logging_events["new_order"] else "🔴"
    event_order_status_changed = "🟢" if tg_logging_events["order_status_changed"] else "🔴"
    event_new_review = "🟢" if tg_logging_events["new_review"] else "🔴"
    
    rows = [
        [InlineKeyboardButton(text=f"👀 Логгирование ивентов: {tg_logging_enabled}", callback_data="switch_tg_logging_enabled")],
        [InlineKeyboardButton(text=f"💬 ID чата для логов: {tg_logging_chat_id}", callback_data="enter_tg_logging_chat_id")],
        [
        InlineKeyboardButton(text=f"{event_new_user_message} 👤 Новое сообщение от пользователя", callback_data="switch_tg_logging_event_new_user_message"),
        InlineKeyboardButton(text=f"{event_new_system_message} ⚙️ Новое системное сообщение", callback_data="switch_tg_logging_event_new_system_message"),
        ],
        [
        InlineKeyboardButton(text=f"{event_new_order} 📋 Новый заказ", callback_data="switch_tg_logging_event_new_order"),
        InlineKeyboardButton(text=f"{event_order_status_changed} 🔄️ Статус заказа изменился", callback_data="switch_tg_logging_event_order_status_changed"),
        ],
        [InlineKeyboardButton(text=f"{event_new_review} ✨ Новый отзыв", callback_data="switch_tg_logging_event_new_review")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    if config["funpay"]["tg_logging"]["chat_id"]:
        rows[1].append(InlineKeyboardButton(text=f"❌💬 Очистить", callback_data="clean_tg_logging_chat_id"))
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_logger_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>👀 Логгер</b>
        \n{placeholder}
    """)
    return txt