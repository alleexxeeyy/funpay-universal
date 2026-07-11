import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from __init__ import VERSION

from .. import callback_datas as calls


def plholders_text(to):
    if to == "account":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>

            <b>👤 Аккаунт</b> (<code>account</code>):

            ・ <code>{account.id}</code> — ID аккаунта
            ・ <code>{account.username}</code> — Никнейм аккаунта
            ・ <code>{account.balance}</code> — Баланс аккаунта
            ・ <code>{account.active_sales}</code> — Активные продажи
            ・ <code>{account.active_purchases}</code> — Активные покупки
        """)
    elif to == "user":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>

            <b>👤 Собеседник</b> (<code>user</code>):

            ・ <code>{user.id}</code> — ID пользователя
            ・ <code>{user.username}</code> — Юзернейм пользователя
        """)
    elif to == "order":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>

            <b>📋 Заказ</b> (<code>order</code>):

            ・ <code>{order.id}</code> — ID заказа
            ・ <code>{order.title}</code> — Название товара
            ・ <code>{order.amount}</code> — Количество
            ・ <code>{order.price}</code> — Цена
            ・ <code>{order.buyer}</code> — Покупатель
            ・ <code>{order.status}</code> — Статус заказа
            ・ <code>{order.date}</code> — Дата заказа

            <b>Также доступны:</b>
            ・ <code>{order_id}</code> — ID заказа
            ・ <code>{order_title}</code> — Название товара
            ・ <code>{order_amount}</code> — Количество
            ・ <code>{order_price}</code> — Цена
        """)
    elif to == "review":
        txt = textwrap.dedent("""
            <b>🏷️ Заменители</b>

            <b>🌟 Отзыв</b> (<code>review</code>):

            ・ <code>{review.stars}</code> — Звёзды отзыва
            ・ <code>{review.text}</code> — Текст отзыва
            ・ <code>{review.author}</code> — Автор отзыва
            ・ <code>{review.order_id}</code> — ID заказа

            <b>Также доступны:</b>
            ・ <code>{review_date}</code> — Текущая дата
            ・ <code>{order_title}</code> — Название товара
            ・ <code>{order_amount}</code> — Количество
            ・ <code>{order_price}</code> — Цена
        """)
    else:
        txt = "<b>🏷️ Заменители</b>\n\nНеизвестная категория"
    return txt


def plholders_kb(to, by, last_page=0):
    sym_acc = "・" if to == "account" else ""
    sym_user = "・" if to == "user" else ""
    sym_order = "・" if to == "order" else ""
    sym_review = "・" if to == "review" else ""

    if by == "mess":
        cb = calls.MessagesPagination(page=last_page).pack()
    else:
        cb = calls.CustomCommandsPagination(page=last_page).pack()

    rows = [
        [
            InlineKeyboardButton(text=f"{sym_acc} 👤 Аккаунт {sym_acc}", callback_data=calls.PlaceholdersNavigation(to="account", by=by).pack()),
            InlineKeyboardButton(text=f"{sym_user} 👤 Собеседник {sym_user}", callback_data=calls.PlaceholdersNavigation(to="user", by=by).pack()),
        ],
        [
            InlineKeyboardButton(text=f"{sym_order} 📋 Заказ {sym_order}", callback_data=calls.PlaceholdersNavigation(to="order", by=by).pack()),
            InlineKeyboardButton(text=f"{sym_review} 🌟 Отзыв {sym_review}", callback_data=calls.PlaceholdersNavigation(to="review", by=by).pack()),
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=cb)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
