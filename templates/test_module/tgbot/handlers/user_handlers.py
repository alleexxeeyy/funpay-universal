from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from threading import Thread
import asyncio

from FunPayAPI import Runner, enums, Account

from tgbot.templates import user_templates as MainTemplates
from ..templates import user_templates as Templates
from ..states.states import *

from settings import Config as MainConfig
from ...settings import Config

router = Router()


# /---- Команды ----\

@router.message(Command('test_module'))
async def handler_testmodule(message: types.Message, state: FSMContext):
    """ Отрабатывает команду /test_module """
    try:
        await state.clear()
        main_config = MainConfig().get()
        if message.from_user.id != main_config["tg_admin_id"]:
            return
        await message.answer(text=Templates.Navigation.MenuNavigation.Default.text(), 
                             reply_markup=Templates.Navigation.MenuNavigation.Default.kb(),
                             parse_mode="HTML")
    except Exception as e:
        await message.answer(text=MainTemplates.System.Error.text(e), parse_mode="HTML")

# /---- Состояния ----\

@router.message(TestModule_SomeState.entering_some_first_int_value)
async def handler_entering_some_first_int_value(message: types.Message, state: FSMContext):
    """ Считывает введёный пользователем some_first_int_value и изменяет в конфиге """
    try: 
        await state.clear()
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text.strip()):
            return await message.answer(text=MainTemplates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        if int(message.text.strip()) <= 0:
            return await message.answer(text=MainTemplates.System.Error.text("Слишком низкое значение"), parse_mode="HTML")
        
        config = Config().get()
        config["some_first_int_value"] = int(message.text.strip())
        Config().update(config)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.SomeSection.SomeFirstIntValueChanged.text(int(message.text.strip())),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=MainTemplates.System.Error.text(e), parse_mode="HTML")