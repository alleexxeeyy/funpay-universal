# FunPay Universal
Современный бот-помощник для FunPay 🤖🟦

## 🧭 Навигация:
- [Функционал бота](#-функционал)
- [Установка бота](#%EF%B8%8F-установка)
- [Полезные ссылки](#-полезные-ссылки)
- [Для разработчиков](#-для-разработчиков)

## ⚡ Функционал
- Удобный Telegram бот для настройки бота 🗨️
- Система модулей🔌
- Базовый функционал:
  - Вечный онлайн на сайте
  - Приветственное сообщение
  - Автоматическое сообщение после покупки товара
  - Возможность добавления пользовательских команд
  - Автоматические ответы на отзывы
  - Команда `!продавец` для вызова продавца (уведомляет вас в Telegram боте, что покупателю требуется ваша помощь

## ⬇️ Установка
1. Скачайте последнюю Release версию и распакуйте в любое удобное для вас место
2. Убедитесь, что у вас установлен **Python версии 3.x.x - 3.12**. Если не установлен, сделайте это, перейдя по ссылке https://www.python.org/downloads (при установке нажмите на пункт `Add to PATH`)
3. Откройте `install_requirements.bat` и дождитесь установки всех необходимых для работы библиотек, а после закройте окно
4. Чтобы запустить бота, откройте запускатор `start.bat`
5. После первого запуска вас попрсят настроить бота для работы

## 📚 Для разработчиков

Модульная система помогает внедрять в бота дополнительный функционал, сделанный энтузиастами. По сути, это же, что и плагины, но в более удобном формате.

<details>
  <summary><strong>📌 Основные ивенты</strong></summary>

  ### Ивенты бота (BOT_EVENT_HANDLERS)

  Ивенты, которые выполняются при определённом действии бота.

  | Ивент | Когда вызывается | Передающиеся аргументы |
  |-------|------------------|------------------------|
  | `ON_MODULE_CONNECTED` | При подключении модуля | `Module` |
  | `ON_INIT` | При инициализации бота | `-` |
  | `ON_FUNPAY_BOT_INIT` | При инициализации (запуске) FunPay бота | `FunPayBot` |
  | `ON_TELEGRAM_BOT_INIT` | При инициализации (запуске) Telegram бота | `TelegramBot` |

  ### Ивенты FunPay (FUNPAY_EVENT_HANDLERS)

  Ивенты, которые выполняются при получении ивента в раннере FunPay бота.

  | Ивент | Когда вызывается | Передающиеся аргументы |
  |-------|------------------|------------------------|
  | `EventTypes.CHATS_LIST_CHANGED` | Список чатов и/или последнее сообщение одного/нескольких чатов изменилось | `FunPayBot`, `ChatsListChangedEvent` |
  | `EventTypes.INITIAL_CHAT` | Обнаружен чат (при первом запросе Runner'а) | `FunPayBot`, `InitialChatEvent` |
  | `EventTypes.INITIAL_ORDER` | Обнаружен заказ (при первом запросе Runner'а) | `FunPayBot`, `InitialOrderEvent` |
  | `EventTypes.LAST_CHAT_MESSAGE_CHANGED` | В чате изменилось последнее сообщение. | `FunPayBot`, `LastChatMessageChangedEvent` |
  | `EventTypes.NEW_MESSAGE` | Обнаружено новое сообщение в истории чата | `FunPayBot`, `NewMessageEvent` |
  | `EventTypes.NEW_ORDER` | Обнаружен новый заказ | `FunPayBot`, `NewOrderEvent` |
  | `EventTypes.ORDER_STATUS_CHANGED` | Статус заказа изменился | `FunPayBot`, `OrderStatusChangedEvent` |
  | `EventTypes.ORDERS_LIST_CHANGED` | Список заказов и/или статус одного/нескольких заказов изменился | `FunPayBot`, `OrdersListChangedEvent` |

</details>

<details>
  <summary><strong>📁 Строение модуля</strong></summary>  
  <br/>Модуль - это папка, внутри которой находятся важные компоненты. Вы можете изучить строение модуля, опираясь на [шаблонный модуль](templates/test_module), но стоит понимать, что это лишь пример, сделанный нами.
  
  Строение модуля может быть абсолютно любым на ваше усмотрение, но всё же в каждом модуля должен быть обязательный файл инициализации **`__init__.py`**, в котором задаются все основные параметры для корректной
  работы модуля.

  Обязательные константы хендлеров:
  | Константа | Тип | Описание |
  |-----------|-----|----------|
  | `BOT_EVENT_HANDLERS` | `dict[str, list[Any]]` | В этом словаре задаются хендлеры ивентов бота |
  | `FUNPAY_EVENT_HANDLERS` | `dict[EventTypes, list[Any]` | В этом словаре задаются хендлеры ивентов FunPay |
  | `TELEGRAM_BOT_ROUTERS` | list[Router] | В этом массиве задаются роутеры модульного Telegram бота  |

  Обязательные константы метаданных:
  | Константа | Тип | Описание |
  |-----------|-----|----------|
  | `PREFIX` | `str` | Префикс |
  | `VERSION` | `str` | Версия |
  | `NAME` | `str` | Название |
  | `DESCRIPTION` | `str` | Описание |
  | `AUTHORS` | `str` | Авторы |
  | `LINKS` | `str` | Ссылки на авторов |

  #### 🔧 Пример содержимого:
  Обратите внимание, что метаданные были вынесены в отдельный файл `meta.py`, но импортируются в `__init__.py`.  
  Это сделано для избежания конфликтов импорта в дальнейшей части кода модуля.

  `meta.py`:
  ```python
  from colorama import Fore, Style

  PREFIX = f"{Fore.LIGHTCYAN_EX}[test module]{Fore.WHITE}"
  VERSION = "0.1"
  NAME = "test_module"
  DESCRIPTION = "Тестовый модуль. /test_module в Telegram боте для управления"
  AUTHORS = "@alleexxeeyy"
  LINKS = "https://t.me/alleexxeeyy, https://t.me/alexeyproduction"
  ```

  `__init__.py`:
  ```python
  from .fpbot.funpaybot_handlers import FunPayBotHandlers
  from .tgbot.telegrambot_handlers import TelegramBotHandlers
  from .tgbot import router
  from .meta import *
  from FunPayAPI.updater.events import EventTypes
  from core.modules_manager import disable_module, Module
  
  _module: Module = None
  def get_module(module: Module):
      global _module
      _module = module
  
  def handler_on_init():
      try:
          # ...
          print(f"{PREFIX} Модуль инициализирован")
      except:
          disable_module(_module.uuid)
  
  BOT_EVENT_HANDLERS = {
      "ON_MODULE_CONNECTED": [handle_on_module_connected],
      "ON_INIT": [handler_on_init],
      "ON_FUNPAY_BOT_INIT": [FunPayBotHandlers.handler_on_funpay_bot_init],
      "ON_TELEGRAM_BOT_INIT": [TelegramBotHandlers.handler_on_telegram_bot_init]
  }
  FUNPAY_EVENT_HANDLERS = {
      EventTypes.NEW_MESSAGE: [FunPayBotHandlers.handler_new_message],
      EventTypes.NEW_ORDER: [FunPayBotHandlers.handler_new_order]
  }
  TELEGRAM_BOT_ROUTERS = [router]
  ```

  Шаблонный модуль можно найти [здесь](templates/...)

</details>


## 🔗 Полезные ссылки
- Разработчик: https://github.com/alleexxeeyy (в профиле есть актуальные ссылки на все контакты для связи)
- Telegram канал: https://t.me/alexeyproduction
- Telegram бот для покупки официальных модулей: https://t.me/alexey_production_bot
