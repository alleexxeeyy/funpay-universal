from aiogram.fsm.state import State, StatesGroup


class FunPayStates(StatesGroup):
    waiting_for_chat_message = State()

    waiting_for_order_review_answer = State()
    waiting_for_order_review_rating = State()

    waiting_for_lot_price = State()
    waiting_for_lot_description = State()
    waiting_for_lot_title = State()

    waiting_for_withdrawal_interval = State()
    waiting_for_withdrawal_address = State()
    waiting_for_withdrawal_amount = State()
    waiting_for_withdrawal_amount_value = State()


class OrderReviewStates(StatesGroup):
    waiting_for_review_text = State()
