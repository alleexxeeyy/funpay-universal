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
        ⚙️ <b>Настройки → 👀 Логгер</b>

        👀 <b>Логгирование ивентов FunPay в Telegram:</b> {tg_logging_enabled}
        💬 <b>ID чата для логов:</b> <b>{tg_logging_chat_id}</b>
        📢 <b>Ивенты логгирования:</b>
        ┣ {event_new_user_message} <b>💬👤 Новое сообщение от пользователя</b>
        ┣ {event_new_system_message} <b>💬⚙️ Новое системное сообщение</b>
        ┣ {event_new_order} <b>📋 Новый заказ</b>
        ┣ {event_order_status_changed} <b>🔄️📋 Статус заказа изменился</b>
        ┗ {event_new_review} <b>💬✨ Новый отзыв</b>
        
        Выберите параметр для изменения ↓
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
        [InlineKeyboardButton(text=f"👀 Логгирование ивентов FunPay в Telegram: {tg_logging_enabled}", callback_data="switch_logger|tg_logging|enabled")],
        [InlineKeyboardButton(text=f"💬 ID чата для логов: {tg_logging_chat_id}", callback_data="enter_tg_logging_chat_id")],
        [
        InlineKeyboardButton(text=f"{event_new_user_message} 💬👤 Новое сообщение от пользователя", callback_data="switch_logger|tg_logging|events|new_user_message"),
        InlineKeyboardButton(text=f"{event_new_system_message} 💬⚙️ Новое системное сообщение", callback_data="switch_logger|tg_logging|events|new_system_message"),
        ],
        [
        InlineKeyboardButton(text=f"{event_new_order} 📋 Новый заказ", callback_data="switch_logger|tg_logging|events|new_order"),
        InlineKeyboardButton(text=f"{event_order_status_changed} 🔄️📋 Статус заказа изменился", callback_data="switch_logger|tg_logging|events|order_status_changed"),
        InlineKeyboardButton(text=f"{event_new_review} 💬✨ Новый отзыв", callback_data="switch_logger|tg_logging|events|new_review")
        ],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="logger").pack())
        ]
    ]
    if config["funpay"]["tg_logging"]["chat_id"]:
        rows[1].append(InlineKeyboardButton(text=f"❌💬 Очистить", callback_data="clean_logger|tg_logging|chat_id"))
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_logger_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 👀 Логгер</b>
        \n{placeholder}
    """)
    return txt