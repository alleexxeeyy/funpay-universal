import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import callback_datas as calls


def profile_text():
    from fpbot.funpaybot import get_funpay_bot as fpbot
    
    acc = fpbot().account
    profile = acc.get_user(acc.id)
    
    txt = textwrap.dedent(f"""
        <b>👤 Мой профиль</b>

        <b>🆔 ID:</b> {profile.id}
        <b>🏷️ Никнейм:</b> {profile.username} <a href="{profile.profile_photo}">(аватар)</a>
        <b>💰 Баланс:</b> {acc.total_balance} {acc.currency.name}

        <b>📝 Активные лоты:</b> {len(profile.get_lots())}
        <b>🛍️ Активные покупки:</b> {acc.active_purchases}
        <b>🛒 Активные продажи:</b> {acc.active_sales}
    """)
    return txt


def profile_kb():
    rows = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb