import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_tickets_text():
    config = sett.get("config")
    auto_tickets_enabled = "🟢 Включено" if config["funpay"]["auto_tickets"]["enabled"] else "🔴 Выключено"
    auto_tickets_orders_per_ticket = config["funpay"]["auto_tickets"]["orders_per_ticket"] or "❌ Не задано"
    auto_tickets_create_interval = config["funpay"]["auto_tickets"]["interval"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 📞 Тикеты</b>

        📧 <b>Авто-создание тикетов на закрытие:</b> {auto_tickets_enabled}
        📋 <b>Кол-во заказов в одном тикете:</b> {auto_tickets_orders_per_ticket}
        ⏱️ <b>Интервал создания тикетов:</b> {auto_tickets_create_interval}

        <b>Что такое авто-создание тикетов на закрытие?</b>
        Бот будет автоматически создавать тикеты в тех. поддержку на закрытие неподтверждённых заказов каждые N секунд. Чем больше заказов в одном тикете - тем дольше его будут проверять, 25 заказов - оптимальное значение. 24 часа - самый идеальный интервал создания тикетов, ведь на FunPay стоит ограничение в виде 1 тикета на закрытие в день, ставить меньше нет смысла

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_tickets_kb():
    config = sett.get("config")
    auto_tickets_enabled = "🟢 Включено" if config["funpay"]["auto_tickets"]["enabled"] else "🔴 Выключено"
    auto_tickets_orders_per_ticket = config["funpay"]["auto_tickets"]["orders_per_ticket"] or "❌ Не задано"
    auto_tickets_create_interval = config["funpay"]["auto_tickets"]["interval"] or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"📧 Авто-создание тикетов на закрытие: {auto_tickets_enabled}", callback_data="switch_tickets|auto_tickets|enabled")],
        [InlineKeyboardButton(text=f"📋 Кол-во заказов в одном тикете: {auto_tickets_orders_per_ticket}", callback_data="enter_auto_tickets_orders_per_ticket")],
        [InlineKeyboardButton(text=f"⏱️ Интервал создания тикетов: {auto_tickets_create_interval}", callback_data="enter_auto_tickets_create_interval")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="tickets").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_tickets_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 📞 Тикеты</b>
        \n{placeholder}
    """)
    return txt