import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_mess_text():
    messages = sett.get("messages")
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ✉️ <b>Сообщения</b>
        Всего <b>{len(messages.keys())}</b> настраиваемых сообщений в конфиге

        Перемещайтесь по разделам ниже. Нажмите на сообщение, чтобы перейти в его редактирование ↓
    """)
    return txt


def settings_mess_kb(page: int = 0):
    messages = sett.get("messages")
    rows = []
    items_per_page = 8
    total_pages = math.ceil(len(messages.keys()) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for mess_id, info in list(messages.items())[start_offset:end_offset]:
        enabled = "🟢" if info["enabled"] else "🔴"
        text_joined = "\n".join(info["text"])
        rows.append([InlineKeyboardButton(text=f"{enabled} {mess_id} | {text_joined}", callback_data=calls.MessagePage(message_id=mess_id).pack())])

    if total_pages > 1:
        buttons_row = []
        
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.MessagesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_messages_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.MessagesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)

        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
                 InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MessagesPagination(page=page).pack())])
    
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_mess_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ✉️ <b>Сообщения</b>
        \n{placeholder}
    """)
    return txt


def settings_mess_page_text(message_id: int):
    messages = sett.get("messages")
    enabled = "🟢 Включено" if messages[message_id]["enabled"] else "🔴 Выключено"
    message_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✒️ <b>Редактирование сообщения</b>

        🆔 <b>ID сообщения:</b> {message_id}
        💡 <b>Состояние:</b> {enabled}
        💬 <b>Текст сообщения:</b> <blockquote>{message_text}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_mess_page_kb(message_id: int, page: int = 0):
    messages = sett.get("messages")
    enabled = "🟢 Включено" if messages[message_id]["enabled"] else "🔴 Выключено"
    message_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"💡 Состояние: {enabled}", callback_data="switch_message_enabled")],
        [InlineKeyboardButton(text=f"💬 Текст сообщения: {message_text}", callback_data="enter_message_text")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MessagesPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MessagePage(message_id=message_id).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_mess_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ✒️ <b>Редактирование сообщения</b>
        \n{placeholder}
    """)
    return txt