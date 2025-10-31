import math
import textwrap
from uuid import UUID
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.modules import Module, get_modules, get_module_by_uuid

from .. import callback_datas as calls


def modules_text():
    modules = get_modules()
    txt = textwrap.dedent(f"""
        🔌 <b>Модули</b>
        Всего <b>{len(modules)}</b> загруженных модулей

        Перемещайтесь по разделам ниже. Нажмите на название модуля, чтобы перейти в его управление ↓
    """)
    return txt


def modules_kb(page: int = 0):
    modules = get_modules()
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(modules) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for module in list(modules)[start_offset:end_offset]:
        rows.append([InlineKeyboardButton(text=module.meta.name, callback_data=calls.ModulePage(uuid=module.uuid).pack())])

    buttons_row = []
    if page > 0: btn_back = InlineKeyboardButton(text="←", callback_data=calls.ModulesPagination(page=page - 1).pack())
    else: btn_back = InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_back)

    buttons_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_module_page"))

    if page < total_pages - 1: btn_next = InlineKeyboardButton(text="→", callback_data=calls.ModulesPagination(page=page+1).pack())
    else: btn_next = InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_next)
    rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def module_page_text(module_uuid: UUID):
    module: Module = get_module_by_uuid(module_uuid)
    if not module: raise Exception("Не удалось найти модуль")
    txt = textwrap.dedent(f"""
        🔧 <b>Управление модулем</b>

        <b>Модуль</b> <code>{module.meta.name}</code>:          
        ┣ UUID: <b>{module.uuid}</b>
        ┣ Версия: <b>{module.meta.version}</b>
        ┣ Описание: <blockquote>{module.meta.description}</blockquote>
        ┣ Авторы: <b>{module.meta.authors}</b>
        ┗ Ссылки: <b>{module.meta.links}</b>

        🔌 <b>Состояние:</b> {'🟢 Включен' if module.enabled else '🔴 Выключен'}

        Выберите действие для управления ↓
    """)
    return txt


def module_page_kb(module_uuid: UUID, page: int = 0):
    module: Module = get_module_by_uuid(module_uuid)
    if not module: raise Exception("Не удалось найти модуль")
    rows = [
        [InlineKeyboardButton(text="🔴 Выключить" if module.enabled else "🟢 Включить", callback_data="switch_module_enabled")],
        [InlineKeyboardButton(text="♻️ Перезагрузить", callback_data="reload_module")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ModulesPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ModulePage(uuid=module_uuid).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def module_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        🔧 <b>Управление модулем</b>
        \n{placeholder}
    """)
    return txt