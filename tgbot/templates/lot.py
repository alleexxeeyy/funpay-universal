from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import escape_html
from FunPayAPI.types import LotFields

from .. import callback_datas as calls


def lot_text(lf: LotFields):
    title = lf.title_ru or lf.title_en or ""
    if not title:
        title = lf.subcategory.name if lf.subcategory and lf.subcategory.name else "?"
    title = escape_html(title)

    desc = lf.description_ru or lf.description_en or ""
    desc = escape_html(desc) if desc else "-"
    price = f"{lf.price} {lf.currency}" if lf.currency else str(lf.price)
    active = "🟢 Активен" if lf.active else "🔴 Выключен"
    amount = lf.amount or "?"

    subcat = "-"
    if lf.subcategory:
        subcat = escape_html(getattr(lf.subcategory, "ui_name", None) or lf.subcategory.name or "-")
    auto = "✅ Да" if lf.auto_delivery else "❌ Нет"

    secrets_str = ""
    if lf.secrets:
        secrets_str = "<b>🔐 Авто-выдача:</b>"
        for s in lf.secrets:
            secrets_str += f"\n・ <code>{escape_html(s)}</code>"

    groups = [
        f"<b>🏷️ Название:</b> {title}",
        f"<b>📂 Категория:</b> {subcat}",
        f"<b>💰 Цена:</b> {price}\n<b>🛒 Кол-во:</b> {amount}\n<b>🤖 Авто-выдача:</b> {auto}",
        f"<b>👀 Статус:</b> {active}",
        f"<b>📃 Описание:</b>\n<blockquote>{desc}</blockquote>",
    ]
    if secrets_str:
        groups.append(secrets_str)

    return f"<b>📄🛍️ Лот #{lf.lot_id}</b>\n\n" + "\n\n".join(groups)


def lot_kb(lf: LotFields, last_page=0):
    rows = []

    rows.append([
        InlineKeyboardButton(
            text="🔴 Выключить" if lf.active else "🟢 Включить",
            callback_data=calls.ToggleLotActive(id=str(lf.lot_id)).pack()
        ),
        InlineKeyboardButton(text="✏️ Цена", callback_data=calls.EditLotPrice(id=str(lf.lot_id)).pack()),
    ])
    rows.append([
        InlineKeyboardButton(text="✏️ Описание", callback_data=calls.EditLotDescription(id=str(lf.lot_id)).pack()),
        InlineKeyboardButton(text="🗑 Удалить", callback_data=calls.DeleteLot(id=str(lf.lot_id)).pack()),
    ])
    rows.append([InlineKeyboardButton(text="🛍️ На сайте", url=f"https://funpay.com/lots/offerEdit?offer={lf.lot_id}")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.LotsPagination(page=last_page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.LotPage(id=str(lf.lot_id)).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def lot_float_text(placeholder):
    return f"<b>📄🛍️ Лот</b>\n\n{placeholder}"
