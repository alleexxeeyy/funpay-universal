import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_other_text():
    config = sett.get("config")
    auto_reviews_replies_enabled = "🟢 Включено" if config["funpay"]["auto_reviews_replies"]["enabled"] else "🔴 Выключено"
    custom_commands_enabled = "🟢 Включено" if config["funpay"]["custom_commands"]["enabled"] else "🔴 Выключено"
    auto_deliveries_enabled = "🟢 Включено" if config["funpay"]["auto_deliveries"]["enabled"] else "🔴 Выключено"
    watermark_enabled = "🟢 Включено" if config["funpay"]["watermark"]["enabled"] else "🔴 Выключено"
    watermark_value = config["funpay"]["watermark"]["value"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 🔧 Прочее</b>

        💬 <b>Авто-ответы на отзывы:</b> {auto_reviews_replies_enabled}
        🔧 <b>Пользовательские команды:</b> {custom_commands_enabled}
        🚀 <b>Авто-выдача:</b> {auto_deliveries_enabled}
        ©️ <b>Водяной знак под сообщениями:</b> {watermark_enabled}
        ✍️©️ <b>Водяной знак:</b> {watermark_value}

        <b>Что такое автоматические ответы на отзывы?</b>
        Когда покупатель будет оставлять отзыв, бот будет автоматически отвечать на него. В ответе на отзыв будут написаны детали заказа.

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_other_kb():
    config = sett.get("config")
    auto_reviews_replies_enabled = "🟢 Включено" if config["funpay"]["auto_reviews_replies"]["enabled"] else "🔴 Выключено"
    custom_commands_enabled = "🟢 Включено" if config["funpay"]["custom_commands"]["enabled"] else "🔴 Выключено"
    auto_deliveries_enabled = "🟢 Включено" if config["funpay"]["auto_deliveries"]["enabled"] else "🔴 Выключено"
    watermark_enabled = "🟢 Включено" if config["funpay"]["watermark"]["enabled"] else "🔴 Выключено"
    watermark_value = config["funpay"]["watermark"]["value"] or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"💬 Авто-ответы на отзывы: {auto_reviews_replies_enabled}", callback_data="switch_other|auto_reviews_replies|enabled")],
        [InlineKeyboardButton(text=f"🔧 Пользовательские команды: {custom_commands_enabled}", callback_data="switch_other|custom_commands|enabled")],
        [InlineKeyboardButton(text=f"🚀 Авто-выдача: {auto_deliveries_enabled}", callback_data="switch_other|auto_deliveries|enabled")],
        [InlineKeyboardButton(text=f"©️ Водяной знак под сообщениями: {watermark_enabled}", callback_data="switch_other|watermark|enabled")],
        [InlineKeyboardButton(text=f"✍️©️ Водяной знак: {watermark_value}", callback_data="enter_watermark_value")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="other").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_other_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 🔧 Прочее</b>
        \n{placeholder}
    """)
    return txt