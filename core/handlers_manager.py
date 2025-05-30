from FunPayAPI.updater.events import EventTypes

_bot_event_handlers = {
    "ON_MODULE_CONNECTED": [],
    "ON_INIT": [],
    "ON_FUNPAY_BOT_INIT": [],
    "ON_TELEGRAM_BOT_INIT": []
}
""" Хендлеры ивентов бота. """
_funpay_event_handlers = {
    EventTypes.CHATS_LIST_CHANGED: [],
    EventTypes.INITIAL_CHAT: [],
    EventTypes.INITIAL_ORDER: [],
    EventTypes.LAST_CHAT_MESSAGE_CHANGED: [],
    EventTypes.NEW_MESSAGE: [],
    EventTypes.NEW_ORDER: [],
    EventTypes.ORDER_STATUS_CHANGED: [],
    EventTypes.ORDERS_LIST_CHANGED: []
}
""" Хендлеры ивентов FunPay Runner`а. """

class HandlersManager:
    """
    Класс, описывающий взаимодействие с хендлерами бота.
    """

    @staticmethod
    def set_bot_event_handlers(data: dict[str, list]):
        global _bot_event_handlers
        _bot_event_handlers = data

    @staticmethod
    def get_bot_event_handlers() -> dict[str, list]:
        global _bot_event_handlers
        return _bot_event_handlers

    @staticmethod
    def add_bot_event_handler(event: str, handler):
        global _bot_event_handlers
        _bot_event_handlers[event].append(handler)

    @staticmethod
    def set_funpay_event_handlers(data: dict[EventTypes, list]):
        global _funpay_event_handlers
        _funpay_event_handlers = data

    @staticmethod
    def get_funpay_event_handlers() -> dict[EventTypes, list]:
        global _funpay_event_handlers
        return _funpay_event_handlers
    
    @staticmethod
    def add_funpay_event_handler(event: EventTypes, handler):
        global _funpay_event_handlers
        _funpay_event_handlers[event].append(handler)

    @staticmethod
    def register_bot_event_handlers(handlers):
        """ Устанавливает ивент хендлеры бота. """
        global _bot_event_handlers
        for event_type, funcs in handlers.items():
            if event_type not in _bot_event_handlers:
                _bot_event_handlers[event_type] = []
            _bot_event_handlers[event_type].extend(funcs)

    @staticmethod
    def register_funpay_event_handlers(handlers):
        """ Устанавливает хендлеры фанпей ивентов. """
        global _funpay_event_handlers
        for event_type, funcs in handlers.items():
            if event_type not in _funpay_event_handlers:
                _funpay_event_handlers[event_type] = []
            _funpay_event_handlers[event_type].extend(funcs)

    @staticmethod
    def remove_handlers(bot_event_handlers, funpay_event_handlers):
        """ Удаляет все хендлеры модуля из глобальных списков. """
        global _bot_event_handlers, _funpay_event_handlers
        for event, funcs in bot_event_handlers.items():
            if event in _bot_event_handlers:
                for func in funcs:
                    if func in _bot_event_handlers[event]:
                        _bot_event_handlers[event].remove(func)
        for event, funcs in funpay_event_handlers.items():
            if event in _funpay_event_handlers:
                for func in funcs:
                    if func in _funpay_event_handlers[event]:
                        _funpay_event_handlers[event].remove(func)
        