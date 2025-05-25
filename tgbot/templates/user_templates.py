from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math
from datetime import datetime

import tgbot.callback_datas.user_callback_datas as CallbackDatas

from fpbot.funpaybot import FunPayBot
from fpbot.data import Data

from settings import Config, Messages, CustomCommands, AutoDeliveries

from bot_settings.app import CURRENT_VERSION
from fpbot.utils.stats import get_stats

from core.modules_manager import Module, get_modules, get_module_by_uuid
from uuid import UUID

funpaybot = FunPayBot()
        
class System:
    """ Шаблоны системных сообщений """
    class Error:
        def text(error_text) -> str:
            msg = f"❌ Произошла ошибка: <b>{error_text}</b>"
            return msg

class Navigation:
    """ Шаблоны навигации по боту """

    class MenuNavigation:
        class Default:
            class Error:
                def text() -> str:
                    msg = f"🏠 <b>Главное меню</b>" \
                        f"\n" \
                        f"\n<b>FunPay UNIVERSAL</b> v{CURRENT_VERSION} " \
                        f"\nБот-помощник для FunPay" \
                        f"\n" \
                        f"\n→ Состояние FunPay бота: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n<b>Ссылки:</b>" \
                        f"\n→ <b>@alleexxeeyy</b> — главный и единственный разработчик" \
                        f"\n→ <b>@alexeyproduction</b> — канал, где публикуются новости" \
                        f"\n→ <b>@alexey_production_bot</b> — бот для покупки официальных модулей" \
                        f"\n" \
                        f"\nПеремещайтесь по разделам ниже ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"🏠 <b>Главное меню</b>" \
                        f"\n" \
                        f"\n<b>FunPay UNIVERSAL</b> v{CURRENT_VERSION} " \
                        f"\nБот-помощник для FunPay" \
                        f"\n" \
                        f"\n→ Состояние FunPay бота: <i>загрузка</i>" \
                        f"\n" \
                        f"\n<b>Ссылки:</b>" \
                        f"\n→ <b>@alleexxeeyy</b> — главный и единственный разработчик" \
                        f"\n→ <b>@alexeyproduction</b> — канал, где публикуются новости" \
                        f"\n→ <b>@alexey_production_bot</b> — бот для покупки официальных модулей" \
                        f"\n" \
                        f"\nПеремещайтесь по разделам ниже ↓"
                    return msg

            class Default:
                def text(bots_manager) -> str:
                    started = "🟢 Запущен" if bots_manager.fpbot else "🔴 Остановлен"
                    msg = f"🏠 <b>Главное меню</b>" \
                        f"\n" \
                        f"\n<b>FunPay UNIVERSAL</b> v{CURRENT_VERSION} " \
                        f"\nБот-помощник для FunPay" \
                        f"\n" \
                        f"\n→ Состояние FunPay бота: <code>{started}</code>" \
                        f"\n" \
                        f"\n<b>Ссылки:</b>" \
                        f"\n→ <b>@alleexxeeyy</b> — главный и единственный разработчик" \
                        f"\n→ <b>@alexeyproduction</b> — канал, где публикуются новости" \
                        f"\n→ <b>@alexey_production_bot</b> — бот для покупки официальных модулей" \
                        f"\n" \
                        f"\nПеремещайтесь по разделам ниже ↓"
                    return msg
                    
                def kb(bots_manager) -> InlineKeyboardMarkup:
                    rows = []

                    if bots_manager.fpbot is not None:
                        btn_stop = InlineKeyboardButton(
                            text="🔴 Остановить FunPay бота",
                            callback_data="stop_funpay_bot"
                        )
                        rows.append([btn_stop])
                    else:
                        btn_start = InlineKeyboardButton(
                            text="🟢 Запустить FunPay бота",
                            callback_data="start_funpay_bot"
                        )
                        rows.append([btn_start])
                    btn1 = InlineKeyboardButton(
                        text="⚙️ Настройки",
                        callback_data=CallbackDatas.SettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    btn2 = InlineKeyboardButton(
                        text="📊 Статистика",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="stats"
                        ).pack()
                    )
                    btn3 = InlineKeyboardButton(
                        text="🔌 Модули",
                        callback_data=CallbackDatas.ModulesPagination(
                            page=0
                        ).pack()
                    )
                    rows.append([btn1, btn2, btn3])
                    btn3 = InlineKeyboardButton(
                        text="📖 Инструкция",
                        callback_data=CallbackDatas.InstructionNavigation(
                            to="default"
                        ).pack()
                    )
                    rows.append([btn3])
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows.append([btn_refresh])

                    btn4 = InlineKeyboardButton(
                        text="👨‍💻 Разработчик",
                        url="https://t.me/alleexxeeyy",
                    )
                    btn5 = InlineKeyboardButton(
                        text="📢 Наш канал",
                        url="https://t.me/alexeyproduction",
                    )
                    btn6 = InlineKeyboardButton(
                        text="🤖 Наш бот",
                        url="https://t.me/alexey_production_bot",
                    )
                    rows.append([btn4, btn5, btn6])

                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
            
            class FunpayBotStarting:
                def text() -> str:
                    msg = "🕓 Запускаем FunPay бота, ожидайте..."
                    return msg
            
            class FunpayBotStarted:
                def text() -> str:
                    msg = "✅ <b>FunPay бот</b> был успешно запущен"
                    return msg
            
            class FunpayBotStopping:
                def text() -> str:
                    msg = "🕓 Останавливаем FunPay бота, ожидайте..."
                    return msg
            
            class FunpayBotStopped:
                def text() -> str:
                    msg = "✅ <b>FunPay бот</b> был успешно остановлен"
                    return msg
                
        class Stats:
            class Error:
                def text() -> str:
                    msg = "📊 <b>Статистика FunPay бота</b>" \
                        f"\n" \
                        f"\n→ Дата запуска: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Продаж: <i>не удалось загрузить</i>" \
                        f"\n→ Активных: <i>не удалось загрузить</i>" \
                        f"\n→ Возвратов: <i>не удалось загрузить</i>" \
                        f"\n→ Заработано: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = "📊 <b>Статистика FunPay бота</b>" \
                        f"\n" \
                        f"\n→ Дата запуска: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Продаж: <i>загрузка</i>" \
                        f"\n→ Активных: <i>загрузка</i>" \
                        f"\n→ Возвратов: <i>загрузка</i>" \
                        f"\n→ Заработано: <i>загрузка</i>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg
                
            class Default:
                def text() -> str:
                    stats = get_stats()
                    msg = "📊 <b>Статистика FunPay бота</b>" \
                        f"\n" \
                        f"\n→ Дата запуска: <code>{stats['bot_launch_time'].strftime("%d.%m.%Y %H:%M:%S")}</code>" \
                        f"\n" \
                        f"\n→ Продаж: <code>{stats['orders_completed']}</code>" \
                        f"\n→ Активных: <code>{stats['active_orders']}</code>" \
                        f"\n→ Возвратов: <code>{stats['orders_refunded']}</code>" \
                        f"\n→ Заработано: <code>{stats['earned_money']}</code> р." \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg
                    
                def kb() -> InlineKeyboardMarkup:
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="stats"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
        class Modules:
            class Pagination:
                def text() -> str:
                    modules = get_modules()
                    msg = f"🔌 <b>Модули</b>" \
                            f"\nВсего <b>{len(modules)}</b> загруженных модулей" \
                            f"\n\nПеремещайтесь по разделам ниже. Нажмите на название модуля, чтобы перейти в его управление ↓"
                    return msg
                
                def kb(page: int = 0) -> InlineKeyboardMarkup:
                    modules = get_modules()

                    rows = []
                    items_per_page = 7
                    total_pages = math.ceil(len(modules)/items_per_page)
                    total_pages = total_pages if total_pages > 0 else 1

                    if page < 0:
                        page = 0
                    elif page >= total_pages:
                        page = total_pages-1

                    start_offset = page * items_per_page
                    end_offset = start_offset + items_per_page

                    for module in list(modules)[start_offset:end_offset]:
                        btn = InlineKeyboardButton(
                            text=module.meta.name,
                            callback_data=CallbackDatas.ModulePage(
                                uuid=module.uuid
                            ).pack()
                        )
                        rows.append([btn])
                        
                    buttons_row = []
                    if page > 0:
                        btn_back = InlineKeyboardButton(
                            text="←",
                            callback_data=CallbackDatas.ModulesPagination(
                                page=page-1
                            ).pack()
                        )
                    else:
                        btn_back = InlineKeyboardButton(
                            text="🛑",
                            callback_data="123"
                        )
                    buttons_row.append(btn_back)
                        
                    btn_pages = InlineKeyboardButton(
                        text=f"{page+1}/{total_pages}",
                        callback_data="enter_modules_page"
                    )
                    buttons_row.append(btn_pages)
                    
                    if end_offset < total_pages:
                        btn_next = InlineKeyboardButton(
                            text="→",
                            callback_data=CallbackDatas.ModulesPagination(
                                page=page+1
                            ).pack()
                        )
                    else:
                        btn_next = InlineKeyboardButton(
                            text="🛑",
                            callback_data="123"
                        )
                    buttons_row.append(btn_next)
                    rows.append(buttons_row)

                    btn2 = InlineKeyboardButton(
                        text="🚪 Выход",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows.append([btn2])
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class Page:
                class Error:
                    def text() -> str:
                        msg = f"🔧 <b>Управление модулем</b>" \
                            f"\n" \
                            f"\n→ Состояние: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\n→ UUID: <i>не удалось загрузить</i>" \
                            f"\n→ Название: <i>не удалось загрузить</i>" \
                            f"\n→ Версия: <i>не удалось загрузить</i>" \
                            f"\n→ Описание: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\n→ Авторы: <i>не удалось загрузить</i>" \
                            f"\n→ Ссылки: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\nВыберите действие для управвления ↓"
                        return msg

                class Loading:
                    def text() -> str:
                        msg = f"🔧 <b>Управлением модулем</b>" \
                            f"\n" \
                            f"\n→ Состояние: <i>загрузка</i>" \
                            f"\n" \
                            f"\n→ UUID: <i>загрузка</i>" \
                            f"\n→ Название: <i>загрузка</i>" \
                            f"\n→ Версия: <i>загрузка</i>" \
                            f"\n→ Описание: <i>загрузка</i>" \
                            f"\n" \
                            f"\n→ Авторы: <i>загрузка</i>" \
                            f"\n→ Ссылки: <i>загрузка</i>" \
                            f"\n" \
                            f"\nВыберите действие для управвления ↓"
                        return msg

                class Default:
                    def text(module_uuid: UUID) -> str:
                        module: Module = get_module_by_uuid(module_uuid)
                        if not module:
                            raise Exception("Не удалось найти модуль")
                        
                        enabled = "🟢 Включен" if module.enabled else "🔴 Выключен"
                        msg = f"🔧 <b>Управлением модулем</b>" \
                            f"\n" \
                            f"\n→ Состояние: <code>{enabled}</code>" \
                            f"\n" \
                            f"\n→ UUID: <code>{module.uuid}</code>" \
                            f"\n→ Название: <code>{module.meta.name}</code>" \
                            f"\n→ Версия: <code>{module.meta.version}</code>" \
                            f"\n→ Описание: <blockquote>{module.meta.description}</blockquote>" \
                            f"\n" \
                            f"\n→ Авторы: <code>{module.meta.authors}</code>" \
                            f"\n→ Ссылки: <code>{module.meta.links}</code>" \
                            f"\n" \
                            f"\nВыберите действие для управвления ↓"
                        return msg
                    
                    def kb(module_uuid: UUID, page: int) -> InlineKeyboardMarkup:
                        module: Module = get_module_by_uuid(module_uuid)
                        if not module:
                            raise Exception("Не удалось найти модуль")
                        
                        rows = []
                        if module.enabled:
                            btn_disable = InlineKeyboardButton(
                                text="🔴 Отключить модуль",
                                callback_data="disable_module"
                            )
                            rows.append([btn_disable])
                        else:
                            btn_enable = InlineKeyboardButton(
                                text="🟢 Подключить модуль",
                                callback_data="enable_module"
                            )
                            rows.append([btn_enable])
                        btn_refresh = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.ModulePage(
                                uuid=module_uuid
                            ).pack()
                        )
                        rows.append([btn_refresh])
                        btn_back = InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=CallbackDatas.ModulesPagination(
                                page=page
                            ).pack()
                        )
                        rows.append([btn_back])
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup

    class InstructionNavigation:
        class Default:
            def text() -> str:
                msg = "📖 <b>Инструкция</b>" \
                    "\nВ этом разделе описаны инструкции по работе с ботом" \
                    "\n" \
                    "\nПеремещайтесь по разделам ниже ↓"
                return msg
                
            def kb() -> InlineKeyboardMarkup:
                btn1 = InlineKeyboardButton(
                    text="⌨️ Команды",
                    callback_data=CallbackDatas.InstructionNavigation(
                        to="commands"
                    ).pack()
                )
                btn_back = InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=CallbackDatas.MenuNavigation(
                        to="default"
                    ).pack()
                )
                rows = [[btn1], [btn_back]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
            
        class Commands:
            def text() -> str:
                msg = "📖 <b>Инструкция → ⌨️ Команды</b>" \
                    "\n" \
                    "\n<b>Команды покупателя:</b>" \
                    "\n→ <code>!команды</code> — отображает меню с доступными для покупателя командами" \
                    "\n→ <code>!продавец</code> — уведомляет и вызывает продавца в диалог с покупателем (пишет вам в Telegram сообщение с просьбой о помощи)" \
                    "\n" \
                    "\nВыберите действие ↓"
                return msg
            
            def kb() -> InlineKeyboardMarkup:
                btn_back = InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=CallbackDatas.MenuNavigation(
                        to="instruction"
                    ).pack()
                )
                rows = [[btn_back]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup

    class SettingsNavigation:
        class Default:
            def text() -> str:
                msg = "⚙️ <b>Настройки FunPay бота</b>" \
                    "\nВ этом разделе вы можете настроить бота" \
                    "\n" \
                    "\nПеремещайтесь по разделам ниже ↓"
                return msg
                
            def kb() -> InlineKeyboardMarkup:
                btn1 = InlineKeyboardButton(
                    text="🤖 Настройки бота",
                    callback_data=CallbackDatas.BotSettingsNavigation(
                        to="default"
                    ).pack()
                )
                btn2 = InlineKeyboardButton(
                    text="📰 Настройки лотов",
                    callback_data=CallbackDatas.LotsSettingsNavigation(
                        to="default"
                    ).pack(),
                )
                btn_back = InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=CallbackDatas.MenuNavigation(
                        to="default"
                    ).pack()
                )
                rows = [[btn1], [btn2], [btn_back]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup

        class BotSettings:
            class Default:
                class Loading:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота</b>" \
                            f"\n" \
                            f"\n<b>Основные настройки:</b>" \
                            f"\n→ golden_key: <i>загрузка</i>" \
                            f"\n→ user_agent: <i>загрузка</i>" \
                            f"\n" \
                            f"\nПеремещайтесь по разделам ниже, чтобы изменить значения параметров ↓"
                        return msg
                    
                class Error:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота</b>" \
                            f"\n" \
                            f"\n<b>Основные настройки:</b>" \
                            f"\n→ golden_key: <i>не удалось загрузить</i>" \
                            f"\n→ user_agent: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\nПеремещайтесь по разделам ниже, чтобы изменить значения параметров ↓"
                        return msg
                    
                class Default:
                    def text() -> str:
                        config = Config().get()
                        golden_key = config["golden_key"][:3] + "*" * (len(config["golden_key"]) - 3) if config["golden_key"] else "❌ Не задано"
                        user_agent = config["user_agent"] if config["user_agent"] else "❌ Не задано"
                        msg = f"🤖 <b>Настройки бота</b>" \
                            f"\n" \
                            f"\n<b>Основные настройки</b>:" \
                            f"\n→ golden_key: <code>{golden_key}</code>" \
                            f"\n→ user_agent: <code>{user_agent}</code>" \
                            f"\n" \
                            f"\nПеремещайтесь по разделам ниже, чтобы изменить значения параметров ↓"
                        return msg
                    
                    def kb() -> InlineKeyboardMarkup:
                        btn1 = InlineKeyboardButton(
                            text="🔑 Авторизация",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="authorization"
                            ).pack()
                        )
                        btn2 = InlineKeyboardButton(
                            text="📶 Соединение",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="connection"
                            ).pack()
                        )
                        btn3 = InlineKeyboardButton(
                            text="🎫 Лоты",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="lots"
                            ).pack()
                        )
                        btn4 = InlineKeyboardButton(
                            text="✉️ Сообщения",
                            callback_data=CallbackDatas.MessagesPagination(
                                page=0
                            ).pack()
                        )
                        btn5 = InlineKeyboardButton(
                            text="⌨️ Пользовательские команды",
                            callback_data=CallbackDatas.CustomCommandsPagination(
                                page=0
                            ).pack()
                        )
                        btn6 = InlineKeyboardButton(
                            text="🚀 Автоматическая выдача",
                            callback_data=CallbackDatas.AutoDeliveriesPagination(
                                page=0
                            ).pack()
                        )
                        btn7 = InlineKeyboardButton(
                            text="🔧 Прочее",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="other"
                            ).pack()
                        )
                        btn_refresh = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="default"
                            ).pack()
                        )
                        btn_back = InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=CallbackDatas.MenuNavigation(
                                to="settings"
                            ).pack()
                        )
                        rows = [[btn1, btn2], [btn3, btn4], [btn5], [btn6], [btn7], [btn_refresh], [btn_back]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                
            class Authorization:
                class Error:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота → 🔑 Авторизация</b>"\
                              f"\n" \
                              f"\n→ golden_key: <i>не удалось загрузить</i>" \
                              f"\n→ user_agent: <i>не удалось загрузить</i>" \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓"
                        return msg
                    
                class Loading:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота → 🔑 Авторизация</b>"\
                              f"\n" \
                              f"\n→ golden_key: <i>загрузка</i>" \
                              f"\n→ user_agent: <i>загрузка</i>" \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓"
                        return msg
                        
                class Default:
                    def text() -> str:
                        config = Config().get()
                        user_agent = config["user_agent"] if config["user_agent"] else "❌ Не задано"
                        golden_key = config["golden_key"][:3] + "*" * (len(config['golden_key']) - 3) if config["golden_key"] else "❌ Не задано"
                        msg = f"🤖 <b>Настройки бота → 🔑 Авторизация</b>"\
                              f"\n" \
                              f"\n→ golden_key: <code>{golden_key}</code>" \
                              f"\n→ user_agent: <code>{user_agent}</code>" \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓"
                        return msg
                    
                    def kb() -> InlineKeyboardMarkup:
                        btn1 = InlineKeyboardButton(
                            text="🔑 golden_key",
                            callback_data="enter_golden_key"
                        )
                        btn2 = InlineKeyboardButton(
                            text="🎩 user_agent",
                            callback_data="enter_user_agent"
                        )
                        btn_refresh = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="authorization"
                            ).pack()
                        )
                        btn_back = InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="default"
                            ).pack()
                        )
                        rows = [[btn1, btn2], [btn_refresh], [btn_back]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class EnterGoldenKey:
                    def text() -> str:
                        config = Config().get()
                        msg = f"🔑 <b>Введите новый golden_key вашего FunPay аккаунта ↓</b>" \
                              f"\nТекущее значение: <code>{config['golden_key']}</code>"
                        return msg
                    
                class GoldenKeyChanged:
                    def text(new):
                        msg = f"✅ <b>golden_key</b> был успешно изменён на <code>{new}</code>"
                        return msg
                    
                class EnterUserAgent:
                    def text() -> str:
                        config = Config().get()
                        user_agent = config["user_agent"] if config["user_agent"] != "" else "❌ Не задано"
                        msg = f"🎩 <b>Введитe новый user_agent вашего браузера ↓</b>" \
                              f"\nТекущее значение: <code>{user_agent}</code>"
                        return msg
                    
                class UserAgentChanged:
                    def text(new):
                        msg = f"✅ <b>user_agent</b> был успешно изменён на <code>{new}</code>"
                        return msg
                    
            class Connection:
                class Error:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота → 📶 Соединение</b>"\
                              f"\n" \
                              f"\n→ Таймаут подключения к funpay.com: <i>не удалось загрузить</i>" \
                              f"\n→ Периодичность запросов к funpay.com: <i>не удалось загрузить</i>" \
                              f"\n" \
                              f"\n<b>Что такое таймаут подключения к funpay.com?</b>" \
                              f"\nЭто максимальное время, за которое должен прийти ответ на запрос с сайта FunPay. " \
                              f"Если время истекло, а ответ не пришёл - бот выдаст ошибку. Если у вас слабый интернет, " \
                              f"указывайте значение больше" \
                              f"\n" \
                              f"\n<b>Что такое периодичность запросов к funpay.com?</b>" \
                              f"\nС какой периодичностью будут отправляться запросы на FunPay для получения событий. " \
                              f"Не рекомендуем ставить ниже 4 секунд, так как FunPay попросту может забанить ваш IP " \
                              f"адрес, и вы уже не сможете отправлять с него запросы" \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓"
                        return msg

                class Loading:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота → 📶 Соединение</b>"\
                              f"\n" \
                              f"\n→ Таймаут подключения к funpay.com: <i>загрузка</i>" \
                              f"\n→ Периодичность запросов к funpay.com: <i>загрузка</i>" \
                              f"\n" \
                              f"\n<b>Что такое таймаут подключения к funpay.com?</b>" \
                              f"\nЭто максимальное время, за которое должен прийти ответ на запрос с сайта FunPay. " \
                              f"Если время истекло, а ответ не пришёл - бот выдаст ошибку. Если у вас слабый интернет, " \
                              f"указывайте значение больше" \
                              f"\n" \
                              f"\n<b>Что такое периодичность запросов к funpay.com?</b>" \
                              f"\nС какой периодичностью будут отправляться запросы на FunPay для получения событий. " \
                              f"Не рекомендуем ставить ниже 4 секунд, так как FunPay попросту может забанить ваш IP " \
                              f"адрес, и вы уже не сможете отправлять с него запросы" \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓"
                        return msg

                class Default:
                    def text() -> str:
                        config = Config().get()

                        msg = f"🤖 <b>Настройки бота → 📶 Соединение</b>"\
                              f"\n" \
                              f"\n→ Таймаут подключения к funpay.com: <code>{config['funpayapi_timeout']}</code> сек." \
                              f"\n→ Периодичность запросов к funpay.com: <code>{config['runner_requests_delay']}</code> сек." \
                              f"\n" \
                              f"\n<b>Что такое таймаут подключения к funpay.com?</b>" \
                              f"\nЭто максимальное время, за которое должен прийти ответ на запрос с сайта FunPay. " \
                              f"Если время истекло, а ответ не пришёл - бот выдаст ошибку. Если у вас слабый интернет, " \
                              f"указывайте значение больше" \
                              f"\n" \
                              f"\n<b>Что такое периодичность запросов к funpay.com?</b>" \
                              f"\nС какой периодичностью будут отправляться запросы на FunPay для получения событий. " \
                              f"Не рекомендуем ставить ниже 4 секунд, так как FunPay попросту может забанить ваш IP " \
                              f"адрес, и вы уже не сможете отправлять с него запросы" \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓"
                        return msg

                    def kb() -> InlineKeyboardMarkup:
                        btn1 = InlineKeyboardButton(
                            text="🛜 Таймаут подключения",
                            callback_data="enter_funpayapi_timeout"
                        )
                        btn2 = InlineKeyboardButton(
                            text="⏱️ Периодичность запросов",
                            callback_data="enter_runner_requests_delay"
                        )
                        btn_update = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="connection"
                            ).pack()
                        )
                        btn_back = InlineKeyboardButton(
                            text="← Назад",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="default"
                            ).pack()
                        )
                        rows = [[btn1], [btn2], [btn_update], [btn_back]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                
                class EnterFunpayApiTimeout:
                    def text() -> str:
                        config = Config().get()
                        msg = f"🛜 <b>Введите новый таймаут подключения к funpay.com ↓</b>" \
                              f"\nТекущее значение: <code>{config['funpayapi_timeout']}</code> сек."
                        return msg
                    
                class FunpayApiTimeoutChanged:
                    def text(new):
                        msg = f"✅ <b>Таймаут подключения к funpay.com</b> был успешно изменён на <code>{new}</code> сек."
                        return msg
                
                class EnterRunnerRequestsDelay:
                    def text() -> str:
                        config = Config().get()
                        msg = f"⏱️ <b>Введите новую периодичность запросов к funpay.com ↓</b>" \
                              f"\nТекущее значение: <code>{config['runner_requests_delay']}</code> сек."
                        return msg
                    
                class RunnerRequestsDelayChanged:
                    def text(new):
                        msg = f"✅ <b>Периодичность запросов к funpay.com</b> была успешно изменена на <code>{new}</code> сек."
                        return msg

            class Lots:
                class Error:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота → 🎫 Лоты</b>"\
                              f"\n" \
                              f"\n→ Автоматическое поднятие лотов: <i>не удалось загрузить</i>" \
                              f"\n→ Интервал сохранения лотов: <i>не удалось загрузить</i>" \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓"
                        return msg

                class Loading:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота → 🎫 Лоты</b>"\
                              f"\n" \
                              f"\n→ Автоматическое поднятие лотов: <i>загрузка</i>" \
                              f"\n→ Интервал сохранения лотов: <i>загрузка</i>" \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓"
                        return msg

                class Default:
                    def text() -> str:
                        config = Config().get()
                        auto_raising_lots_enabled = "🟢 Включено" if config["auto_raising_lots_enabled"] == True else "🔴 Выключено"
                        
                        msg = f"🤖 <b>Настройки бота → 🎫 Лоты</b>"\
                              f"\n" \
                              f"\n→ Автоматическое поднятие лотов: <code>{auto_raising_lots_enabled}</code>" \
                              f"\n→ Интервал сохранения лотов: <code>{config['lots_saving_interval']}</code> сек." \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓" 
                        return msg

                    def kb() -> InlineKeyboardMarkup:
                        config = Config().get()
                        rows = []
                        
                        if config["auto_raising_lots_enabled"]:
                            btn_disable = InlineKeyboardButton(
                                text="🔴 ВЫКЛ Автоподнятие лотов",
                                callback_data="disable_auto_raising_lots"
                            )
                            rows.append([btn_disable])
                        else:
                            btn_enable = InlineKeyboardButton(
                                text="🟢 ВКЛ Автоподнятие лотов",
                                callback_data="enable_auto_raising_lots"
                            )
                            rows.append([btn_enable])
                        btn1 = InlineKeyboardButton(
                            text="⏲️ Интервал сохранения лотов",
                            callback_data="enter_lots_saving_interval"
                        )
                        btn_refresh = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="lots"
                            ).pack()
                        )
                        rows.append([btn_refresh])
                        btn_back = InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="default"
                            ).pack()
                        )
                        rows.append([btn_back])
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class EnterLotsSavingInterval:
                    def text() -> str:
                        config = Config().get()
                        msg = f"⏲️ <b>Введите новый интервал сохранения лотов ↓</b>" \
                              f"\nТекущее значение: <code>{config['lots_saving_interval']}</code> сек."
                        return msg
                    
                class LotsSavingIntervalChanged:
                    def text(new) -> str:
                        msg = f"✅ <b>Интервал сохранения лотов</b> был успешно изменён на <code>{new}</code>" 
                        return msg
                    
            class CustomCommands:
                class Pagination:
                    def text() -> str:
                        custom_commands = CustomCommands().get()
                        msg = f"🤖 <b>Настройки бота</b> → ⌨️ <b>Пользовательские команды</b>" \
                              f"\nВсего <b>{len(custom_commands.keys())}</b> пользовательских команд в конфиге" \
                              f"\n\nПеремещайтесь по разделам ниже. Нажмите на команду, чтобы перейти в её редактирование ↓"
                        return msg
                    
                    def kb(page: int = 0) -> InlineKeyboardMarkup:
                        custom_commands = CustomCommands().get()

                        rows = []
                        items_per_page = 7
                        total_pages = math.ceil(len(custom_commands.keys())/items_per_page)
                        total_pages = total_pages if total_pages > 0 else 1

                        if page < 0:
                            page = 0
                        elif page >= total_pages:
                            page = total_pages-1

                        start_offset = page * items_per_page
                        end_offset = start_offset + items_per_page

                        for command in list(custom_commands.keys())[start_offset:end_offset]:
                            btn = InlineKeyboardButton(
                                text=command,
                                callback_data=CallbackDatas.CustomCommandPage(
                                    command=command
                                ).pack()
                            )
                            rows.append([btn])
                            
                        buttons_row = []
                        if page > 0:
                            btn_back = InlineKeyboardButton(
                                text="←",
                                callback_data=CallbackDatas.CustomCommandsPagination(
                                    page=page-1
                                ).pack()
                            )
                        else:
                            btn_back = InlineKeyboardButton(
                                text="🛑",
                                callback_data="123"
                            )
                        buttons_row.append(btn_back)
                            
                        btn_pages = InlineKeyboardButton(
                            text=f"{page+1}/{total_pages}",
                            callback_data="enter_custom_command_page"
                        )
                        buttons_row.append(btn_pages)
                        
                        if end_offset < total_pages:
                            btn_next = InlineKeyboardButton(
                                text="→",
                                callback_data=CallbackDatas.CustomCommandsPagination(
                                    page=page+1
                                ).pack()
                            )
                        else:
                            btn_next = InlineKeyboardButton(
                                text="🛑",
                                callback_data="123"
                            )
                        buttons_row.append(btn_next)
                        rows.append(buttons_row)

                        btn1 = InlineKeyboardButton(
                            text="➕⌨️ Добавить пользовательскую команду",
                            callback_data="enter_custom_command"
                        )
                        rows.append([btn1])
                        btn2 = InlineKeyboardButton(
                            text="🚪 Выход",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="default"
                            ).pack()
                        )
                        rows.append([btn2])
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class Page:
                    class Error:
                        def text() -> str:
                            msg = f"✏️ <b>Редактирование пользовательской команды</b>" \
                                f"\n" \
                                f"\n→ Команда: <i>не удалось загрузить</i>" \
                                f"\n→ Ответ: <i>не удалось загрузить</i>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg

                    class Loading:
                        def text() -> str:
                            msg = f"✏️ <b>Редактирование пользовательской команды</b>" \
                                f"\n" \
                                f"\n→ Команда: <i>загрузка</i>" \
                                f"\n→ Ответ: <i>загрузка</i>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg

                    class Default:
                        def text(command: str) -> str:
                            custom_commands = CustomCommands().get()
                            command_text = "\n".join(custom_commands[command])
                            msg = f"✏️ <b>Редактирование пользовательской команды</b>" \
                                f"\n" \
                                f"\n→ Команда: <code>{command}</code>" \
                                f"\n→ Ответ: \n<blockquote>{command_text}</blockquote>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg
                        
                        def kb(command, page) -> InlineKeyboardMarkup:
                            btn1 = InlineKeyboardButton(
                                text="✍️ Текст ответа",
                                callback_data="enter_new_custom_command_answer"
                            )
                            btn2 = InlineKeyboardButton(
                                text="🗑️ Удалить команду",
                                callback_data="confirm_deleting_custom_command"
                            )
                            btn_refresh = InlineKeyboardButton(
                                text="🔄️ Обновить",
                                callback_data=CallbackDatas.CustomCommandPage(
                                    command=command
                                ).pack()
                            )
                            btn_back = InlineKeyboardButton(
                                text="⬅️ Назад",
                                callback_data=CallbackDatas.CustomCommandsPagination(
                                    page=page
                                ).pack()
                            )
                            rows = [[btn1, btn2], [btn_refresh], [btn_back]]
                            markup = InlineKeyboardMarkup(inline_keyboard=rows)
                            return markup
                    
                class EnterCustomCommandsPage:
                    def text() -> str:
                        msg = f"📃 Введите номер страницы для перехода ↓" 
                        return msg
                    
                class EnterCustomCommand:
                    def text() -> str:
                        msg = f"⌨️ <b>Введите название команды ↓</b>" \
                              f"\nТекст, который должен будет вводить покупатель, чтобы ему выдался ответ"
                        return msg
                    
                class EnterCustomCommandAnswer:
                    def text() -> str:
                        msg = f"✍️ <b>Введите ответ команды ↓</b>" \
                              f"\nТекст, который будет выдавать покуптаелю после ввода команды"
                        return msg
                    
                class ConfirmAddingCustomCommand:
                    def text(command, command_answer) -> str:
                        msg = f"➕⌨️ <b>Подтвердите добавление новой пользовательской команды</b>" \
                              f"\nКоманда: <code>{command}</code>" \
                              f"\nОтвет: <blockquote>{command_answer}</blockquote>"
                        return msg

                    def kb() -> InlineKeyboardMarkup:
                        btn1 = InlineKeyboardButton(
                            text="✅ Подтвердить",
                            callback_data="add_custom_command"
                        )
                        btn2 = InlineKeyboardButton(
                            text="❌ Отменить",
                            callback_data="destroy"
                        )
                        rows = [[btn1, btn2]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class CustomCommandAdded:
                    def text(command) -> str:
                        msg = f"✅ Пользовательская команда <code>{command}</code> <b>была успешно добавлена</b>" 
                        return msg
                    
                class EnterNewCustomCommandAnswer:
                    def text(command) -> str:
                        custom_commands = CustomCommands().get()
                        command_answer = "\n".join(custom_commands[command])
                        msg = f"✍️ <b>Введите новый текст ответа ↓</b>" \
                              f"\nКоманда: <code>{command}</code>" \
                              f"\nТекущий ответ: <blockquote>{command_answer}</blockquote>"
                        return msg
                    
                class CustomCommandAnswerChanged:
                    def text(new, command) -> str:
                        msg = f"✅ Текст ответа команды <code>{command}</code> <b>был успешно изменён</b> на:\n<blockquote>{new}</blockquote>" 
                        return msg
                    
                class ConfirmDeletingCustomCommand:
                    def text(command) -> str:
                        msg = f"🗑️ <b>Подтвердите удаление пользовательской команды</b>" \
                            f"\nЭто действие удалит пользовательскую команду <code>{command}</code>" 
                        return msg

                    def kb() -> InlineKeyboardMarkup:
                        btn1 = InlineKeyboardButton(
                            text="✅ Подтвердить",
                            callback_data="delete_custom_command"
                        )
                        btn2 = InlineKeyboardButton(
                            text="❌ Отменить",
                            callback_data="destroy"
                        )
                        rows = [[btn1, btn2]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class CustomComandDeleted:
                    def text(command) -> str:
                        msg = f"✅ Пользовательская команда <code>{command}</code> <b>была успешно удалена</b>" 
                        return msg
                    
            class AutoDeliveries:
                class Pagination:
                    def text() -> str:
                        auto_deliveries = AutoDeliveries().get()
                        msg = f"🤖 <b>Настройки бота</b> → 🚀 <b>Автоматическая выдача</b>" \
                              f"\nВсего <b>{len(auto_deliveries.keys())}</b> настроенных лотов для авто-выдачи в конфиге" \
                              f"\n\nПеремещайтесь по разделам ниже. Нажмите на ID лота, чтобы перейти в редактирование его авто-выдачи ↓"
                        return msg
                    
                    def kb(page: int = 0) -> InlineKeyboardMarkup:
                        auto_deliveries = AutoDeliveries().get()

                        rows = []
                        items_per_page = 7
                        total_pages = math.ceil(len(auto_deliveries.keys())/items_per_page)
                        total_pages = total_pages if total_pages > 0 else 1

                        if page < 0:
                            page = 0
                        elif page >= total_pages:
                            page = total_pages-1

                        start_offset = page * items_per_page
                        end_offset = start_offset + items_per_page

                        for lot_id in list(auto_deliveries.keys())[start_offset:end_offset]:
                            auto_delivery_text = " ".join(auto_deliveries[lot_id])
                            btn = InlineKeyboardButton(
                                text=f"{lot_id} → {auto_delivery_text[:48]}...",
                                callback_data=CallbackDatas.AutoDeliveryPage(
                                    lot_id=lot_id
                                ).pack()
                            )
                            rows.append([btn])
                            
                        buttons_row = []
                        if page > 0:
                            btn_back = InlineKeyboardButton(
                                text="←",
                                callback_data=CallbackDatas.AutoDeliveriesPagination(
                                    page=page-1
                                ).pack()
                            )
                        else:
                            btn_back = InlineKeyboardButton(
                                text="🛑",
                                callback_data="123"
                            )
                        buttons_row.append(btn_back)
                            
                        btn_pages = InlineKeyboardButton(
                            text=f"{page+1}/{total_pages}",
                            callback_data="enter_auto_deliveries_page"
                        )
                        buttons_row.append(btn_pages)
                        
                        if end_offset < total_pages:
                            btn_next = InlineKeyboardButton(
                                text="→",
                                callback_data=CallbackDatas.AutoDeliveriesPagination(
                                    page=page+1
                                ).pack()
                            )
                        else:
                            btn_next = InlineKeyboardButton(
                                text="🛑",
                                callback_data="123"
                            )
                        buttons_row.append(btn_next)
                        rows.append(buttons_row)

                        btn1 = InlineKeyboardButton(
                            text="➕🚀 Добавить авто-выдачу",
                            callback_data="enter_auto_delivery_lot_id"
                        )
                        rows.append([btn1])
                        btn2 = InlineKeyboardButton(
                            text="🚪 Выход",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="default"
                            ).pack()
                        )
                        rows.append([btn2])
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class Page:
                    class Error:
                        def text() -> str:
                            msg = f"✏️ <b>Редактирование авто-выдачи</b>" \
                                f"\n" \
                                f"\n→ ID лота: <i>не удалось загрузить</i>" \
                                f"\n→ Сообщение после покупки: <i>не удалось загрузить</i>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg

                    class Loading:
                        def text() -> str:
                            msg = f"✏️ <b>Редактирование авто-выдачи</b>" \
                                f"\n" \
                                f"\n→ ID лота: <i>загрузка</i>" \
                                f"\n→ Сообщение после покупки: <i>загрузка</i>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg

                    class Default:
                        def text(lot_id: str) -> str:
                            auto_deliveries = AutoDeliveries().get()
                            auto_delivery_message = "\n".join(auto_deliveries[str(lot_id)])
                            msg = f"✏️ <b>Редактирование авто-выдачи</b>" \
                                f"\n" \
                                f"\n→ ID лота: <code>{lot_id}</code>" \
                                f"\n→ Сообщение после покупки: \n<blockquote>{auto_delivery_message}</blockquote>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg
                        
                        def kb(lot_id, page) -> InlineKeyboardMarkup:
                            btn1 = InlineKeyboardButton(
                                text="✍️ Сообщение после покупки",
                                callback_data="enter_new_auto_delivery_message"
                            )
                            btn2 = InlineKeyboardButton(
                                text="🗑️ Удалить авто-выдачу",
                                callback_data="confirm_deleting_auto_delivery"
                            )
                            btn_refresh = InlineKeyboardButton(
                                text="🔄️ Обновить",
                                callback_data=CallbackDatas.AutoDeliveryPage(
                                    lot_id=lot_id
                                ).pack()
                            )
                            btn_back = InlineKeyboardButton(
                                text="⬅️ Назад",
                                callback_data=CallbackDatas.AutoDeliveriesPagination(
                                    page=page
                                ).pack()
                            )
                            rows = [[btn1], [btn2], [btn_refresh], [btn_back]]
                            markup = InlineKeyboardMarkup(inline_keyboard=rows)
                            return markup
                    
                class EnterAutoDeliveryPage:
                    def text() -> str:
                        msg = f"📃 Введите номер страницы для перехода ↓" 
                        return msg
                    
                class EnterAutoDeliveryLotId:
                    def text() -> str:
                        msg = f"🎫 <b>Введите ID лота ↓</b>" \
                              f"\nID лота, на котором будет работать эта авто-выдача"
                        return msg
                    
                class EnterAutoDeliveryMessage:
                    def text() -> str:
                        msg = f"✍️ <b>Введите сообщение после покупки ↓</b>" \
                              f"\nТекст, который будет выдавать покуптаелю после покупки этого лота"
                        return msg
                    
                class ConfirmAddingAutoDelivery:
                    def text(lot_id, message) -> str:
                        msg = f"➕🚀 <b>Подтвердите добавление новой авто-выдачи</b>" \
                              f"\nID лота: <code>{lot_id}</code>" \
                              f"\nСообщение после покупки: <blockquote>{message}</blockquote>"
                        return msg

                    def kb() -> InlineKeyboardMarkup:
                        btn1 = InlineKeyboardButton(
                            text="✅ Подтвердить",
                            callback_data="add_auto_delivery"
                        )
                        btn2 = InlineKeyboardButton(
                            text="❌ Отменить",
                            callback_data="destroy"
                        )
                        rows = [[btn1, btn2]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class AutoDeliveryAdded:
                    def text(lot_id) -> str:
                        msg = f"✅ Авто-выдача на лот <code>{lot_id}</code> <b>была успешно добавлена</b>" 
                        return msg
                    
                class EnterNewAutoDeliveryMessage:
                    def text(lot_id) -> str:
                        auto_deliveries = AutoDeliveries().get()
                        auto_delivery_message = "\n".join(auto_deliveries[str(lot_id)])
                        msg = f"✍️ <b>Введите новое сообщение после покупки ↓</b>" \
                              f"\nID лота: <code>{lot_id}</code>" \
                              f"\nТекущее сообщение: <blockquote>{auto_delivery_message}</blockquote>"
                        return msg
                    
                class AutoDeliveryMessageChanged:
                    def text(new, lot_id) -> str:
                        msg = f"✅ Сообщение после покупки лота <code>{lot_id}</code> <b>было успешно изменено</b> на:\n<blockquote>{new}</blockquote>" 
                        return msg
                    
                class ConfirmDeletingAutoDelivery:
                    def text(lot_id) -> str:
                        msg = f"🗑️ <b>Подтвердите удаление авто-выдачи</b>" \
                              f"\nЭто действие удалит авто-выдачу на лот <code>{lot_id}</code>" 
                        return msg

                    def kb() -> InlineKeyboardMarkup:
                        btn1 = InlineKeyboardButton(
                            text="✅ Подтвердить",
                            callback_data="delete_auto_delivery"
                        )
                        btn2 = InlineKeyboardButton(
                            text="❌ Отменить",
                            callback_data="destroy"
                        )
                        rows = [[btn1, btn2]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class AutoDeliveryDeleted:
                    def text(lot_id) -> str:
                        msg = f"✅ Авто-выдача на лот <code>{lot_id}</code> <b>была успешно удалена</b>" 
                        return msg
                
            class Messages:
                class Pagination:
                    def text() -> str:
                        messages = Messages().get()
                        if not messages:
                            raise Exception("В конфиге нет ни одного сообщения")
                        msg = f"🤖 <b>Настройки бота</b> → ✉️ <b>Сообщения</b>" \
                              f"\nВсего <b>{len(messages.keys())}</b> настраиваемых сообщений в конфиге" \
                              f"\n\nПеремещайтесь по разделам ниже. Нажмите на сообщение, чтобы перейти в его редактирование ↓"
                        return msg
                    
                    def kb(page: int = 0) -> InlineKeyboardMarkup:
                        messages = Messages().get()
                        if not messages:
                            raise Exception("В конфиге нет ни одного сообщения")

                        rows = []
                        items_per_page = 8
                        total_pages = math.ceil(len(messages.keys())/items_per_page)
                        total_pages = total_pages if total_pages > 0 else 1

                        if page < 0:
                            page = 0
                        elif page >= total_pages:
                            page = total_pages-1

                        start_offset = page * items_per_page
                        end_offset = start_offset + items_per_page

                        for message in list(messages.keys())[start_offset:end_offset]:
                            btn = InlineKeyboardButton(
                                text=message,
                                callback_data=CallbackDatas.MessagePage(
                                    message_id=message
                                ).pack()
                            )
                            rows.append([btn])
                            
                        buttons_row = []
                        if page > 0:
                            btn_back = InlineKeyboardButton(
                                text="←",
                                callback_data=CallbackDatas.MessagesPagination(
                                    page=page-1
                                ).pack()
                            )
                        else:
                            btn_back = InlineKeyboardButton(
                                text="🛑",
                                callback_data="123"
                            )
                        buttons_row.append(btn_back)

                            
                        btn_pages = InlineKeyboardButton(
                            text=f"{page+1}/{total_pages}",
                            callback_data="enter_messages_page"
                        )
                        buttons_row.append(btn_pages)
                        
                        if end_offset < total_pages:
                            btn_next = InlineKeyboardButton(
                                text="→",
                                callback_data=CallbackDatas.MessagesPagination(
                                    page=page+1
                                ).pack()
                            )
                        else:
                            btn_next = InlineKeyboardButton(
                                text="🛑",
                                callback_data="123"
                            )
                        buttons_row.append(btn_next)
                        rows.append(buttons_row)

                        btn1 = InlineKeyboardButton(
                            text="🚪 Выход",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="default"
                            ).pack()
                        )
                        rows.append([btn1])
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
                class Page:
                    class Error:
                        def text() -> str:
                            msg = f"✒️ <b>Редактирование сообщения</b>" \
                                f"\n" \
                                f"\n→ ID сообщения: <i>не удалось загрузить</i>" \
                                f"\n→ Текст сообщения: <i>не удалось загрузить</i>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg

                    class Loading:
                        def text() -> str:
                            msg = f"✒️ <b>Редактирование сообщения</b>" \
                                f"\n" \
                                f"\n→ ID сообщения: <i>загрузка</i>" \
                                f"\n→ Текст сообщения: <i>загрузка</i>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg

                    class Default:
                        def text(message_id) -> str:
                            messages = Messages().get()
                            message_text = "\n".join(messages[message_id])
                            msg = f"✒️ <b>Редактирование сообщения</b>" \
                                f"\n" \
                                f"\n→ ID сообщения: <code>{message_id}</code>" \
                                f"\n→ Текст сообщения: \n<blockquote>{message_text}</blockquote>" \
                                f"\n" \
                                f"\nВыберите параметр для изменения ↓"
                            return msg
                        
                        def kb(message_id, page) -> InlineKeyboardMarkup:
                            btn1 = InlineKeyboardButton(
                                text="✍️ Текст сообщения",
                                callback_data="enter_message_text"
                            )
                            btn_refresh = InlineKeyboardButton(
                                text="🔄️ Обновить",
                                callback_data=CallbackDatas.MessagePage(
                                    message_id=message_id
                                ).pack()
                            )
                            btn_back = InlineKeyboardButton(
                                text="⬅️ Назад",
                                callback_data=CallbackDatas.MessagesPagination(
                                    page=page
                                ).pack()
                            )
                            rows = [[btn1], [btn_refresh], [btn_back]]
                            markup = InlineKeyboardMarkup(inline_keyboard=rows)
                            return markup
                    
                class EnterMessagesPage:
                    def text() -> str:
                        msg = f"📃 Введите номер страницы для перехода ↓" 
                        return msg
                    
                class EnterMessageText:
                    def text(message_id) -> str:
                        messages = Messages().get()
                        message_text = "\n".join(messages[message_id])
                        msg = f"✍️ <b>Введите новый текст сообщения ↓</b>" \
                              f"\nID сообщения: \n<code>{message_id}</code>" \
                              f"\nТекущий текст: \n<blockquote>{message_text}</blockquote>"
                        return msg
                    
                class MessageTextChanged:
                    def text(new, message_id) -> str:
                        msg = f"✅ Текст сообщения <code>{message_id}</code> <b>был успешно изменён</b> на:\n<blockquote>{new}</blockquote>" 
                        return msg
                    
            class Other:
                class Error:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота → 🔧 Прочее</b>" \
                              f"\n" \
                              f"\n→ Автоматические ответы на отзывы: <i>не удалось загрузить</i>" \
                              f"\n→ Приветственное сообщение: <i>не удалось загрузить</i>" \
                              f"\n→ Пользовательские команды: <i>не удалось загрузить</i>" \
                              f"\n→ Авто-выдача: <i>не удалось загрузить</i>" \
                              f"\n" \
                              f"\n<b>Что такое автоматические ответы на отзывы?</b>" \
                              f"\nКогда покупатель будет оставлять отзыв, бот будет автоматически отвечать на него. " \
                              f"В ответе на отзыв будут написаны детали заказа." \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓" 
                        return msg

                class Loading:
                    def text() -> str:
                        msg = f"🤖 <b>Настройки бота → 🔧 Прочее</b>" \
                              f"\n" \
                              f"\n→ Автоматические ответы на отзывы: <i>загрузка</i>" \
                              f"\n→ Приветственное сообщение: <i>загрузка</i>" \
                              f"\n→ Пользовательские команды: <i>загрузка</i>" \
                              f"\n→ Авто-выдача: <i>загрузка</i>" \
                              f"\n" \
                              f"\n<b>Что такое автоматические ответы на отзывы?</b>" \
                              f"\nКогда покупатель будет оставлять отзыв, бот будет автоматически отвечать на него. " \
                              f"В ответе на отзыв будут написаны детали заказа." \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓" 
                        return msg

                class Default:
                    def text() -> str:
                        config = Config().get()
                        auto_reviews_replies_enabled = "🟢 Включено" if config["auto_reviews_replies_enabled"] else "🔴 Выключено"
                        first_message_enabled = "🟢 Включено" if config["first_message_enabled"] else "🔴 Выключено"
                        custom_commands_enabled = "🟢 Включено" if config["custom_commands_enabled"] else "🔴 Выключено"
                        auto_delivery_enabled = "🟢 Включено" if config["auto_delivery_enabled"] else "🔴 Выключено"
                        msg = f"🤖 <b>Настройки бота → 🔧 Прочее</b>" \
                              f"\n" \
                              f"\n→ Автоматические ответы на отзывы: <code>{auto_reviews_replies_enabled}</code>" \
                              f"\n→ Приветственное сообщение: <code>{first_message_enabled}</code>" \
                              f"\n→ Пользовательские команды: <code>{custom_commands_enabled}</code>" \
                              f"\n→ Авто-выдача: <code>{auto_delivery_enabled}</code>" \
                              f"\n" \
                              f"\n<b>Что такое автоматические ответы на отзывы?</b>" \
                              f"\nКогда покупатель будет оставлять отзыв, бот будет автоматически отвечать на него. " \
                              f"В ответе на отзыв будут написаны детали заказа." \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓" 
                        return msg
                    
                    def kb() -> InlineKeyboardMarkup:
                        config = Config().get()
                        rows = []

                        if config["auto_reviews_replies_enabled"]:
                            btn_disable = InlineKeyboardButton(
                                text="🔴 ВЫКЛ авто-ответы на отзывы",
                                callback_data="disable_auto_reviews_replies"
                            )
                            rows.append([btn_disable])
                        else:
                            btn_enable = InlineKeyboardButton(
                                text="🟢 ВКЛ авто-ответы на отзывы",
                                callback_data="enable_auto_reviews_replies"
                            )
                            rows.append([btn_enable])

                        if config["first_message_enabled"]:
                            btn_disable = InlineKeyboardButton(
                                text="🔴 ВЫКЛ приветственное сообщение",
                                callback_data="disable_first_message"
                            )
                            rows.append([btn_disable])
                        else:
                            btn_enable = InlineKeyboardButton(
                                text="🟢 ВКЛ приветственное сообщение",
                                callback_data="enable_first_message"
                            )
                            rows.append([btn_enable])

                        if config["custom_commands_enabled"]:
                            btn_disable = InlineKeyboardButton(
                                text="🔴 ВЫКЛ пользовательские ответы",
                                callback_data="disable_custom_commands"
                            )
                            rows.append([btn_disable])
                        else:
                            btn_enable = InlineKeyboardButton(
                                text="🟢 ВКЛ пользовательские ответы",
                                callback_data="enable_custom_commands"
                            )
                            rows.append([btn_enable])

                        if config["auto_delivery_enabled"]:
                            btn_disable = InlineKeyboardButton(
                                text="🔴 ВЫКЛ авто-выдачу",
                                callback_data="disable_auto_delivery"
                            )
                            rows.append([btn_disable])
                        else:
                            btn_enable = InlineKeyboardButton(
                                text="🟢 ВКЛ авто-выдачу",
                                callback_data="enable_auto_delivery"
                            )
                            rows.append([btn_enable])

                        btn_refresh = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="other"
                            ).pack()
                        )
                        rows.append([btn_refresh])
                        btn_back = InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=CallbackDatas.BotSettingsNavigation(
                                to="default"
                            ).pack()
                        )
                        rows.append([btn_back])
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                    
        class LotsSettings:
            class Error:
                def text() -> str:
                    msg = f"📰 <b>Настройки лотов</b>" \
                          f"\n" \
                          f"\n→ Активные лоты: <i>не удалось загрузить</i>" \
                          f"\n→ Сохранённые лоты: <i>не удалось загрузить</i>" \
                          f"\n" \
                          f"\nВыберите действие для управления ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"📰 <b>Настройки лотов</b>" \
                          f"\n" \
                          f"\n→ Активные лоты: <i>загрузка</i>" \
                          f"\n→ Сохранённые лоты: <i>загрузка</i>" \
                          f"\n" \
                          f"\nВыберите действие для управления ↓"
                    return msg

            class Default:
                def text() -> str:
                    funpay_profile = funpaybot.funpay_profile
                    active_lots = funpay_profile.get_lots()
                    saved_lots = Data().get_saved_lots()
                    my_saved_lots = 0
                    for active_lot in active_lots:
                        if active_lot.id in saved_lots["active"] or active_lot.id in saved_lots["inactive"]:
                            my_saved_lots += 1
                    msg = f"📰 <b>Настройки лотов</b>" \
                          f"\n" \
                          f"\n→ Активные лоты: <code>{len(active_lots)}</code>" \
                          f"\n→ Сохранённые лоты: <code>{my_saved_lots}</code>" \
                          f"\n" \
                          f"\nВыберите действие для управления ↓"
                    return msg
                
                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="🟢 Сделать лоты активными",
                        callback_data="confirm_activating_lots"
                    )
                    btn2 = InlineKeyboardButton(
                        text="🔴 Сделать лоты неактивными",
                        callback_data="confirm_deactivating_lots"
                    )
                    btn3 = InlineKeyboardButton(
                        text="📃 Сохранить все лоты профиля",
                        callback_data="save_lots"
                    )
                    btn5 = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.LotsSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    btn6 = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="settings"
                        ).pack()
                    )
                    rows = [[btn1, btn2], [btn3], [btn5], [btn6]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup

            class ConfirmActivatingLots:
                def text() -> str:
                    msg = f"🟢 <b>Подтвердите активацию всех лотов</b>" \
                          f"\nЭто действие активирует только все сохранённые нашим ботом лоты с вашего профиля (интервал сохранения лотов можно указать в разделе настроек бота)" 
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="✅ Подтвердить",
                        callback_data="activate_lots"
                    )
                    btn2 = InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="destroy"
                    )
                    rows = [[btn1, btn2]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup

            class ConfirmDeactivatingLots:
                def text() -> str:
                    msg = f"🔴 <b>Подтвердите деактивацию всех лотов</b>" \
                          f"\nЭто действие деактивирует только все сохранённые нашим ботом лоты с вашего профиля (интервал сохранения лотов можно указать в разделе настроек бота)" 
                    return msg
                
                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="✅ Подтвердить",
                        callback_data="deactivate_lots"
                    )
                    btn2 = InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="destroy"
                    )
                    rows = [[btn1, btn2]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class ActivatingLots:
                def text() -> str:
                    msg = f"🕓 Активация всех лотов вашего профиля, ожидайте..." 
                    return msg

            class DeactivatingLots:
                def text() -> str:
                    msg = f"🕓 Деактивация всех лотов вашего профиля, ожидайте..." 
                    return msg
                
            class LotsActivated:
                def text() -> str:
                    msg = f"🟢 Все ваши лоты были активированы" 
                    return msg

            class LotsDeactivated:
                def text() -> str:
                    msg = f"🔴 Все ваши лоты были деактивированы" 
                    return msg

            class SavingLots:
                def text() -> str:
                    msg = f"🕓 Сохранение всех лотов вашего профиля, ожидайте..." 
                    return msg

            class LotsSaved:
                def text() -> str:
                    msg = f"✅ Все лоты вашего профиля были сохранены" 
                    return msg

class Callbacks:
    class CallSeller:
        def text(calling_name, chat_link) -> str:
            msg = f"🆘 <b>{calling_name}</b> требуется ваша помощь!" \
                  f"\n{chat_link}"
            return msg