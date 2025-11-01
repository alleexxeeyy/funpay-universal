from colorama import Fore
from logging import getLogger

from FunPayAPI.updater.events import EventTypes


logger = getLogger("universal.handlers")

_bot_event_handlers: dict[str, list[callable]] = {
    "ON_MODULE_CONNECTED": [],
    "ON_MODULE_ENABLED": [],
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


def get_bot_event_handlers() -> dict[str, list[callable]]:
    """
    Возвращает хендлеры ивентов бота.

    :return: Словарь с событиями и списками хендлеров.
    :rtype: `dict[str, list[callable]]`
    """
    return _bot_event_handlers


def set_bot_event_handlers(data: dict[str, list[callable]]):
    """
    Устанавливает новые хендлеры ивентов бота.

    :param data: Словарь с названиями событий и списками хендлеров.
    :type data: `dict[str, list[callable]]`
    """
    global _bot_event_handlers
    _bot_event_handlers = data


def add_bot_event_handler(event: str, handler: callable, index: int | None = None):
    """
    Добавляет новый хендлер в ивенты бота.

    :param event: Название события, для которого добавляется хендлер.
    :type event: `str`

    :param handler: Вызываемый метод.
    :type handler: `callable`

    :param index: Индекс в массиве хендлеров, _опционально_.
    :type index: `int` or `None`
    """
    global _bot_event_handlers
    if not index: _bot_event_handlers[event].append(handler)
    else: _bot_event_handlers[event].insert(index, handler)


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


def remove_bot_event_handlers(handlers: dict[str, list[callable]]):
    """
    Удаляет переданные хендлеры бота.

    :param handlers: Словарь с событиями и списками хендлеров бота.
    :type handlers: `dict[str, list[callable]]`
    """
    for event, funcs in handlers.items():
        if event in _bot_event_handlers:
            for func in funcs:
                if func in _bot_event_handlers[event]:
                    _bot_event_handlers[event].remove(func)


def get_funpay_event_handlers() -> dict[EventTypes, list]:
    """
    Возвращает хендлеры ивентов FunPay.

    :return: Словарь с событиями и списками хендлеров.
    :rtype: `dict[FunPayAPI.updater.events.EventTypes, list[callable]]`
    """
    return _funpay_event_handlers


def set_funpay_event_handlers(data: dict[EventTypes, list[callable]]):
    """
    Устанавливает новые хендлеры ивентов FunPay.

    :param data: Словарь с событиями и списками хендлеров.
    :type data: `dict[FunPayAPI.updater.events.EventTypes, list[callable]]`
    """
    global _funpay_event_handlers
    _funpay_event_handlers = data


def add_funpay_event_handler(event: EventTypes, handler: callable, index: int | None = None):
    """
    Добавляет новый хендлер в ивенты FunPay.

    :param event: Событие, для которого добавляется хендлер.
    :type event: `FunPayAPI.updater.events.EventTypes`

    :param handler: Вызываемый метод.
    :type handler: `callable`

    :param index: Индекс в массиве хендлеров, _опционально_.
    :type index: `int` or `None`
    """
    global _funpay_event_handlers
    if not index: _funpay_event_handlers[event].append(handler)
    else: _funpay_event_handlers[event].insert(index, handler)


def register_funpay_event_handlers(handlers: dict[EventTypes, list[callable]]):
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


def remove_funpay_event_handlers(handlers: dict[EventTypes, list[callable]]):
    """
    Удаляет переданные хендлеры FunPay.

    :param handlers: Словарь с событиями и списками хендлеров FunPay.
    :type handlers: `dict[FunPayAPI.updater.events.EventTypes, list[callable]]`
    """
    global _funpay_event_handlers
    for event, funcs in handlers.items():
        if event in _funpay_event_handlers:
            for func in funcs:
                if func in _funpay_event_handlers[event]:
                    _funpay_event_handlers[event].remove(func)


async def call_bot_event(event: str, args: list = [], func = None):
    """
    Вызывает ивент бота.

    :param event: Тип ивента.
    :type event: `str`

    :param args: Аргументы.
    :type args: `list`
    
    :param func: Функция, для которой нужно вызвать ивент (если нужно вызвать только для одной определённой), _опционально_.
    :type func: `callable` or `None`
    """
    if not func: 
        handlers = get_bot_event_handlers().get(event, [])
    else:
        handlers = [func]
    for handler in handlers:
        try:
            await handler(*args)
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера «{handler.__module__}.{handler.__qualname__}» для ивента бота «{event}»: {Fore.WHITE}{e}")


async def call_funpay_event(event: EventTypes, args: list = []):
    """
    Вызывает ивент бота.

    :param event: Тип ивента.
    :type event: `FunPayAPI.common.enums.EventTypes`

    :param args: Аргументы.
    :type args: `list`
    """
    handlers = get_funpay_event_handlers().get(event, [])
    for handler in handlers:
        try:
            await handler(*args)
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера «{handler.__module__}.{handler.__qualname__}» для ивента FunPay «{event.name}»: {Fore.WHITE}{e}")