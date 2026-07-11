from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import get_event_next_time

from .. import callback_datas as calls


WALLETS = [
    ("CARD_RUB", "💳 Карта ₽"),
    ("CARD_USD", "💳 Карта $"),
    ("CARD_EUR", "💳 Карта €"),
    ("TRC", "💲 USDT TRC20"),
    ("YOUMONEY", "🟡 ЮMoney"),
    ("QIWI", "🟧 QIWI"),
    ("BINANCE", "🟦 Binance"),
    ("WEBMONEY", "🟪 WebMoney"),
]


def withdrawal_text():
    config = sett.get("config")
    wd = config["funpay"]["auto_withdrawal"]

    enabled = "✅" if wd["enabled"] else "❌"
    interval = wd["interval"]
    wallet_type = wd["wallet_type"]
    wallet_label = next((label for key, label in WALLETS if key == wallet_type), "Не указано")
    address = wd["address"] or "Не указано"
    amount_type = wd["amount_type"]
    amount = wd["amount"]

    if amount_type == "all":
        amount_str = "Весь баланс"
    else:
        amount_str = f"{amount} {wd['currency'].upper()}"

    last_time_iso = wd["last_time"]
    last_time = datetime.fromisoformat(last_time_iso).strftime("%d.%m.%Y %H:%M:%S") if last_time_iso else "никогда"

    if wd["enabled"]:
        if not last_time_iso:
            next_time = "прямо сейчас"
        else:
            next_time = get_event_next_time(last_time_iso, interval).strftime("%d.%m.%Y %H:%M:%S")
    else:
        next_time = "никогда"

    return (
        f"<b>💸 Авто-вывод</b>\n"
        f"<blockquote>Бот будет автоматически с указанным интервалом выводить средства на аккаунте по указанным реквизитам.</blockquote>\n\n"
        f"<b>💡 Включено:</b> {enabled}\n"
        f"<b>⏰ Интервал:</b> {interval} сек.\n\n"
        f"<b>💳 Способ:</b> {wallet_label}\n"
        f"<b>📬 Реквизиты:</b> {address}\n\n"
        f"<b>💰 Сумма:</b> {amount_str}\n\n"
        f"⏮️ Последний раз: <b>{last_time}</b>\n"
        f"⏭️ Следующий раз: <b>{next_time}</b>"
    )


def withdrawal_kb():
    config = sett.get("config")
    wd = config["funpay"]["auto_withdrawal"]

    enabled = "✅" if wd["enabled"] else "❌"
    amount_type = wd["amount_type"]

    rows = [
        [InlineKeyboardButton(text="💸 Создать вывод", callback_data="confirm_withdrawal")],
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_auto_withdrawal_enabled")],
        [InlineKeyboardButton(text=f"⏰ Интервал: {wd['interval']} сек.", callback_data="enter_withdrawal_interval")],
    ]

    wallet_type = wd["wallet_type"]
    wallet_label = next((label for key, label in WALLETS if key == wallet_type), "Не указано")
    rows.append([InlineKeyboardButton(text=f"💳 Способ: {wallet_label}", callback_data="select_withdrawal_wallet")])

    rows.append([InlineKeyboardButton(text=f"📬 Реквизиты: {wd['address'] or 'Не указано'}", callback_data="enter_withdrawal_address")])

    amount_label = "Весь баланс" if amount_type == "all" else f"{wd['amount']} {wd['currency'].upper()}"
    rows.append([InlineKeyboardButton(text=f"💰 Сумма: {amount_label}", callback_data="switch_withdrawal_amount_type")])

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def withdrawal_wallets_kb():
    config = sett.get("config")
    wallet_type = config["funpay"]["auto_withdrawal"]["wallet_type"]

    rows = []
    for key, label in WALLETS:
        sym = "・" if key == wallet_type else ""
        rows.append([InlineKeyboardButton(
            text=f"{sym} {label} {sym}",
            callback_data=f"sel_withdrawal_wallet:{key}"
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="withdrawal").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def withdrawal_float_text(placeholder):
    return f"<b>💸 Авто-вывод</b>\n\n{placeholder}"
