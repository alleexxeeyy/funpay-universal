import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def notifications_text():
    config = sett.get("config")
    
    enabled = "✅" if config["funpay"]["notifications"]["enabled"] else "❌"
    chat_id = config["funpay"]["notifications"]["chat_id"] or "Текущий"
    events = config["funpay"]["notifications"]["events"] or {}

    new_user_message = "🟢" if events["new_user_message"] else "🔴"
    new_system_message = "🟢" if events["new_system_message"] else "🔴"
    new_order = "🟢" if events["new_order"] else "🔴"
    order_status_changed = "🟢" if events["order_status_changed"] else "🔴"
    new_review = "🟢" if events["new_review"] else "🔴"
    ticket_created = "🟢" if events["ticket_created"] else "🔴"
    
    txt = textwrap.dedent(f"""
        <b>🔔 Уведомления</b>

        <b>💡 Включено:</b> {enabled}
        <b>💬 Чат:</b> {chat_id}
        
        {new_user_message} Новое сообщение
        {new_system_message} Системное сообщение
        {new_order} Новый заказ
        {order_status_changed} Статус заказа изменился
        {new_review} Новый отзыв
        {ticket_created} Тикет создан
    """)
    return txt


def notifications_kb():
    config = sett.get("config")
    
    enabled = "✅" if config["funpay"]["notifications"]["enabled"] else "❌"
    chat_id = config["funpay"]["notifications"]["chat_id"] or "Текущий"
    events = config["funpay"]["notifications"]["events"] or {}

    new_user_message = "🟢" if events["new_user_message"] else "🔴"
    new_system_message = "🟢" if events["new_system_message"] else "🔴"
    new_order = "🟢" if events["new_order"] else "🔴"
    order_status_changed = "🟢" if events["order_status_changed"] else "🔴"
    new_review = "🟢" if events["new_review"] else "🔴"
    ticket_created = "🟢" if events["ticket_created"] else "🔴"
    
    rows = [
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_notifications_enabled")],
        [InlineKeyboardButton(text=f"💬 Чат: {chat_id}", callback_data="enter_notifications_chat_id")],
        [InlineKeyboardButton(text=f"{new_user_message} Новое сообщение", callback_data="switch_notifications_event_new_user_message")],
        [InlineKeyboardButton(text=f"{new_system_message} Системное сообщение", callback_data="switch_notifications_event_new_system_message")],
        [InlineKeyboardButton(text=f"{new_order} Новый заказ", callback_data="switch_notifications_event_new_order")],
        [InlineKeyboardButton(text=f"{order_status_changed} Статус заказа изменился", callback_data="switch_notifications_event_order_status_changed")],
        [InlineKeyboardButton(text=f"{new_review} Новый отзыв", callback_data="switch_notifications_event_new_review")],
        [InlineKeyboardButton(text=f"{ticket_created} Тикет создан", callback_data="switch_notifications_event_ticket_created")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    
    if config["funpay"]["notifications"]["chat_id"]:
        rows[1].append(InlineKeyboardButton(text=f"❌ Очистить", callback_data="clean_notifications_chat_id"))
    
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def notifications_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔔 Уведомления</b>
        \n{placeholder}
    """)
    return txt