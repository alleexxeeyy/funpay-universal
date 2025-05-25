from aiogram import F, Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
import traceback

from tgbot.templates import user_templates as MainTemplates
from ..templates import user_templates as Templates
from ..callback_datas import user_callback_datas as CallbackDatas
from ..states.states import *

from fpbot.funpaybot import FunPayBot as MainFunPayBot

from ...settings import Config

router = Router()
main_funpaybot = MainFunPayBot()


@router.callback_query(CallbackDatas.TestModule_MenuNavigation.filter())
async def callback_menu_navigation(callback: CallbackQuery, callback_data: CallbackDatas.TestModule_MenuNavigation, state: FSMContext):
    """ Навигация в главном меню """
    to = callback_data.to
    try:
        if to == "default":
            await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.MenuNavigation.Default.kb(),
                                             parse_mode="HTML")
        elif to == "settings":
            await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.SettingsNavigation.Default.kb(),
                                             parse_mode="HTML")
        elif to == "stats":
            try:
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Stats.Loading.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Stats.Default.kb(),
                                                 parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Stats.Default.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Stats.Default.kb(),
                                                 parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Stats.Error.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Stats.Default.kb(),
                                                 parse_mode="HTML")
                raise e
        elif to == "instruction":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.Default.kb(),
                                             parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=MainTemplates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.TestModule_InstructionNavigation.filter())
async def callback_instruction_navgiation(callback: CallbackQuery, callback_data: CallbackDatas.TestModule_InstructionNavigation):
    """ Навигация в инструкции """
    to = callback_data.to
    try:
        if to == "default":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.Default.kb(),
                                             parse_mode="HTML")
        elif to == "commands":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.Commands.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.Commands.kb(),
                                             parse_mode="HTML")
        elif to == "smm_lots":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.SmmLots.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.SmmLots.kb(),
                                             parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=MainTemplates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.TestModule_SettingsNavigation.filter())
async def callback_settings_navigation(callback: CallbackQuery, callback_data: CallbackDatas.TestModule_SettingsNavigation):
    """ Навигация в настройках """
    to = callback_data.to
    try:
        if to == "default":
            await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.SettingsNavigation.Default.kb(),
                                             parse_mode="HTML")
        if to == "some_section":
            try:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.SomeSection.Loading.text(),
                                                 reply_markup=Templates.Navigation.SettingsNavigation.SomeSection.Default.kb(),
                                                 parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.SomeSection.Default.text(),
                                                 reply_markup=Templates.Navigation.SettingsNavigation.SomeSection.Default.kb(),
                                                 parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.SomeSection.Error.text(),
                                                 reply_markup=Templates.Navigation.SettingsNavigation.SomeSection.Default.kb(),
                                                 parse_mode="HTML")
                raise e
        # elif to == "notifications": ....
    except Exception as e:
        await callback.message.answer(text=MainTemplates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "tm_disable_some_bool_value")
async def callback_tm_disable_some_bool_value(call: CallbackQuery, state: FSMContext):
    try:
        config = Config().get()
        config["some_bool_value"] = False
        Config().update(config)
        call_data = CallbackDatas.TestModule_SettingsNavigation(to="some_section")
        await callback_settings_navigation(call, call_data)
    except Exception as e:
        await call.message.answer(text=MainTemplates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "tm_enable_some_bool_value")
async def callback_tm_enable_some_bool_value(call: CallbackQuery, state: FSMContext):
    try:
        config = Config().get()
        config["some_bool_value"] = True
        Config().update(config)
        call_data = CallbackDatas.TestModule_SettingsNavigation(to="some_section")
        await callback_settings_navigation(call, call_data)
    except Exception as e:
        await call.message.answer(text=MainTemplates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "tm_enter_some_first_int_value")
async def callback_tm_enable_some_bool_value(call: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(TestModule_SomeState.entering_some_first_int_value)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.SomeSection.EnterSomeFirstIntValue.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=MainTemplates.System.Error.text(e), parse_mode="HTML")