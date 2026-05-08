import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import get_stats

from .. import callback_datas as calls


def stats_text(to):
    stats = get_stats()

    if to == "day":
        txt = textwrap.dedent(f"""
            <b>📊 Статистика</b>

            <b>⏰ За последние 24 часа:</b>
                            
            ・ ➕ Активных: {stats['day']['active']}
            ・ ➖ Завершённых: {stats['day']['completed']}
            ・ 🔙 Возвратов: {stats['day']['refunded']}
            ・ ♾️ Всего: {stats['day']['orders']}
            
            <b>💸 Заработано:</b> {stats['day']['profit']} руб.
            <b>🔥 Лучший товар:</b> {stats['day']['best']}
            
            <i>Подсчитывается только во время использования бота</i>
        """)
    elif to == "week":
        txt = textwrap.dedent(f"""
            <b>📊 Статистика</b>

            <b>📅 За последние 7 дней:</b>
                          
            ・ ➕ Активных: {stats['week']['active']}
            ・ ➖ Завершённых: {stats['week']['completed']}
            ・ 🔙 Возвратов: {stats['week']['refunded']}
            ・ ♾️ Всего: {stats['week']['orders']}
            
            <b>💸 Заработано:</b> {stats['week']['profit']} руб.
            <b>🔥 Лучший товар:</b> {stats['week']['best']}
            
            <i>Подсчитывается только во время использования бота</i>
        """)
    elif to == "month":
        txt = textwrap.dedent(f"""
            <b>📊 Статистика</b>

            <b>🗓 За последние 30 дней:</b>
                          
            ・ ➕ Активных: {stats['month']['active']}
            ・ ➖ Завершённых: {stats['month']['completed']}
            ・ 🔙 Возвратов: {stats['month']['refunded']}
            ・ ♾️ Всего: {stats['month']['orders']}
            
            <b>💸 Заработано:</b> {stats['month']['profit']} руб.
            <b>🔥 Лучший товар:</b> {stats['month']['best']}
            
            <i>Подсчитывается только во время использования бота</i>
        """)
    elif to == "all":
        txt = textwrap.dedent(f"""
            <b>📊 Статистика</b>

            <b>📈 За всё время:</b>
        
            ・ ➕ Активных: {stats['all']['active']}
            ・ ➖ Завершённых: {stats['all']['completed']}
            ・ 🔙 Возвратов: {stats['all']['refunded']}
            ・ ♾️ Всего: {stats['all']['orders']}
            
            <b>💸 Заработано:</b> {stats['all']['profit']} руб.
            <b>🔥 Лучший товар:</b> {stats['all']['best']}
            
            <i>Подсчитывается только во время использования бота</i>
        """)
        
    return txt


def stats_kb(to):
    sym1 = "・" if to == "day" else ""
    sym2 = "・" if to == "week" else ""
    sym3 = "・" if to == "month" else ""
    sym4 = "・" if to == "all" else ""
    
    rows = [
        [
        InlineKeyboardButton(text=f"{sym1} ⏰ 24 часа {sym1}", callback_data=calls.StatsNavigation(to="day").pack()),
        InlineKeyboardButton(text=f"{sym2} 📅 7 дней {sym2}", callback_data=calls.StatsNavigation(to="week").pack())
        ],
        [
        InlineKeyboardButton(text=f"{sym3} 🗓 30 дней {sym3}", callback_data=calls.StatsNavigation(to="month").pack()),
        InlineKeyboardButton(text=f"{sym4} 📈 Всё время {sym4}", callback_data=calls.StatsNavigation(to="all").pack())
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb