import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def delivs_text():
    auto_deliveries = sett.get("auto_deliveries")
    txt = textwrap.dedent(f"""
        <b>🚀 Авто-выдача</b>
        Всего <b>{len(auto_deliveries)}</b> лотов с авто-выдачей:
    """)
    return txt


def delivs_kb(page: int = 0):
    auto_deliveries = sett.get("auto_deliveries")
    
    try:
        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account
        user = acc.get_user(acc.id)
        lots = user.get_lots()
    except:
        lots = []

    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(auto_deliveries.keys()) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for lot_id in list(auto_deliveries.keys())[start_offset:end_offset]:
        lot_title = "❌"
        lot = next((lot for lot in lots if int(lot.id) == int(lot_id)), None)
        if lot:
            lot_title = lot.title
        
        lot_title_frmtd = lot_title[:48] + ("..." if len(lot_title) > 48 else "")
        auto_delivery_text = "\n".join(auto_deliveries[lot_id])
        
        rows.append([InlineKeyboardButton(
            text=f"«{lot_title_frmtd}» → {auto_delivery_text}", 
            callback_data=calls.AutoDeliveryPage(lot_id=lot_id).pack()
        )])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.AutoDeliveriesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.AutoDeliveriesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)
        
    rows.append([InlineKeyboardButton(text="➕ Добавить", callback_data="enter_new_auto_delivery_lot_link")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def delivs_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🚀 Авто-выдача</b>
        \n{placeholder}
    """)
    return txt


def new_deliv_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>➕🚀 Добавление авто-выдачи</b>
        \n{placeholder}
    """)
    return txt