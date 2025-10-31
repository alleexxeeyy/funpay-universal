from aiogram.fsm.state import State, StatesGroup


class SystemStates(StatesGroup):
    waiting_for_password = State()


class ActionsStates(StatesGroup):
    waiting_for_message_text = State()
    waiting_for_review_answer_text = State()


class SettingsStates(StatesGroup):
    waiting_for_golden_key = State()
    waiting_for_user_agent = State()
    waiting_for_proxy = State()

    waiting_for_requests_timeout = State()
    waiting_for_runner_requests_delay = State()

    waiting_for_auto_tickets_orders_per_ticket = State()
    waiting_for_auto_tickets_min_order_age = State()
    waiting_for_auto_tickets_create_interval = State()

    waiting_for_tg_logging_chat_id = State()
    waiting_for_watermark_value = State()


class MessagesStates(StatesGroup):
    waiting_for_page = State()
    waiting_for_message_text = State()


class CustomCommandsStates(StatesGroup):
    waiting_for_page = State()
    waiting_for_new_custom_command = State()
    waiting_for_new_custom_command_answer = State()
    waiting_for_custom_command_answer = State()


class AutoDeliveriesStates(StatesGroup):
    waiting_for_page = State()
    waiting_for_new_auto_delivery_lot_id = State()
    waiting_for_new_auto_delivery_message = State()
    waiting_for_auto_delivery_message = State()