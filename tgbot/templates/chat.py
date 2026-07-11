from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import escape_html
from FunPayAPI.types import Chat

from .. import callback_datas as calls


def chat_text(chat: Chat, msgs=None):
    from fpbot.funpaybot import get_funpay_bot as fpbot
    acc = fpbot().account

    msgs = msgs if msgs is not None else (chat.messages or [])
    shown = list(msgs)[-15:]

    msgs_frmtd = ""
    for msg in shown:
        author = msg.author or "FunPay"
        if msg.author_id == acc.id:
            username = "Вы"
        elif msg.author_id == 0:
            username = "FunPay"
        else:
            username = escape_html(author)

        if msg.image_link:
            msg_text = f'<a href="{msg.image_link}"><i>*Изображение*</i></a>'
        elif msg.text:
            msg_text = escape_html(msg.text)
        else:
            msg_text = "<i>*Без текста*</i>"

        by_bot_mark = " 🤖" if getattr(msg, "by_bot", False) else ""
        msgs_frmtd += f"<b>{username}{by_bot_mark}:</b> <blockquote>{msg_text}</blockquote>\n\n"

    msgs_frmtd = msgs_frmtd.strip()
    if not msgs_frmtd:
        msgs_frmtd = "<i>История пуста</i>"

    looking = ""
    if getattr(chat, "looking_text", None):
        looking = f"\n👀 Смотрит: <i>{escape_html(chat.looking_text)}</i>"

    header = f"<b>💬 Чат с {escape_html(chat.name or '?')}</b>{looking}"
    return f"{header}\n\n{msgs_frmtd}"


def chat_kb(chat: Chat, last_page=0):
    rows = [
        [
            InlineKeyboardButton(text="✏️ Ответить", callback_data="enter_chat_message"),
            InlineKeyboardButton(text="⚡ Быстрый ответ", callback_data=calls.SelFastReplyPagination(id=chat.id, page=last_page).pack()),
        ],
        [InlineKeyboardButton(text="💬 На сайте", url=f"https://funpay.com/chat/?node={chat.id}")],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ChatsPagination(page=last_page).pack()),
            InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ChatPage(id=str(chat.id)).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def chat_float_text(chat: Chat, placeholder: str):
    name = escape_html(chat.name or "?") if chat else "?"
    return f"<b>💬 Чат с {name}</b>\n\n{placeholder}"
