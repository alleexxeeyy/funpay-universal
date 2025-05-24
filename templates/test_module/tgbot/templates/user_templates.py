from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..callback_datas import user_callback_datas as CallbackDatas

from fpbot.funpaybot import FunPayBot as MainFunPayBot

from ...fpbot.data import Data
from ...settings import Config
from ...meta import NAME, VERSION

funpaybot = MainFunPayBot()


class Navigation:
    """ Шаблоны навигации по боту """
    class MenuNavigation:
        class Default:
            def text() -> str:
                msg = f"📈 <b>Меню {NAME}</b>" \
                      f"\n" \
                      f"\n<b>{NAME}</b> v{VERSION} " \
                      f"\nТестовый модуль" \
                      f"\n" \
                      f"\n<b>Ссылки:</b>" \
                      f"\n→ <b>@alleexxeeyy</b> — главный и единственный разработчик" \
                      f"\n→ <b>@alexey_production_bot</b> — бот для покупки официальных модулей" \
                      f"\n" \
                      f"\nПеремещайтесь по разделам ниже ↓"
                return msg
                
            def kb() -> InlineKeyboardMarkup:
                btn1 = InlineKeyboardButton(
                    text="🔌 Настройки",
                    callback_data=CallbackDatas.TestModule_SettingsNavigation(
                        to="default"
                    ).pack()
                )
                btn2 = InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data=CallbackDatas.TestModule_MenuNavigation(
                        to="stats"
                    ).pack()
                )
                btn3 = InlineKeyboardButton(
                    text="📖 Инструкция",
                    callback_data=CallbackDatas.TestModule_InstructionNavigation(
                        to="default"
                    ).pack()
                )
                btn4 = InlineKeyboardButton(
                    text="👨‍💻 Разработчик",
                    url="https://t.me/alleexxeeyy",
                )
                btn5 = InlineKeyboardButton(
                    text="🤖 Наш бот",
                    url="https://t.me/alexey_production_bot",
                )

                rows = [[btn1, btn2], [btn3], [btn4, btn5]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
            
        class Stats:
            class Error:
                def text() -> str:
                    msg = f"📊 <b>Статистика {NAME}</b>" \
                        f"\n" \
                        f"\n→ Какая-то статистика: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"📊 <b>Статистика {NAME}</b>" \
                        f"\n" \
                        f"\n→ Какая-то статистика: <i>загрузка</i>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg
                
            class Default:
                def text() -> str:
                    msg = f"📊 <b>Статистика {NAME}</b>" \
                        f"\n" \
                        f"\n→ Какая-то статистика: <code>123</code>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg
                    
                def kb() -> InlineKeyboardMarkup:
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.TestModule_MenuNavigation(
                            to="stats"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.TestModule_MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
    class InstructionNavigation:
        class Default:
            def text() -> str:
                msg = f"📖 <b>Инструкция {NAME}</b>" \
                    "\nВ этом разделе описаны инструкции по работе с модулем" \
                    "\n" \
                    "\nПеремещайтесь по разделам ниже ↓"
                return msg
                
            def kb() -> InlineKeyboardMarkup:
                btn1 = InlineKeyboardButton(
                    text="⌨️ Команды",
                    callback_data=CallbackDatas.TestModule_InstructionNavigation(
                        to="commands"
                    ).pack()
                )
                btn_back = InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=CallbackDatas.TestModule_MenuNavigation(
                        to="default"
                    ).pack()
                )
                rows = [[btn1], [btn_back]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
            
        class Commands:
            def text() -> str:
                msg = f"📖 <b>Инструкция {NAME}</b> → ⌨️ <b>Команды</b>" \
                    "\n" \
                    "\n→ <code>!некоторая-команда</code> — делает что-то непонятное" \
                    "\n" \
                    "\nВыберите действие ↓"
                return msg
            
            def kb() -> InlineKeyboardMarkup:
                btn_back = InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=CallbackDatas.TestModule_MenuNavigation(
                        to="instruction"
                    ).pack()
                )
                rows = [[btn_back]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup

    class SettingsNavigation:
        class Default:
            def text() -> str:
                msg = f"🔌 <b>Настройки модуля {NAME}</b>" \
                      f"\nПеремещайтесь по разделам ниже, чтобы изменить значения параметров ↓"
                return msg
            
            def kb() -> InlineKeyboardMarkup:
                btn1 = InlineKeyboardButton(
                    text="🌐 Какой-то раздел настройки",
                    callback_data=CallbackDatas.TestModule_SettingsNavigation(
                        to="some_section"
                    ).pack()
                )
                btn_back = InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=CallbackDatas.TestModule_MenuNavigation(
                        to="default"
                    ).pack()
                )
                rows = [[btn1], [btn_back]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
            
        class SomeSection:
            class Error:
                def text() -> str:
                    msg = f"🔌 <b>Настройки модуля {NAME}</b> → 🌐 <b>Какой-то раздел настройки</b>"\
                            f"\n" \
                            f"\n→ bool значение: <i>не удалось загрузить</i>" \
                            f"\n→ int значение: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"🔌 <b>Настройки модуля {NAME}</b> → 🌐 <b>Какой-то раздел настройки</b>"\
                            f"\n" \
                            f"\n→ bool значение: <i>загрузка</i>" \
                            f"\n→ int значение: <i>загрузка</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg

            class Default:
                def text() -> str:
                    config = Config().get()
                    bool_enabled = "🟢 Включено" if config["some_bool_value"] else "🔴 Выключено"
                    msg = f"🔌 <b>Настройки модуля {NAME}</b> → 🌐 <b>Какой-то раздел настройки</b>"\
                            f"\n" \
                            f"\n→ bool значение: <code>{bool_enabled}</code>" \
                            f"\n→ int значение: <code>{config['some_first_int_value']}</code>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    rows = []
                    config = Config().get()
                    if config["some_bool_value"]:
                        btn_disable = InlineKeyboardButton(
                            text="🔴 ВЫКЛ bool значение",
                            callback_data="tm_disable_some_bool_value"
                        )
                        rows.append([btn_disable])
                    else:
                        btn_enable = InlineKeyboardButton(
                            text="🟢 ВКЛ bool значение",
                            callback_data="tm_enable_some_bool_value"
                        )
                        rows.append([btn_enable])
                    btn1 = InlineKeyboardButton(
                        text="✏️ int значение",
                        callback_data="tm_enter_some_first_int_value"
                    )
                    rows.append([btn1])
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.TestModule_SettingsNavigation(
                            to="some_section"
                        ).pack()
                    )
                    rows.append([btn_refresh])
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.TestModule_SettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    rows.append([btn_back])
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class EnterSomeFirstIntValue:
                def text() -> str:
                    config = Config().get()
                    msg = f"✏️ <b>Введите новое int значение ↓</b>" \
                          f"\nТекущее значение: <code>{config['some_first_int_value']}</code>"
                    return msg
                
            class SomeFirstIntValueChanged:
                def text(new) -> str:
                    msg = f"✅ <b>int значение</b> был успешно изменено на <code>{new}</code>" 
                    return msg