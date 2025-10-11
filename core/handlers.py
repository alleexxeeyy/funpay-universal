from FunPayAPI.updater.events import EventTypes


_bot_event_handlers: dict[str, list[callable]] = {
    "ON_MODULE_CONNECTED": [],
    "ON_MODULE_ENABLED": [],
    "ON_MODULE_DISABLED": [],
    "ON_MODULE_RELOADED": [],
    "ON_INIT": [],
    "ON_FUNPAY_BOT_INIT": [],
    "ON_TELEGRAM_BOT_INIT": []
}
_funpay_event_handlers: dict[EventTypes, list[callable]] = {
    EventTypes.CHATS_LIST_CHANGED: [],
    EventTypes.INITIAL_CHAT: [],
    EventTypes.INITIAL_ORDER: [],
    EventTypes.LAST_CHAT_MESSAGE_CHANGED: [],
    EventTypes.NEW_MESSAGE: [],
    EventTypes.NEW_ORDER: [],
    EventTypes.ORDER_STATUS_CHANGED: [],
    EventTypes.ORDERS_LIST_CHANGED: []
}


def set_bot_event_handlers(data: dict[str, list[callable]]):
    """
    Устанавливает новые хендлеры ивентов бота.

    :param data: Словарь с названиями событий и списками хендлеров.
    :type data: `dict[str, list[callable]]`
    """
    global _bot_event_handlers
    _bot_event_handlers = data


def add_bot_event_handler(event: str, handler: callable):
    """
    Добавляет новый хендлер в ивенты бота.

    :param event: Название события, для которого добавляется хендлер.
    :type event: `str`

    :param handler: Вызываемый метод.
    :type handler: `callable`
    """
    global _bot_event_handlers
    _bot_event_handlers[event].append(handler)


def register_bot_event_handlers(handlers: dict[str, list[callable]]):
    """
    Регистрирует хендлеры ивентов бота (добавляет переданные хендлеры, если их нету). 

    :param data: Словарь с названиями событий и списками хендлеров.
    :type data: `dict[str, list[callable]]`
    """
    global _bot_event_handlers
    for event_type, funcs in handlers.items():
        if event_type not in _bot_event_handlers:
            _bot_event_handlers[event_type] = []
        _bot_event_handlers[event_type].extend(funcs)


def get_bot_event_handlers() -> dict[str, list[callable]]:
    """
    Возвращает хендлеры ивентов бота.

    :return: Словарь с событиями и списками хендлеров.
    :rtype: `dict[str, list[callable]]`
    """
    return _bot_event_handlers


def set_funpay_event_handlers(data: dict[EventTypes, list[callable]]):
    """
    Устанавливает новые хендлеры ивентов FunPay.

    :param data: Словарь с событиями и списками хендлеров.
    :type data: `dict[FunPayAPI.updater.events.EventTypes, list[callable]]`
    """
    global _funpay_event_handlers
    _funpay_event_handlers = data


def add_funpay_event_handler(event: EventTypes, handler: callable):
    """
    Добавляет новый хендлер в ивенты FunPay.

    :param event: Событие, для которого добавляется хендлер.
    :type event: `FunPayAPI.updater.events.EventTypes`

    :param handler: Вызываемый метод.
    :type handler: `callable`
    """
    global _funpay_event_handlers
    _funpay_event_handlers[event].append(handler)


def register_funpay_event_handlers(handlers):
    """
    Регистрирует хендлеры ивентов FunPay (добавляет переданные хендлеры, если их нету). 

    :param data: Словарь с событиями и списками хендлеров.
    :type data: `dict[FunPayAPI.updater.events.EventTypes, list[callable]]`
    """
    global _funpay_event_handlers
    for event_type, funcs in handlers.items():
        if event_type not in _funpay_event_handlers:
            _funpay_event_handlers[event_type] = []
        _funpay_event_handlers[event_type].extend(funcs)


def get_funpay_event_handlers() -> dict[EventTypes, list]:
    """
    Возвращает хендлеры ивентов FunPay.

    :return: Словарь с событиями и списками хендлеров.
    :rtype: `dict[FunPayAPI.updater.events.EventTypes, list[callable]]`
    """
    return _funpay_event_handlers


def remove_handlers(bot_event_handlers: dict[str, list[callable]], funpay_event_handlers: dict[EventTypes, list[callable]]):
    """
    Удаляет переданные хендлеры бота и FunPay.

    :param bot_event_handlers: Словарь с событиями и списками хендлеров бота.
    :type bot_event_handlers: `dict[str, list[callable]]`

    :param funpay_event_handlers: Словарь с событиями и списками хендлеров FunPay.
    :type funpay_event_handlers: `dict[FunPayAPI.updater.events.EventTypes, list[callable]]`
    """ # ДОДЕЛАТЬ
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