import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import escape_html
from FunPayAPI.types import ChatShortcut

from .. import callback_datas as calls


def _get_chat_info(chat: ChatShortcut):
    from fpbot.funpaybot import get_funpay_bot as fpbot

    name = chat.name or "Без названия"
    username = f"👤 {name}"
    if chat.unread:
        username = f"{username} 🔹"

    last_msg = chat.last_message_text or "<i>*Без сообщения*</i>"
    last_msg = escape_html(last_msg.replace("\n", " ")) if last_msg else ""
    last_msg = last_msg[:48] + ("..." if len(last_msg) > 48 else "")

    return username, last_msg


def chats_text(chats: list[ChatShortcut], page=0):
    items_per_page = 12

    total_pages = math.ceil(len(chats) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    chats_frmtd = ""
    for chat in list(chats)[start_offset:end_offset]:
        username, msg = _get_chat_info(chat)
        chats_frmtd += (
            f"<b>{username}</b>"
            f"\n      ┗ {msg}\n\n"
        )

    chats_frmtd = chats_frmtd.strip()
    if not chats_frmtd:
        chats_frmtd = "Не найдено чатов. Попробуйте обновить страницу"

    return f"<b>💬 Чаты</b>\n\n{chats_frmtd}"


def chats_kb(chats: list[ChatShortcut], page=0):
    rows = []
    items_per_page = 12
    items_per_row = 2

    total_pages = math.ceil(len(chats) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for chat in list(chats)[start_offset:end_offset]:
        username, _ = _get_chat_info(chat)
        dynamic_btns.append(InlineKeyboardButton(
            text=f"{username}",
            callback_data=calls.ChatPage(id=str(chat.id)).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.ChatsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.ChatsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="💬 На сайте", url="https://funpay.com/chat/")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ChatsPagination(page=page, upd=True).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def chats_float_text(placeholder):
    return f"<b>💬 Чаты</b>\n\n{placeholder}"
