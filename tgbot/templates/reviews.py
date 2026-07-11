import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import escape_html
from FunPayAPI.types import Review

from .. import callback_datas as calls


def _get_review_info(review: Review):
    stars = "⭐" * (review.stars or 0)
    author = escape_html(review.author or "Аноним")
    text = escape_html(review.text or "") if review.text else ""
    text = text[:60] + ("..." if len(text) > 60 else "")
    return stars, author, text


def reviews_text(reviews: list, page=0):
    items_per_page = 12

    total_pages = math.ceil(len(reviews) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    reviews_frmtd = ""
    for review in list(reviews)[start_offset:end_offset]:
        stars, author, text = _get_review_info(review)
        line = f"<b>{stars} {author}</b>"
        if review.order_id:
            line += f" · #{review.order_id}"
        if text:
            line += f"\n      ┗ {text}"
        reviews_frmtd += line + "\n\n"

    reviews_frmtd = reviews_frmtd.strip()
    if not reviews_frmtd:
        reviews_frmtd = "Отзывов не найдено. Попробуйте обновить страницу"

    return f"<b>🌟 Отзывы</b>\n\n{reviews_frmtd}"


def reviews_kb(reviews: list, page=0):
    rows = []
    items_per_page = 12
    items_per_row = 1

    total_pages = math.ceil(len(reviews) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for review in list(reviews)[start_offset:end_offset]:
        stars, author, text = _get_review_info(review)
        btn_text = f"{stars} {author}"
        if review.order_id:
            btn_text += f" · #{review.order_id}"
        dynamic_btns.append(InlineKeyboardButton(
            text=btn_text,
            callback_data=calls.ReviewPage(id=str(review.order_id)).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.ReviewsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)
        buttons_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer"))
        btn_next = InlineKeyboardButton(text="→", callback_data=calls.ReviewsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ReviewsPagination(page=page, upd=True).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def reviews_float_text(placeholder):
    return f"<b>🌟 Отзывы</b>\n\n{placeholder}"
