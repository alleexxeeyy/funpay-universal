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

from core.modules_manager import ModulesManager, Module
from uuid import UUID

from FunPayAPI import types as fpapi_types

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
            def text() -> str:
                msg = f"🏠 <b>Главное меню</b>" \
                    f"\n" \
                    f"\n<b>FunPay UNIVERSAL</b> v{CURRENT_VERSION} " \
                    f"\nБот-помощник для FunPay" \
                    f"\n" \
                    f"\n<b>Ссылки:</b>" \
                    f"\n→ <b>@alleexxeeyy</b> — главный и единственный разработчик" \
                    f"\n→ <b>@alexeyproduction</b> — канал, где публикуются новости" \
                    f"\n→ <b>@alexey_production_bot</b> — бот для покупки официальных модулей" \
                    f"\n" \
                    f"\nПеремещайтесь по разделам ниже ↓"
                return msg
                
            def kb() -> InlineKeyboardMarkup:
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
                btn4 = InlineKeyboardButton(
                    text="🛒 Активные заказы",
                    callback_data=CallbackDatas.ActiveOrdersPagination(
                        page=0
                    ).pack()
                )
                btn5 = InlineKeyboardButton(
                    text="📖 Инструкция",
                    callback_data=CallbackDatas.InstructionNavigation(
                        to="default"
                    ).pack()
                )
                btn6 = InlineKeyboardButton(
                    text="👨‍💻 Разработчик",
                    url="https://t.me/alleexxeeyy",
                )
                btn7 = InlineKeyboardButton(
                    text="📢 Наш канал",
                    url="https://t.me/alexeyproduction",
                )
                btn8 = InlineKeyboardButton(
                    text="🤖 Наш бот",
                    url="https://t.me/alexey_production_bot",
                )
                rows = [[btn1, btn2], [btn3, btn4], [btn5], [btn6, btn7, btn8]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
                
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
                        f"\n→ Дата запуска: <code>{stats['bot_launch_time'].strftime('%d.%m.%Y %H:%M:%S')}</code>" \
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
                        config = Config.get()
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
                        config = Config.get()
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
                        config = Config.get()
                        msg = f"🔑 <b>Введите новый golden_key вашего FunPay аккаунта ↓</b>" \
                              f"\nТекущее значение: <code>{config['golden_key']}</code>"
                        return msg
                    
                class GoldenKeyChanged:
                    def text(new):
                        msg = f"✅ <b>golden_key</b> был успешно изменён на <code>{new}</code>"
                        return msg
                    
                class EnterUserAgent:
                    def text() -> str:
                        config = Config.get()
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
                        config = Config.get()

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
                        config = Config.get()
                        msg = f"🛜 <b>Введите новый таймаут подключения к funpay.com ↓</b>" \
                              f"\nТекущее значение: <code>{config['funpayapi_timeout']}</code> сек."
                        return msg
                    
                class FunpayApiTimeoutChanged:
                    def text(new):
                        msg = f"✅ <b>Таймаут подключения к funpay.com</b> был успешно изменён на <code>{new}</code> сек."
                        return msg
                
                class EnterRunnerRequestsDelay:
                    def text() -> str:
                        config = Config.get()
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
                        config = Config.get()
                        auto_raising_lots_enabled = "🟢 Включено" if config["auto_raising_lots_enabled"] == True else "🔴 Выключено"
                        
                        msg = f"🤖 <b>Настройки бота → 🎫 Лоты</b>"\
                              f"\n" \
                              f"\n→ Автоматическое поднятие лотов: <code>{auto_raising_lots_enabled}</code>" \
                              f"\n→ Интервал сохранения лотов: <code>{config['lots_saving_interval']}</code> сек." \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓" 
                        return msg

                    def kb() -> InlineKeyboardMarkup:
                        config = Config.get()
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
                        rows.append([btn1])
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
                        config = Config.get()
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
                        custom_commands = CustomCommands.get()
                        msg = f"🤖 <b>Настройки бота</b> → ⌨️ <b>Пользовательские команды</b>" \
                              f"\nВсего <b>{len(custom_commands.keys())}</b> пользовательских команд в конфиге" \
                              f"\n\nПеремещайтесь по разделам ниже. Нажмите на команду, чтобы перейти в её редактирование ↓"
                        return msg
                    
                    def kb(page: int = 0) -> InlineKeyboardMarkup:
                        custom_commands = CustomCommands.get()

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
                                text=f'{command} → {" ".join(custom_commands[command])[:64]}',
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
                        
                        if page < total_pages-1:
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
                            custom_commands = CustomCommands.get()
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
                        custom_commands = CustomCommands.get()
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
                        auto_deliveries = AutoDeliveries.get()
                        msg = f"🤖 <b>Настройки бота</b> → 🚀 <b>Автоматическая выдача</b>" \
                              f"\nВсего <b>{len(auto_deliveries.keys())}</b> настроенных лотов для авто-выдачи в конфиге" \
                              f"\n\nПеремещайтесь по разделам ниже. Нажмите на ID лота, чтобы перейти в редактирование его авто-выдачи ↓"
                        return msg
                    
                    def kb(page: int = 0) -> InlineKeyboardMarkup:
                        auto_deliveries = AutoDeliveries.get()

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
                                text=f"{lot_id} → {auto_delivery_text[:64]}",
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
                        
                        if page < total_pages-1:
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
                            auto_deliveries = AutoDeliveries.get()
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
                        auto_deliveries = AutoDeliveries.get()
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
                        messages = Messages.get()
                        if not messages:
                            raise Exception("В конфиге нет ни одного сообщения")
                        msg = f"🤖 <b>Настройки бота</b> → ✉️ <b>Сообщения</b>" \
                              f"\nВсего <b>{len(messages.keys())}</b> настраиваемых сообщений в конфиге" \
                              f"\n\nПеремещайтесь по разделам ниже. Нажмите на сообщение, чтобы перейти в его редактирование ↓"
                        return msg
                    
                    def kb(page: int = 0) -> InlineKeyboardMarkup:
                        messages = Messages.get()
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
                        
                        if page < total_pages-1:
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
                            messages = Messages.get()
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
                        messages = Messages.get()
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
                        config = Config.get()
                        auto_reviews_replies_enabled = "🟢 Включено" if config["auto_reviews_replies_enabled"] else "🔴 Выключено"
                        first_message_enabled = "🟢 Включено" if config["first_message_enabled"] else "🔴 Выключено"
                        custom_commands_enabled = "🟢 Включено" if config["custom_commands_enabled"] else "🔴 Выключено"
                        auto_deliveries_enabled = "🟢 Включено" if config["auto_deliveries_enabled"] else "🔴 Выключено"
                        msg = f"🤖 <b>Настройки бота → 🔧 Прочее</b>" \
                              f"\n" \
                              f"\n→ Автоматические ответы на отзывы: <code>{auto_reviews_replies_enabled}</code>" \
                              f"\n→ Приветственное сообщение: <code>{first_message_enabled}</code>" \
                              f"\n→ Пользовательские команды: <code>{custom_commands_enabled}</code>" \
                              f"\n→ Авто-выдача: <code>{auto_deliveries_enabled}</code>" \
                              f"\n" \
                              f"\n<b>Что такое автоматические ответы на отзывы?</b>" \
                              f"\nКогда покупатель будет оставлять отзыв, бот будет автоматически отвечать на него. " \
                              f"В ответе на отзыв будут написаны детали заказа." \
                              f"\n" \
                              f"\nВыберите параметр для изменения ↓" 
                        return msg
                    
                    def kb() -> InlineKeyboardMarkup:
                        config = Config.get()
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

                        if config["auto_deliveries_enabled"]:
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
                          f"\n" \
                          f"\nВыберите действие для управления ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"📰 <b>Настройки лотов</b>" \
                          f"\n" \
                          f"\n→ Активные лоты: <i>загрузка</i>" \
                          f"\n" \
                          f"\nВыберите действие для управления ↓"
                    return msg

            class Default:
                def text() -> str:
                    profile = funpaybot.funpay_account.get_user(funpaybot.funpay_account.id)
                    active_lots = profile.get_lots()
                    msg = f"📰 <b>Настройки лотов</b>" \
                          f"\n" \
                          f"\n→ Активные лоты: <code>{len(active_lots)}</code>" \
                          f"\n" \
                          f"\nВыберите действие для управления ↓"
                    return msg
                
                def kb() -> InlineKeyboardMarkup:
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.LotsSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="settings"
                        ).pack()
                    )
                    rows = [[btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
    class Modules:
        class Pagination:
            def text() -> str:
                modules = ModulesManager.get_modules()
                msg = f"🔌 <b>Модули</b>" \
                        f"\nВсего <b>{len(modules)}</b> загруженных модулей" \
                        f"\n\nПеремещайтесь по разделам ниже. Нажмите на название модуля, чтобы перейти в его управление ↓"
                return msg
            
            def kb(page: int = 0) -> InlineKeyboardMarkup:
                modules = ModulesManager.get_modules()

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
                
                if page < total_pages-1:
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
                    module: Module = ModulesManager.get_module_by_uuid(module_uuid)
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
                    module: Module = ModulesManager.get_module_by_uuid(module_uuid)
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
                
    class ActiveOrders:
        class Pagination:
            class Error:
                def text() -> str:
                    msg = f"🛒 <b>Активные заказы</b>" \
                            f"\nВсего <i>не удалось загрузить</i> активных заказов" \
                            f"\n\nПеремещайтесь по разделам ниже. Нажмите на заказ, чтобы перейти на его страницу"
                    return msg
                
                def kb(page: int = 0) -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="...",
                        callback_data="123"
                    )
                    btn2 = InlineKeyboardButton(
                        text="🛑",
                        callback_data="123"
                    )
                    btn3 = InlineKeyboardButton(
                        text="?/?",
                        callback_data="123"
                    )
                    btn4 = InlineKeyboardButton(
                        text="🛑",
                        callback_data="123"
                    )
                    btn5 = InlineKeyboardButton(
                        text="📞 Создать тикет на подтверждение заказов",
                        callback_data="confirm_creating_ticket_to_orders"
                    )
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.ActiveOrdersPagination(
                            page=page
                        ).pack()
                    )
                    btn_exit = InlineKeyboardButton(
                        text="🚪 Выход",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn1], [btn2, btn3, btn4], [btn5], [btn_refresh], [btn_exit]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup

            class Loading:
                def text(loaded: int = 0, count: int | str = 0) -> str:
                    msg = f"🛒 <b>Активные заказы</b>" \
                            f"\nЗагружаю заказы: <b>{loaded}</b>/<b>{count}</b>" \
                            f"\n\nПеремещайтесь по разделам ниже. Нажмите на заказ, чтобы перейти на его страницу"
                    return msg
                
                def kb(page: int = 0) -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="...",
                        callback_data="123"
                    )
                    btn2 = InlineKeyboardButton(
                        text="🛑",
                        callback_data="123"
                    )
                    btn3 = InlineKeyboardButton(
                        text="?/?",
                        callback_data="123"
                    )
                    btn4 = InlineKeyboardButton(
                        text="🛑",
                        callback_data="123"
                    )
                    btn5 = InlineKeyboardButton(
                        text="📞 Создать тикет на подтверждение заказов",
                        callback_data="confirm_creating_ticket_to_orders"
                    )
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.ActiveOrdersPagination(
                            page=page
                        ).pack()
                    )
                    btn_exit = InlineKeyboardButton(
                        text="🚪 Выход",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn1], [btn2, btn3, btn4], [btn5], [btn_refresh], [btn_exit]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
            
            class Default:
                def text(active_orders: list[fpapi_types.OrderShortcut]) -> str:
                    msg = f"🛒 <b>Активные заказы</b>" \
                            f"\nВсего <b>{len(active_orders)}</b> активных заказов" \
                            f"\n\nПеремещайтесь по разделам ниже. Нажмите на заказ, чтобы перейти на его страницу"
                    return msg
            
                def kb(page: int = 0, active_orders: list[fpapi_types.OrderShortcut] = None) -> InlineKeyboardMarkup:
                    rows = []
                    items_per_page = 12
                    items_per_row = 2
                    total_pages = math.ceil(len(active_orders)/items_per_page)
                    total_pages = total_pages if total_pages > 0 else 1

                    if page < 0:
                        page = 0
                    elif page >= total_pages:
                        page = total_pages-1

                    start_offset = page * items_per_page
                    end_offset = start_offset + items_per_page

                    prev_btn = None
                    for i in range(len(active_orders[start_offset:end_offset])):
                        order = active_orders[i+start_offset]
                        btn = InlineKeyboardButton(
                            text=f"#{order.id} ({order.buyer_username})",
                            callback_data=CallbackDatas.ActiveOrderPage(
                                order_id=order.id
                            ).pack()
                        )
                        if i > 0 and i % items_per_row == 0:
                            rows.append([prev_btn, btn])
                        elif page == total_pages and i == len(active_orders[start_offset:end_offset])-1:
                            rows.append([btn])
                        prev_btn = btn
                        
                    buttons_row = []
                    if page > 0:
                        btn_back = InlineKeyboardButton(
                            text="←",
                            callback_data=CallbackDatas.ActiveOrdersPagination(
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
                        callback_data="enter_active_orders_page"
                    )
                    buttons_row.append(btn_pages)
                    
                    if page < total_pages-1:
                        btn_next = InlineKeyboardButton(
                            text="→",
                            callback_data=CallbackDatas.ActiveOrdersPagination(
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

                    btn_create_ticket = InlineKeyboardButton(
                        text="📞 Создать тикет на подтверждение заказов",
                        callback_data="confirm_creating_tickets_to_orders"
                    )
                    rows.append([btn_create_ticket])
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data="refresh_active_orders_pagination"
                    )
                    rows.append([btn_refresh])
                    btn_exit = InlineKeyboardButton(
                        text="🚪 Выход",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows.append([btn_exit])
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
        class EnterActiveOrderPage:
            def text() -> str:
                msg = f"📃 Введите номер страницы для перехода ↓" 
                return msg
            
        class ConfirmCreatingTicketsToOrders:
            def text(active_orders_count) -> str:
                msg = f"➕📞 <b>Подтвердите создание тикетов в тех.поддержку на подтверждение активных заказов</b>" \
                        f"\nЭто действие создаст заявки в тех. поддержку FunPay на подтверждение <code>{active_orders_count}</code> оплаченных заказов" \
                        f"\n\nВсего будет создано <b>{math.ceil(active_orders_count/5)}</b> тикетов <i>(по 5 заказов на 1 тикет, чтобы не перегружать общее количество)</i>"
                return msg

            def kb() -> InlineKeyboardMarkup:
                btn1 = InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data="create_tickets_to_orders"
                )
                btn2 = InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="destroy"
                )
                rows = [[btn1, btn2]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
            
        class CreatingTicketsToOrders:
            def text(active_orders_count, created) -> str:
                msg = f"🕐 Создаю тикеты в тех. поддержку для заказов..." \
                      f"\nПроцесс: <b>{created}</b>/<b>{active_orders_count}</b>"
                return msg
            
        class TicketsToOrdersCreated:
            def text(active_orders_count, created_count) -> str:
                msg = f"✅ Тикеты в тех.поддержку для <b>{created_count}</b>/<b>{active_orders_count}</b> заказов <b>были успешно созданы</b> ↓" \
                      f"\nhttps://support.funpay.com/tickets"
                return msg
        
        class Page:
            class Error:
                def text() -> str:
                    msg = f"📄 <b>Страница активного заказа</b>" \
                        f"\n" \
                        f"\n→ ID заказа: <i>не удалось загрузить</i>" \
                        f"\n→ Покупатель: <i>не удалось загрузить</i>" \
                        f"\n→ Сумма: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Название: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Ссылка: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\nВыберите параметр для изменения ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"📄 <b>Страница активного заказа</b>" \
                        f"\n" \
                        f"\n→ ID заказа: <i>загрузка</i>" \
                        f"\n→ Покупатель: <i>загрузка</i>" \
                        f"\n→ Сумма: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Название: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Ссылка: <i>загрузка</i>" \
                        f"\n" \
                        f"\nВыберите параметр для изменения ↓"
                    return msg

            class Default:
                def text(order: fpapi_types.Order) -> str:
                    msg = f"📄 <b>Страница активного заказа</b>" \
                        f"\n" \
                        f"\n→ ID заказа: <code>{order.id}</code>" \
                        f"\n→ Покупатель: <code>{order.buyer_username}</code>" \
                        f"\n→ Сумма: <code>{order.sum}</code> р." \
                        f"\n" \
                        f"\n→ Название: <blockquote>{order.title}</blockquote>" \
                        f"\n" \
                        f"\n→ Ссылка: <b>https://funpay.com/orders/{order.id}/</b>" \
                        f"\n" \
                        f"\nВыберите действие для управления ↓"
                    return msg
                
                def kb(page: int = 0, order_id: str = "") -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="📞 Создать тикет на подтверждение заказа",
                        callback_data="confirm_creating_ticket_to_order"
                    )
                    btn2 = InlineKeyboardButton(
                        text="🔗 Открыть заказ на сайте",
                        url=f"https://funpay.com/orders/{order_id}/"
                    )
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.ActiveOrderPage(
                            order_id=order_id
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.ActiveOrdersPagination(
                            page=page
                        ).pack()
                    )
                    rows = [[btn1, btn2], [btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class ConfirmCreatingTicketToOrder:
                def text(order_id) -> str:
                    msg = f"➕📞 <b>Подтвердите создание тикета в тех. поддержку на подтверждение заказа</b>" \
                            f"\nЭто действие создаст заявку в тех. поддержку FunPay на подтверждение заказа <code>#{order_id}</code>"
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="✅ Подтвердить",
                        callback_data="create_ticket_to_order"
                    )
                    btn2 = InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="destroy"
                    )
                    rows = [[btn1, btn2]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class CreatingTicketToOrders:
                def text(order_id) -> str:
                    msg = f"🕐 Создаю тикет в тех. поддержку для заказа <code>#{order_id}</code>"
                    return msg
                
            class TicketToOrderCreated:
                def text(order_id, ticket_link) -> str:
                    msg = f"✅ Тикет в тех. поддержку на подтверждение заказа <code>#{order_id}</code> <b>был успешно создан</b>" \
                          f"\n→ {ticket_link}"
                    return msg

class Callbacks:
    class CallSeller:
        def text(calling_name, chat_link) -> str:
            msg = f"🆘 <b>{calling_name}</b> требуется ваша помощь!" \
                  f"\n{chat_link}"
            return msg