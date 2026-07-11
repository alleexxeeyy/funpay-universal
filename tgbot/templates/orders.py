import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import escape_html
from FunPayAPI.types import OrderShortcut
from FunPayAPI.common.enums import OrderStatuses

from .. import callback_datas as calls


def _status_info(status: OrderStatuses):
    if status == OrderStatuses.PAID:
        return "🟢", "Оплачен"
    elif status == OrderStatuses.CLOSED:
        return "🔵", "Закрыт"
    elif status == OrderStatuses.REFUNDED:
        return "🟠", "Возврат"
    elif status == OrderStatuses.PARTIALLY_REFUNDED:
        return "🟠", "Частичный возврат"
    elif status == OrderStatuses.UNPAID:
        return "🔴", "Не оплачен"
    return "⚪", "Неизвестно"


def _get_order_info(order: OrderShortcut):
    username = escape_html(order.buyer_username or "?")
    desc = escape_html(order.description or "")
    desc = desc[:48] + ("..." if len(desc) > 48 else "")
    sym, status_str = _status_info(order.status)
    price = f"{order.price} {order.currency}" if order.currency else str(order.price)
    return username, desc, price, status_str, sym


def orders_text(orders: list[OrderShortcut], page=0):
    items_per_page = 12

    total_pages = math.ceil(len(orders) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    orders_frmtd = ""
    for order in list(orders)[start_offset:end_offset]:
        username, desc, price, status_str, sym = _get_order_info(order)
        orders_frmtd += (
            f"<b>{sym} #{order.id} ・ {username}</b> ・ {status_str} ・ {price}"
            f"\n      ┗ {desc}\n\n"
        )

    orders_frmtd = orders_frmtd.strip()
    if not orders_frmtd:
        orders_frmtd = "Нет заказов по заданным фильтрам. Попробуйте обновить страницу"

    return f"<b>📋 Заказы</b>\n\n{orders_frmtd}"


def orders_kb(orders: list[OrderShortcut], page=0):
    rows = []
    items_per_page = 12
    items_per_row = 1

    total_pages = math.ceil(len(orders) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for order in list(orders)[start_offset:end_offset]:
        username, desc, _, _, sym = _get_order_info(order)
        dynamic_btns.append(InlineKeyboardButton(
            text=f"{sym} #{order.id} ・ {username} ・ {desc}",
            callback_data=calls.OrderPage(id=str(order.id)).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.OrdersPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.OrdersPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="✨ Фильтр", callback_data="orders_filter"),
        InlineKeyboardButton(text="📋 На сайте", url="https://funpay.com/orders/trade")
    ])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.OrdersPagination(page=page, upd=True).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def orders_float_text(placeholder):
    return f"<b>📋 Заказы</b>\n\n{placeholder}"
