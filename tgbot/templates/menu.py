import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from __init__ import VERSION

from .. import callback_datas as calls


def menu_text():
    txt = textwrap.dedent(f"""
        <b>🏠 FunPay Universal</b> v{VERSION}
        Ваш бот-помощник для FunPay
    """)
    return txt


def menu_kb():
    rows = [
        [InlineKeyboardButton(text="━━━  НАСТРОЙКИ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text="🔒 Авторизация", callback_data=calls.MenuNavigation(to="auth").pack()),
        InlineKeyboardButton(text="🛜 Соединение", callback_data=calls.MenuNavigation(to="conn").pack()),
        ],
        [
        InlineKeyboardButton(text="💬 Сообщения", callback_data=calls.MessagesPagination(page=0).pack()),
        InlineKeyboardButton(text="❗ Команды", callback_data=calls.CustomCommandsPagination(page=0).pack()),
        ],
        [
        InlineKeyboardButton(text="🚀 Авто-выдача", callback_data=calls.AutoDeliveriesPagination(page=0).pack()),
        InlineKeyboardButton(text="📞 Авто-тикеты", callback_data=calls.MenuNavigation(to="tickets").pack()),
        ],
        [
        InlineKeyboardButton(text="🔔 Уведомления", callback_data=calls.MenuNavigation(to="notifications").pack()),
        InlineKeyboardButton(text="⚡ Быстрые ответы", callback_data=calls.FastRepliesPagination(page=0).pack()),
        ],
        [InlineKeyboardButton(text="🔧 Прочее", callback_data=calls.MenuNavigation(to="other").pack())],
        [InlineKeyboardButton(text="━━━  УПРАВЛЕНИЕ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text="👤 Профиль", callback_data=calls.MenuNavigation(to="profile").pack()),
        InlineKeyboardButton(text="📊 Статистика", callback_data=calls.StatsNavigation(to="day").pack()),
        ],
        [InlineKeyboardButton(text="━━━  СИСТЕМА  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text="🔃 Обновления", callback_data=calls.MenuNavigation(to="updates").pack()),
        InlineKeyboardButton(text="🗒️ Логи", callback_data=calls.MenuNavigation(to="logs").pack()),
        ],
        [
        InlineKeyboardButton(text="🔌 Модули", callback_data=calls.ModulesPagination(page=0).pack()),
        InlineKeyboardButton(text="🔑 Авторизации", callback_data=calls.SignedUsersPagination(page=0).pack())
        ],
        [InlineKeyboardButton(text="━━━  ССЫЛКИ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text="📢 Новости", url="https://t.me/alexeyproduction"), 
        InlineKeyboardButton(text="🧩 Плагины", url="https://t.me/alexey_production_bot"),
        ],
        [
        InlineKeyboardButton(text="👨‍💻 Разработчик", url="https://t.me/alleexxeeyy"), 
        InlineKeyboardButton(text="🐈‍⬛ GitHub", url="https://github.com/alleexxeeyy/funpay-universal"),
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb