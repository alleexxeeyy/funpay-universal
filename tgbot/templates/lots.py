import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import escape_html
from FunPayAPI.types import MyLotShortcut, LotShortcut

from .. import callback_datas as calls


def _get_lot_info(lot):
    title = escape_html(lot.description or "?")
    title = title[:40] + ("..." if len(title) > 40 else "")
    price = f"{lot.price} {lot.currency}" if lot.currency else str(lot.price)
    active_sym = "🟢" if getattr(lot, "active", True) else "🔴"
    auto_sym = " 🤖" if getattr(lot, "auto", False) else ""
    return title, price, active_sym, auto_sym


def lots_text(lots: list, page=0):
    items_per_page = 12

    total_pages = math.ceil(len(lots) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    lots_frmtd = ""
    for lot in list(lots)[start_offset:end_offset]:
        title, price, sym, auto = _get_lot_info(lot)
        lots_frmtd += f"<b>{sym} {title}{auto}</b> ・ {price}\n\n"

    lots_frmtd = lots_frmtd.strip()
    if not lots_frmtd:
        lots_frmtd = "Лотов не найдено. Попробуйте обновить страницу"

    return f"<b>🛍️ Лоты</b>\n\n{lots_frmtd}"


def lots_kb(lots: list, page=0):
    rows = []
    items_per_page = 12
    items_per_row = 2

    total_pages = math.ceil(len(lots) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for lot in list(lots)[start_offset:end_offset]:
        title, price, sym, auto = _get_lot_info(lot)
        dynamic_btns.append(InlineKeyboardButton(
            text=f"{sym} {title}",
            callback_data=calls.LotPage(id=str(lot.id)).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.LotsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.LotsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="🛍️ На сайте", url="https://funpay.com/lots/trade")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.LotsPagination(page=page, upd=True).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def lots_float_text(placeholder):
    return f"<b>🛍️ Лоты</b>\n\n{placeholder}"
