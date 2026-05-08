import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from FunPayAPI.types import LotFields
from settings import Settings as sett

from .. import callback_datas as calls


def deliv_page_text(lot_id: int, lot: LotFields):
    auto_deliveries = sett.get("auto_deliveries")
    
    auto_delivery_message = "\n".join(auto_deliveries[str(lot_id)]) or "❌ Не задано"
    try: lot_title = lot.title_ru
    except: lot_title = lot_id
    
    txt = textwrap.dedent(f"""
        <b>📄🚀 Страница авто-выдачи</b>

        <b>📄 Лот:</b> <a href="https://funpay.com/lots/offer?id={lot_id}/">{lot_title}</a>
        <b>💬 Сообщение:</b> <blockquote>{auto_delivery_message}</blockquote>
    """)
    return txt


def deliv_page_kb(lot_id: int, lot: LotFields, page=0):
    auto_deliveries = sett.get("auto_deliveries")
    
    auto_delivery_message = "\n".join(auto_deliveries[str(lot_id)]) or "❌ Не задано"
    try: lot_title = lot.title_ru
    except: lot_title = lot_id
    
    rows = [
        [InlineKeyboardButton(text=f"📄 Лот: {lot_title}", callback_data="enter_auto_delivery_lot_link")],
        [InlineKeyboardButton(text=f"💬 Сообщение: {auto_delivery_message}", callback_data="enter_auto_delivery_message")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data="confirm_deleting_auto_delivery")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.AutoDeliveriesPagination(page=page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def deliv_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📄🚀 Страница авто-выдачи</b>
        \n{placeholder}
    """)
    return txt