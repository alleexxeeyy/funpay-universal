import os
import sys
import importlib
import uuid
from uuid import UUID
from colorama import Fore, Style

from core.handlers_manager import remove_handlers, register_bot_event_handlers, register_funpay_event_handlers

class ModuleMeta:
    """
    Класс, содержащий метаданные модуля.

    :param prefix: Префикс модуля.
    :type prefix: str

    :param version: Версия модуля.
    :type version: str

    :param name: Название модуля.
    :type name: str

    :param description: Описание модуля.
    :type description: str

    :param authors: Авторы модуля.
    :type authors: str

    :param links: Ссылки на авторов модуля.
    :type links: str
    """
    def __init__(self, prefix: str, version: str, name: str,
                 description: str, authors: str, links: str):
        self.prefix = prefix
        """ Префикс модуля. """
        self.version = version
        """ Версия модуля. """
        self.name = name
        """ Название модуля. """
        self.description = description
        """ Описание модуля. """
        self.authors = authors
        """ Авторы модуля. """
        self.links = links
        """ Ссылки на авторов модуля. """

class Module:
    """ Класс, содержащий данные модуля """
    def __init__(self, enabled: bool, meta: ModuleMeta, bot_event_handlers: dict, 
                 funpay_event_handlers: dict, telegram_bot_routers: list):
        self.uuid: UUID = uuid.uuid4()
        """ UUID модуля (генерируется при инициализации). """
        self.enabled: bool = enabled
        """ Включен ли модуль. """
        self.meta = meta
        """ Метаданные модуля. """
        self.bot_event_handlers = bot_event_handlers
        """ Хендлеры ивентов бота. """
        self.funpay_event_handlers = funpay_event_handlers
        """ Хендлеры ивентов FunPay. """
        self.telegram_bot_routers = telegram_bot_routers
        """ Роутеры Telegram бота. """


_loaded_modules: list[Module] = []
""" Загруженные модули """

def set_modules(modules: list[Module]):
    """ Устанавливает загруженные модули """
    global _loaded_modules
    _loaded_modules = modules

def get_modules() -> list[Module]:
    """ Получает загруженные модули """
    return _loaded_modules

def get_module_by_uuid(module_uuid: UUID) -> Module:
    """ 
    Получает модуль по названию.
    
    :param module_uuid: UUID модуля.
    :type module_uuid: UUID

    :return: Объект модуля.
    :rtype: Module
    """
    for module in _loaded_modules:
        if module.uuid == module_uuid:
            return module
    return None

def enable_module(module_uuid: UUID) -> bool:
    """
    Включает модуль и добавляет его хендлеры.

    :param module_uuid: UUID модуля.
    :type module_uuid: UUID
    """
    global _loaded_modules
    try:
        module = get_module_by_uuid(module_uuid)
        if not module:
            raise Exception("Модуль не найден в загруженных")
    
        register_bot_event_handlers(module.bot_event_handlers)
        register_funpay_event_handlers(module.funpay_event_handlers)
        i = _loaded_modules.index(module)
        module.enabled = True
        _loaded_modules[i] = module
        print(f"{Fore.WHITE}🔌 Модуль {Fore.LIGHTWHITE_EX}{module.meta.name} {Fore.WHITE}подключен")
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Ошибка при подключении модуля {module_uuid}: {Fore.WHITE}{e}")
        return False

def disable_module(module_uuid: UUID) -> bool:
    """ 
    Полностью выключает модуль и удаляет его хендлеры.
    
    :param module_uuid: UUID модуля.
    :type module_uuid: UUID
    """
    global _loaded_modules
    try:
        module = get_module_by_uuid(module_uuid)
        if not module:
            raise Exception("Модуль не найден в загруженных")
        
        remove_handlers(module.bot_event_handlers, module.funpay_event_handlers)
        i = _loaded_modules.index(module)
        module.enabled = False
        _loaded_modules[i] = module
        print(f"{Fore.LIGHTRED_EX}🚫 Модуль {module.meta.name} отключен")
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Ошибка при отключении модуля {module_uuid}: {Fore.WHITE}{e}")
        return False


def load_modules() -> list[Module]:
    """ Загружает все модули из папки modules. """
    modules = []
    modules_path = "modules"
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)

    for name in os.listdir(modules_path):
        bot_event_handlers = {}
        funpay_event_handlers = {}
        telegram_bot_routers = []
        
        full_path = os.path.join(modules_path, name)
        if os.path.isdir(full_path) and "__init__.py" in os.listdir(full_path):
            try:
                module = importlib.import_module(f"modules.{name}")
                if hasattr(module, "BOT_EVENT_HANDLERS"):
                    for key, funcs in module.BOT_EVENT_HANDLERS.items():
                        bot_event_handlers.setdefault(key, []).extend(funcs)
                if hasattr(module, "FUNPAY_EVENT_HANDLERS"):
                    for key, funcs in module.FUNPAY_EVENT_HANDLERS.items():
                        funpay_event_handlers.setdefault(key, []).extend(funcs)
                if hasattr(module, "TELEGRAM_BOT_ROUTERS"):
                    telegram_bot_routers.extend(module.TELEGRAM_BOT_ROUTERS)
                
                module_data = Module(
                    enabled=False,
                    meta=ModuleMeta(
                        module.PREFIX,
                        module.VERSION,
                        module.NAME,
                        module.DESCRIPTION,
                        module.AUTHORS,
                        module.LINKS
                    ),
                    bot_event_handlers=bot_event_handlers,
                    funpay_event_handlers=funpay_event_handlers,
                    telegram_bot_routers=telegram_bot_routers
                )
                modules.append(module_data)
            except Exception as e:
                print(f"{Fore.LIGHTRED_EX}Ошибка при загрузке модуля {name}: {Fore.WHITE}{e}")
    return modules

def connect_modules(modules: list[Module]):
    """ Подключает (включает) переданные в массиве модули. """
    names = []
    for module in modules:
        try:
            register_bot_event_handlers(module.bot_event_handlers)
            register_funpay_event_handlers(module.funpay_event_handlers)
            i = _loaded_modules.index(module)
            module.enabled = True
            _loaded_modules[i] = module
            names.append(f"{Fore.LIGHTYELLOW_EX}{module.meta.name} {Fore.LIGHTWHITE_EX}{module.meta.version}")
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Ошибка при подключении модуля {module.meta.name}: {Fore.WHITE}{e}")
            continue
    print(f'{Fore.WHITE}🔌 Подключено {Fore.LIGHTWHITE_EX}{len(modules)} модуля(-ей): {f"{Fore.WHITE}, ".join(names)}')