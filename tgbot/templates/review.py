from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import escape_html
from FunPayAPI.types import Review

from .. import callback_datas as calls


def review_text(review: Review):
    stars = "⭐" * (review.stars or 0)
    author = escape_html(review.author or "Аноним")
    text = escape_html(review.text or "") if review.text else "<i>Без текста</i>"

    groups = [
        f"<b>👤 Автор:</b> {author}\n<b>✨ Оценка:</b> {stars}",
        f"<b>🏷️ Текст:</b>\n<blockquote>{text}</blockquote>",
    ]

    if review.reply:
        groups.append(f"<b>↩️ Ваш ответ:</b>\n<blockquote>{escape_html(review.reply)}</blockquote>")

    header = f"<b>🌟 Отзыв по заказу #{review.order_id}</b>" if review.order_id else "<b>🌟 Отзыв</b>"
    return header + "\n\n" + "\n\n".join(groups)


def review_kb(review: Review, last_page=0):
    rows = []

    if not review.reply:
        rows.append([InlineKeyboardButton(
            text="↩️ Ответить",
            callback_data=calls.AnswerReview(id=str(review.order_id)).pack()
        )])
    else:
        rows.append([InlineKeyboardButton(
            text="🗑 Удалить ответ",
            callback_data=calls.DeleteReview(id=str(review.order_id)).pack()
        )])

    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ReviewsPagination(page=last_page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ReviewPage(id=str(review.order_id)).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def review_float_text(placeholder):
    return f"<b>🌟 Отзыв</b>\n\n{placeholder}"
