import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import escape_html
from FunPayAPI.types import Order
from FunPayAPI.common.enums import OrderStatuses

from .. import callback_datas as calls


def _status_str(status: OrderStatuses):
    if status == OrderStatuses.PAID: return "🟢 Оплачен"
    elif status == OrderStatuses.CLOSED: return "🔵 Закрыт"
    elif status == OrderStatuses.REFUNDED: return "🟠 Возврат"
    elif status == OrderStatuses.PARTIALLY_REFUNDED: return "🟠 Частичный возврат"
    elif status == OrderStatuses.UNPAID: return "🔴 Не оплачен"
    return "⚪ Неизвестно"


def order_text(order: Order, date=None):
    from fpbot.funpaybot import get_funpay_bot as fpbot
    acc = fpbot().account

    buyer = escape_html(order.buyer_username or "?")
    buyer += " (Вы)" if order.buyer_id == acc.id else ""

    desc = escape_html(order.subcategory.name) if order.subcategory and order.subcategory.name else "?"
    price = f"{order.sum} {order.currency}" if order.currency else str(order.sum)
    status = _status_str(order.status)

    server = escape_html(order.server.name) if order.server and order.server.name else "-"
    side = escape_html(order.side.name) if order.side and order.side.name else "-"
    player = escape_html(order.player) if order.player else "-"
    amount = order.amount or "?"

    fields_str = ""
    if order.fields:
        fields_str = "<b>📝 Поля:</b>"
        for key, f in order.fields.items():
            fname = escape_html(f.name) if f.name else escape_html(key)
            fval = f.value
            if isinstance(fval, dict):
                fval = ", ".join(str(v) for v in fval.values())
            fval = escape_html(str(fval)) if fval is not None else "-"
            fields_str += f"\n・ <b>{fname}:</b> {fval}"

    secrets_str = ""
    if order.order_secrets:
        secrets_str = "<b>🔐 Авто-выдача:</b>"
        for s in order.order_secrets:
            secrets_str += f"\n・ <code>{escape_html(s)}</code>"

    review_str = ""
    if order.review:
        stars = "⭐" * (order.review.stars or 0)
        author = escape_html(order.review.author or "Аноним")
        text = escape_html(order.review.text or "") if order.review.text else "<i>Без текста</i>"
        review_str = f"<b>🌟 Отзыв от {author}:</b> {stars}\n<blockquote>{text}</blockquote>"
        if order.review.reply:
            review_str += f"\n<b>↩️ Ваш ответ:</b>\n<blockquote>{escape_html(order.review.reply)}</blockquote>"

    date_str = ""
    if date is not None:
        try:
            date_str = f"<b>📅 Дата:</b> {date.astimezone(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M')}"
        except Exception:
            date_str = f"<b>📅 Дата:</b> {date}"

    groups = []

    groups.append(
        f"<b>👤 Покупатель:</b> {buyer}\n"
        f"<b>🏷️ Статус:</b> {status}"
    )

    groups.append(
        f"<b>🛍️ Товар:</b> {desc}\n"
        f"<b>💰 Сумма:</b> {price}\n"
        f"<b>🛒 Кол-во:</b> {amount}"
    )

    groups.append(
        f"<b>🎮 Сервер:</b> {server} ・ <b>Сторона:</b> {side}\n"
        f"<b>👤 Персонаж:</b> {player}"
    )

    if fields_str:
        groups.append(fields_str)
    if secrets_str:
        groups.append(secrets_str)
    if review_str:
        groups.append(review_str)
    if date_str:
        groups.append(date_str)

    return f"<b>📄📋 Заказ #{order.id}</b>\n\n" + "\n\n".join(groups)


def order_kb(order: Order, last_page=0):
    rows = []

    if order.status == OrderStatuses.PAID:
        rows.append([InlineKeyboardButton(
            text="📦 Возврат",
            callback_data=calls.RefundOrder(id=str(order.id)).pack()
        )])

    rows.append([
        InlineKeyboardButton(text="💬 Открыть чат", callback_data=calls.ChatPage(id=str(order.chat_id)).pack()),
        InlineKeyboardButton(text="📋 На сайте", url=f"https://funpay.com/orders/{order.id}/")
    ])

    if order.review:
        if not order.review.reply:
            rows.append([InlineKeyboardButton(
                text="↩️ Ответить на отзыв",
                callback_data=calls.AnswerOrderReview(id=str(order.id)).pack()
            )])
        else:
            rows.append([InlineKeyboardButton(
                text="🗑 Удалить ответ",
                callback_data=calls.DeleteOrderReview(id=str(order.id)).pack()
            )])

    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.OrdersPagination(page=last_page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.OrderPage(id=str(order.id)).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def order_float_text(placeholder):
    return f"<b>📄📋 Страница заказа</b>\n\n{placeholder}"
