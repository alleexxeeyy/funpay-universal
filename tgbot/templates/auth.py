import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def auth_text():
    config = sett.get("config")
    
    golden_key = (config["funpay"]["api"]["golden_key"][:5] + "*****") or "❌ Не задано"
    user_agent = config["funpay"]["api"]["user_agent"] or "❌ Не задано"
    
    txt = textwrap.dedent(f"""
        <b>🔒 Авторизация</b>

        <b>🔑 Golden Key:</b> {golden_key}
        <b>🎩 User Agent:</b> {user_agent}
    """)
    return txt


def auth_kb():
    config = sett.get("config")
    
    golden_key = (config["funpay"]["api"]["golden_key"][:5] + "*" * 5) or "❌ Не задано"
    user_agent = config["funpay"]["api"]["user_agent"] or "❌ Не задано"
    
    rows = [
        [InlineKeyboardButton(text=f"🔑 Golden Key: {golden_key}", callback_data="enter_golden_key")],
        [InlineKeyboardButton(text=f"🎩 User Agent: {user_agent}", callback_data="enter_user_agent")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def auth_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔒 Авторизация</b>
        \n{placeholder}
    """)
    return txt