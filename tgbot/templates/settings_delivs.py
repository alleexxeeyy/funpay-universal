import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_delivs_text():
    auto_deliveries = sett.get("auto_deliveries")
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → 🚀 <b>Авто-выдача</b>
        Всего <b>{len(auto_deliveries.keys())}</b> настроенных лотов для авто-выдачи в конфиге

        Перемещайтесь по разделам ниже. Нажмите на ID лота, чтобы перейти в редактирование его авто-выдачи ↓
    """)
    return txt


def settings_delivs_kb(page: int = 0):
    auto_deliveries = sett.get("auto_deliveries")
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(auto_deliveries.keys()) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for lot_id in list(auto_deliveries.keys())[start_offset:end_offset]:
        auto_delivery_text = "\n".join(auto_deliveries[lot_id])
        rows.append([InlineKeyboardButton(text=f"{lot_id} → {auto_delivery_text}", callback_data=calls.AutoDeliveryPage(lot_id=lot_id).pack())])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.AutoDeliveriesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_auto_deliveries_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.AutoDeliveriesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        
        rows.append(buttons_row)
        
    rows.append([InlineKeyboardButton(text="➕🚀 Добавить", callback_data="enter_new_auto_delivery_lot_id")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.AutoDeliveriesPagination(page=page).pack())
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_delivs_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ⌨️ <b>Авто-выдача</b>
        \n{placeholder}
    """)
    return txt


def settings_new_deliv_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        🚀 <b>Добавление пользовательской авто-выдачи</b>
        \n{placeholder}
    """)
    return txt


def settings_deliv_page_text(lot_id: int):
    auto_deliveries = sett.get("auto_deliveries")
    auto_delivery_message = "\n".join(auto_deliveries[str(lot_id)]) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование авто-выдачи</b>

        🆔 <b>ID лота:</b> {lot_id}
        💬 <b>Сообщение:</b> 
        <blockquote>{auto_delivery_message}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_deliv_page_kb(lot_id: int, page: int = 0):
    auto_deliveries = sett.get("auto_deliveries")
    auto_delivery_message = "\n".join(auto_deliveries[str(lot_id)]) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"💬 Сообщение: {auto_delivery_message}", callback_data="enter_auto_delivery_message")],
        [InlineKeyboardButton(text="🗑️ Удалить авто-выдачу", callback_data="confirm_deleting_auto_delivery")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.AutoDeliveriesPagination(page=page).pack()), 
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.AutoDeliveryPage(lot_id=lot_id).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_deliv_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование авто-выдачи</b>
        \n{placeholder}
    """)
    return txt