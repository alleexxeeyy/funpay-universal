import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from fpbot.stats import get_stats

from .. import callback_datas as calls


def stats_text():
    from fpbot.funpaybot import get_funpay_bot
    stats = get_stats()
    txt = textwrap.dedent(f"""
        📊 <b>Статистика FunPay бота</b>

        Дата запуска бота: <b>{stats.bot_launch_time.strftime("%d.%m.%Y %H:%M:%S") or 'Не запущен'}</b>

        <b>Статистика с момента запуска:</b>
        ┣ Выполнено: <b>{stats.orders_completed}</b>
        ┣ Возвратов: <b>{stats.orders_refunded}</b>
        ┗ Заработано: <b>{stats.earned_money} {get_funpay_bot().funpay_account.currency.name}</b>

        Выберите действие ↓
    """)
    return txt


def stats_kb():
    rows = [
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MenuNavigation(to="stats").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb