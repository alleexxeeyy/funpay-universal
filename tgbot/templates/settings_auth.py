import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_auth_text():
    config = sett.get("config")
    golden_key = (config["funpay"]["api"]["golden_key"][:5] + "*" * 5) or "❌ Не задано"
    user_agent = config["funpay"]["api"]["user_agent"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 🔑 Авторизация</b>

        🔑 <b>golden_key:</b> {golden_key}
        🎩 <b>user_agent:</b> {user_agent}

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_auth_kb():
    config = sett.get("config")
    golden_key = (config["funpay"]["api"]["golden_key"][:5] + "*" * 5) or "❌ Не задано"
    user_agent = config["funpay"]["api"]["user_agent"] or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"🔑 golden_key: {golden_key}", callback_data="enter_golden_key")],
        [InlineKeyboardButton(text=f"🎩 user_agent: {user_agent}", callback_data="enter_user_agent")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="authorization").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_auth_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 🔑 Авторизация</b>
        \n{placeholder}
    """)
    return txt