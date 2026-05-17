import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def other_text():
    config = sett.get("config")
    
    auto_raise_lots_enabled = "✅" if config["funpay"]["auto_raise_lots"] else "❌"
    auto_review_replies_enabled = "✅" if config["funpay"]["auto_review_replies"] else "❌"
    watermark_enabled = "✅" if config["funpay"]["watermark"]["enabled"] else "❌"
    watermark_value = config["funpay"]["watermark"]["value"] or "❌ Не задано"
    
    txt = textwrap.dedent(f"""
        <b>🔧 Прочее</b>

        <b>⬆️ Авто-поднятие лотов:</b> {auto_raise_lots_enabled}
        <b>💬 Авто-ответы на отзывы:</b> {auto_review_replies_enabled}
        
        <b>©️ Водяной знак:</b> {watermark_enabled}
        <b>🏷️©️ Значение:</b> {watermark_value}
    """)
    return txt


def other_kb():
    config = sett.get("config")
    
    auto_raise_lots_enabled = "✅" if config["funpay"]["auto_raise_lots"] else "❌"
    auto_review_replies_enabled = "✅" if config["funpay"]["auto_review_replies"] else "❌"
    watermark_enabled = "✅" if config["funpay"]["watermark"]["enabled"] else "❌"
    watermark_value = config["funpay"]["watermark"]["value"] or "❌ Не задано"

    rows = [
        [InlineKeyboardButton(text=f"⬆️ Авто-поднятие лотов: {auto_raise_lots_enabled}", callback_data="switch_auto_raise_lots_enabled")],
        [InlineKeyboardButton(text=f"💬 Авто-ответы на отзывы: {auto_review_replies_enabled}", callback_data="switch_auto_review_replies_enabled")],
        [InlineKeyboardButton(text=f"©️ Водяной знак: {watermark_enabled}", callback_data="switch_watermark_enabled")],
        [InlineKeyboardButton(text=f"🏷️©️ Значение: {watermark_value}", callback_data="enter_watermark_value")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def other_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔧 Прочее</b>
        \n{placeholder}
    """)
    return txt