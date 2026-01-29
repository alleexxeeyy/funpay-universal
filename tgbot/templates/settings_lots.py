import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_lots_text():
    config = sett.get("config")
    auto_raise_lots_enabled = "🟢 Включено" if config["funpay"]["auto_raise_lots"]["enabled"] else "🔴 Выключено"

    txt = textwrap.dedent(f"""
        <b>📄 Лоты</b>

        <b>⬆️ Авто-поднятие лотов:</b> {auto_raise_lots_enabled}
    """)
    return txt


def settings_lots_kb():
    config = sett.get("config")
    auto_raise_lots_enabled = "🟢 Включено" if config["funpay"]["auto_raise_lots"]["enabled"] else "🔴 Выключено"
    
    rows = [
        [InlineKeyboardButton(text=f"⬆️ Авто-поднятие лотов: {auto_raise_lots_enabled}", callback_data="switch_auto_raise_lots_enabled")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_lots_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>⬆️ Поднятие лотов</b>
        \n{placeholder}
    """)
    return txt