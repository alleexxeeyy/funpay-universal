from aiogram.fsm.state import State, StatesGroup



class StatsNavigationStates(StatesGroup):
    """ Состояния навигации по инструкции """
    entering_active_smm_lots_page = State()

class LotsSettingsNavigationStates(StatesGroup):
    """ Состояния навигации по настройкам лотов """
    confirming_activating_lots = State()
    confirming_deactivating_lots = State()

class BotSettingsNavigationStates(StatesGroup):
    """ Состояния навигации по настройкам бота """
    entering_golden_key = State()
    entering_user_agent = State()
    entering_funpayapi_requests_timeout = State()
    entering_funpayapi_runner_requests_delay = State()
    entering_messages_watermark = State()

class MessagesNavigationStates(StatesGroup):
    """ Состояния навигации по сообщениям """
    entering_messages_page = State()

class MessagePageNavigationStates(StatesGroup):
    """ Состояния навигации по странице сообщения """
    entering_message_text = State()

class CustomCommandsNavigationStates(StatesGroup):
    """ Состояния навигации по сообщениям """
    entering_custom_commands_page = State()

class CustomCommandPageNavigationStates(StatesGroup):
    """ Состояния навигации по странице сообщения """
    entering_custom_command = State()
    entering_custom_command_answer = State()
    entering_new_custom_command_answer = State()

class AutoDeliveriesNavigationStates(StatesGroup):
    """ Состояния навигации по авто-выдаче """
    entering_custom_commands_page = State()

class AutoDeliveryPageNavigationStates(StatesGroup):
    """ Состояния навигации по странице сообщения """
    entering_auto_delivery_lot_id = State()
    entering_auto_delivery_message = State()
    entering_new_auto_delivery_message = State()

class ActiveOrdersNavigationStates(StatesGroup):
    """ Состояния навигации по активным заказам """
    entering_active_orders_page = State()
    confirming_creating_tickets_to_orders = State()

class ActiveOrderPageNavigationStates(StatesGroup):
    """ Состояния навигации по странице активного заказа """
    confirming_creating_ticket_to_order = State()