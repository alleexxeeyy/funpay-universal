import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_delivs_text():
    auto_deliveries = sett.get("auto_deliveries")
    txt = textwrap.dedent(f"""
        <b>🚀 Авто-выдача</b>

        Всего <b>{len(auto_deliveries)}</b> лотов с авто-выдачей:
    """)
    return txt


def settings_delivs_kb(page: int = 0):
    from fpbot.funpaybot import get_funpay_bot
    auto_deliveries = sett.get("auto_deliveries")
    try:
        user = get_funpay_bot().account.get_user(get_funpay_bot().account.id)
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
        try: lot_title = [lot for lot in lots if int(lot.id) == int(lot_id)][0].title
        except: lot_title = lot_id
        lot_title_frmtd = lot_title[:48] + ("..." if len(lot_title) > 48 else "")
        auto_delivery_text = "\n".join(auto_deliveries[lot_id])
        rows.append([InlineKeyboardButton(
            text=f"«{lot_title_frmtd}» → {auto_delivery_text}", 
            callback_data=calls.AutoDeliveryPage(lot_id=lot_id).pack()
        )])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.AutoDeliveriesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_auto_deliveries_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.AutoDeliveriesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)
        
    rows.append([InlineKeyboardButton(text="➕ Добавить", callback_data="enter_new_auto_delivery_lot_link")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_delivs_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🚀 Авто-выдача</b>
        \n{placeholder}
    """)
    return txt


def settings_new_deliv_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>➕🚀 Добавление авто-выдачи</b>
        \n{placeholder}
    """)
    return txt