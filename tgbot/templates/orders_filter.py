from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import callback_datas as calls


def orders_filter_kb(filter, last_page=0):
    statuses = filter.get("statuses", [])

    st1 = "・" if "paid" in statuses else ""
    st2 = "・" if "closed" in statuses else ""
    st3 = "・" if "refunded" in statuses else ""
    st4 = "・" if statuses == [] else ""

    rows = [
        [InlineKeyboardButton(text="━━━  СТАТУС  ━━━", callback_data="null_answer")],
        [
            InlineKeyboardButton(text=f"{st1} Оплачены {st1}", callback_data=calls.ChangeOrdersFilter(st=1).pack()),
            InlineKeyboardButton(text=f"{st2} Закрытые {st2}", callback_data=calls.ChangeOrdersFilter(st=2).pack()),
        ],
        [
            InlineKeyboardButton(text=f"{st3} Возвраты {st3}", callback_data=calls.ChangeOrdersFilter(st=3).pack()),
        ],
        [InlineKeyboardButton(text=f"{st4} Все {st4}", callback_data=calls.ChangeOrdersFilter(st=4).pack())],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.OrdersPagination(page=last_page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb
