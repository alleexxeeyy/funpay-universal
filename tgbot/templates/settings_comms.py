import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_comms_text():
    custom_commands = sett.get("custom_commands")
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ⌨️ <b>Пользовательские команды</b>
        Всего <b>{len(custom_commands.keys())}</b> пользовательских команд в конфиге

        Перемещайтесь по разделам ниже. Нажмите на команду, чтобы перейти в её редактирование ↓
    """)
    return txt


def settings_comms_kb(page: int = 0):
    custom_commands = sett.get("custom_commands")
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(custom_commands.keys())/items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages-1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for command in list(custom_commands.keys())[start_offset:end_offset]:
        command_text = "\n".join(custom_commands[command])
        rows.append([InlineKeyboardButton(text=f'{command} → {command_text}', callback_data=calls.CustomCommandPage(command=command).pack())])
        
    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.CustomCustomCommandsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑",callback_data="123")
        buttons_row.append(btn_back)
    
        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}",callback_data="enter_custom_commands_page")
        buttons_row.append(btn_pages)
        
        btn_next = InlineKeyboardButton(text="→", callback_data=calls.CustomCustomCommandsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        
        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="➕⌨️ Добавить",callback_data="enter_new_custom_command")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.CustomCommandsPagination(page=page).pack())
        ])
    
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_comms_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ⌨️ <b>Пользовательские команды</b>
        \n{placeholder}
    """)
    return txt


def settings_new_comm_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Добавление пользовательской команды</b>
        \n{placeholder}
    """)
    return txt


def settings_comm_page_text(command: str):
    custom_commands = sett.get("custom_commands")
    command_text = "\n".join(custom_commands[command]) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование пользовательской команды</b>

        ⌨️ <b>Команда:</b> {command}
        💬 <b>Ответ:</b> 
        <blockquote>{command_text}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt


def settings_comm_page_kb(command: str, page: int = 0):
    custom_commands = sett.get("custom_commands")
    command_text = "\n".join(custom_commands[command]) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"✍️ Ответ: {command_text}", callback_data="enter_custom_command_answer")],
        [InlineKeyboardButton(text="🗑️ Удалить команду", callback_data="confirm_deleting_custom_command")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.CustomCommandsPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.CustomCommandPage(command=command).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_comm_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование пользовательской команды</b>
        \n{placeholder}
    """)
    return txt