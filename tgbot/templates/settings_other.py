import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_other_text():
    config = sett.get("config")
    
    auto_review_replies_enabled = "🟢 Включено" if config["funpay"]["auto_review_replies"]["enabled"] else "🔴 Выключено"
    custom_commands_enabled = "🟢 Включено" if config["funpay"]["custom_commands"]["enabled"] else "🔴 Выключено"
    auto_deliveries_enabled = "🟢 Включено" if config["funpay"]["auto_deliveries"]["enabled"] else "🔴 Выключено"
    watermark_enabled = "🟢 Включено" if config["funpay"]["watermark"]["enabled"] else "🔴 Выключено"
    watermark_value = config["funpay"]["watermark"]["value"] or "❌ Не задано"
    
    txt = textwrap.dedent(f"""
        <b>🔧 Прочее</b>

        <b>💬 Авто-ответы на отзывы:</b> {auto_review_replies_enabled}
        <b>❗ Команды:</b> {custom_commands_enabled}
        <b>🚀 Авто-выдача:</b> {auto_deliveries_enabled}
        
        <b>©️ Водяной знак под сообщениями:</b> {watermark_enabled}
        <b>✍️©️ Водяной знак:</b> {watermark_value}
    """)
    return txt


def settings_other_kb():
    config = sett.get("config")
    
    auto_review_replies_enabled = "🟢 Включено" if config["funpay"]["auto_review_replies"]["enabled"] else "🔴 Выключено"
    custom_commands_enabled = "🟢 Включено" if config["funpay"]["custom_commands"]["enabled"] else "🔴 Выключено"
    auto_deliveries_enabled = "🟢 Включено" if config["funpay"]["auto_deliveries"]["enabled"] else "🔴 Выключено"
    watermark_enabled = "🟢 Включено" if config["funpay"]["watermark"]["enabled"] else "🔴 Выключено"
    watermark_value = config["funpay"]["watermark"]["value"] or "❌ Не задано"

    rows = [
        [InlineKeyboardButton(text=f"💬 Авто-ответы на отзывы: {auto_review_replies_enabled}", callback_data="switch_auto_review_replies_enabled")],
        [InlineKeyboardButton(text=f"❗ Команды: {custom_commands_enabled}", callback_data="switch_custom_commands_enabled")],
        [InlineKeyboardButton(text=f"🚀 Авто-выдача: {auto_deliveries_enabled}", callback_data="switch_auto_deliveries_enabled")],
        [InlineKeyboardButton(text=f"©️ Водяной знак под сообщениями: {watermark_enabled}", callback_data="switch_watermark_enabled")],
        [InlineKeyboardButton(text=f"✍️©️ Водяной знак: {watermark_value}", callback_data="enter_watermark_value")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_other_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔧 Прочее</b>
        \n{placeholder}
    """)
    return txt