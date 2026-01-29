import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import callback_datas as calls


def profile_text():
    from fpbot.funpaybot import get_funpay_bot
    account = get_funpay_bot().funpay_account
    profile = account.get_user(account.id)
    txt = textwrap.dedent(f"""
        <b>👤 Мой профиль</b>

        <b>🆔 ID:</b> {profile.id}
        <b>🏷️ Никнейм:</b> {profile.username}
        <b>💰 Баланс:</b> {account.total_balance} {account.currency.name}

        <b>📄 Активные лоты:</b> {len(profile.get_lots())}
        <b>🛍️ Активные покупки:</b> {account.active_purchases}
        <b>🛒 Активные продажи:</b> {account.active_sales}
    """)
    return txt


def profile_kb():
    rows = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb