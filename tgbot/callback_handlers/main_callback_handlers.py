from aiogram import F, Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
import traceback

import tgbot.templates.user_templates as Templates
import tgbot.callback_datas.user_callback_datas as CallbackDatas
from tgbot.states.states import *

from fpbot.funpaybot import FunPayBot
from settings import Config, CustomCommands, AutoDeliveries
from core.modules_manager import enable_module, disable_module

router = Router()
funpaybot = FunPayBot()



@router.callback_query(F.data == "destroy")
async def callback_back(call: CallbackQuery, state: FSMContext):
    """ Отработка удаления сообщения """
    try:
        await call.message.delete()
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e),
                                  parse_mode="HTML")

@router.callback_query(CallbackDatas.MenuNavigation.filter())
async def callback_menu_navigation(callback: CallbackQuery, callback_data: CallbackDatas.MenuNavigation):
    """ Навигация в главном меню """
    to = callback_data.to
    try:
        if to == "default":
            try:
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Default.Loading.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Default.Default.kb(callback.message.bot.bots_manager),
                                                 parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Default.Default.text(callback.message.bot.bots_manager),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Default.Default.kb(callback.message.bot.bots_manager),
                                                 parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Default.Error.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Default.Default.kb(),
                                                 parse_mode="HTML")
                raise e
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
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.InstructionNavigation.filter())
async def callback_instruction_navgiation(callback: CallbackQuery, callback_data: CallbackDatas.InstructionNavigation, state: FSMContext):
    """ Навигация в инструкции """
    to = callback_data.to
    try:
        if to == "default":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.Default.kb(),
                                             parse_mode="HTML")
        if to == "commands":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.Commands.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.Commands.kb(),
                                             parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.SettingsNavigation.filter())
async def callback_settings_navigation(callback: CallbackQuery, callback_data: CallbackDatas.SettingsNavigation, state: FSMContext):
    """ Навигация в настройках """
    to = callback_data.to
    try:
        if to == "default":
            await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.SettingsNavigation.Default.kb(),
                                             parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.BotSettingsNavigation.filter())
async def callback_botsettings_navigation(callback: CallbackQuery, callback_data: CallbackDatas.BotSettingsNavigation):
    """ Навигация в настройках бота """
    to = callback_data.to
    try:
        
        if to == "default":
            try:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Default.Loading.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Default.Default.kb(),
                                                parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Default.Default.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Default.Default.kb(),
                                                parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Default.Error.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Default.Default.kb(),
                                                parse_mode="HTML")
                raise e
        if to == "connection":
            try:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Connection.Loading.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Connection.Default.kb(),
                                                parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Connection.Default.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Connection.Default.kb(),
                                                parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Connection.Error.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Connection.Default.kb(),
                                                parse_mode="HTML")
                raise e
        if to == "authorization":
            try:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.Loading.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.Default.kb(),
                                                parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.Default.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.Default.kb(),
                                                parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.Error.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.Default.kb(),
                                                parse_mode="HTML")
                raise e
        if to == "lots":
            try:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Lots.Loading.text(),
                                                    reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Lots.Default.kb(),
                                                    parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Lots.Default.text(),
                                                    reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Lots.Default.kb(),
                                                    parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Lots.Error.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Lots.Default.kb(),
                                                parse_mode="HTML")
                raise e
        if to == "other":
            try:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Other.Loading.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Other.Default.kb(),
                                                parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Other.Default.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Other.Default.kb(),
                                                parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Other.Error.text(),
                                                reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Other.Default.kb(),
                                                parse_mode="HTML")
                raise e
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "start_funpay_bot")
async def callback_start_funpay_bot(call: CallbackQuery):
    """ Запускает FunPay бота """
    try:
        await call.message.bot.bots_manager.start_funpay_bot()
        callback_data = CallbackDatas.MenuNavigation(to="default")
        return await callback_menu_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "stop_funpay_bot")
async def callback_stop_funpay_bot(call: CallbackQuery):
    """ Останавливает FunPay бота """
    try:
        await call.message.bot.bots_manager.stop_funpay_bot()
        callback_data = CallbackDatas.MenuNavigation(to="default")
        return await callback_menu_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_golden_key")
async def callback_enter_golden_key(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового golden_key """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_golden_key)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.EnterGoldenKey.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_user_agent")
async def callback_enter_user_agent(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового golden_key """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_user_agent)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.EnterUserAgent.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_funpayapi_timeout")
async def callback_enter_funpayapi_timeout(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового funpayapi_timeout """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_funpayapi_timeout)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.Connection.EnterFunpayApiTimeout.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_runner_requests_delay")
async def callback_enter_runner_requests_delay(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового enter_runner_requests_delay """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_runner_requests_delay)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.Connection.EnterRunnerRequestsDelay.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_auto_raising_lots")
async def callback_enable_auto_raising_lots(call: CallbackQuery):
    """ Включает автоматическое поднятие лотов """
    try:
        config = Config().get()
        config["auto_raising_lots_enabled"] = True
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="lots")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_auto_raising_lots")
async def callback_disable_auto_raising_lots(call: CallbackQuery):
    """ Выключает автоматическое поднятие лотов """
    try:
        config = Config().get()
        config["auto_raising_lots_enabled"] = False
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="lots")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_lots_saving_interval")
async def callback_enter_lots_saving_interval(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового интервал сохранения лотов """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_lots_saving_interval)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.Lots.EnterLotsSavingInterval.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_auto_reviews_replies")
async def callback_enable_auto_reviews_replies(call: CallbackQuery):
    """ Включает авто-ответы на отзывы """
    try:
        config = Config().get()
        config["auto_reviews_replies_enabled"] = True
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_auto_reviews_replies")
async def callback_disable_auto_reviews_replies(call: CallbackQuery):
    """ Выключает авто-ответы на отзывы """
    try:
        config = Config().get()
        config["auto_reviews_replies_enabled"] = False
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_first_message")
async def callback_disable_first_message(call: CallbackQuery):
    """ Выключает приветственное сообщение """
    try:
        config = Config().get()
        config["first_message_enabled"] = False
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_first_message")
async def callback_enable_first_message(call: CallbackQuery):
    """ Включает приветственное сообщение """
    try:
        config = Config().get()
        config["first_message_enabled"] = True
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_custom_commands")
async def callback_disable_custom_commands(call: CallbackQuery):
    """ Выключает пользовательские ответы """
    try:
        config = Config().get()
        config["custom_commands_enabled"] = False
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_custom_commands")
async def callback_enable_custom_commands(call: CallbackQuery):
    """ Включает пользовательские ответы """
    try:
        config = Config().get()
        config["custom_commands_enabled"] = True
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_auto_delivery")
async def callback_disable_auto_delivery(call: CallbackQuery):
    """ Выключает авто-выдачу """
    try:
        config = Config().get()
        config["auto_delivery_enabled"] = False
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_auto_delivery")
async def callback_enable_auto_delivery(call: CallbackQuery):
    """ Включает авто-выдачу """
    try:
        config = Config().get()
        config["auto_delivery_enabled"] = True
        Config().update(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.CustomCommandsPagination.filter())
async def callback_custom_commands_pagination(callback: CallbackQuery, callback_data: CallbackDatas.CustomCommandsPagination, state: FSMContext):
    """ Срабатывает при пагинации в пользовательских командах """
    page = callback_data.page
    await state.update_data(last_page=page)
    try:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Pagination.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Pagination.kb(page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.CustomCommandPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: CallbackDatas.CustomCommandPage, state: FSMContext):
    """ Срабатывает при переходе на страницу редактирования пользовательской команды """
    command = callback_data.command
    data = await state.get_data()
    await state.update_data(custom_command=command)
    last_page = data.get("last_page") if data.get("last_page") in data else 0
    try:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Page.Loading.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Page.Default.kb(command, last_page),
                                         parse_mode="HTML")
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Page.Default.text(command),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Page.Default.kb(command, last_page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Page.Error.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Page.Default.kb(command, last_page),
                                         parse_mode="HTML")
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_custom_commands_page")
async def callback_enter_custom_commands_page(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод страницы пользовательских команд """
    try:
        await state.set_state(CustomCommandsNavigationStates.entering_custom_commands_page)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.EnterCustomCommandsPage.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e),
                                  parse_mode="HTML")

@router.callback_query(F.data == "enter_custom_command")
async def callback_enter_custom_command(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод пользовательской команды """
    try:
        await state.set_state(CustomCommandPageNavigationStates.entering_custom_command)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.EnterCustomCommand.text(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "add_custom_command")
async def callback_add_custom_command(call: CallbackQuery, state: FSMContext):
    """ Добавляет пользовательскую команду """
    try:
        data = await state.get_data()
        custom_commands = CustomCommands().get()
        new_custom_command = data.get("new_custom_command")
        new_custom_command_answer = data.get("new_custom_command_answer")
        if not new_custom_command:
            raise Exception("Новая пользовательская команда не была найдена, повторите процесс с самого начала")
        if not new_custom_command_answer:
            raise Exception("Ответ на новую пользовательскую команду не был найден, повторите процесс с самого начала")
        
        custom_commands[new_custom_command] = []
        for line in new_custom_command_answer.splitlines():
            custom_commands[new_custom_command].append(line)
        CustomCommands().update(custom_commands)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.CustomCommandAdded.text(new_custom_command),
                                  parse_mode="HTML") 
        await state.clear()
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_new_custom_command_answer")
async def callback_enter_new_custom_command_answer(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового ответа на пользовательскую команду """
    try:
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await state.set_state(CustomCommandPageNavigationStates.entering_new_custom_command_answer)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.EnterNewCustomCommandAnswer.text(custom_command),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "confirm_deleting_custom_command")
async def callback_confirm_deleting_custom_command(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает подтверждения удаления пользовательской команды """
    try:
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.ConfirmDeletingCustomCommand.text(custom_command),
                                  reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.ConfirmDeletingCustomCommand.kb(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "delete_custom_command")
async def callback_delete_custom_command(call: CallbackQuery, state: FSMContext):
    """ Удаляет пользовательскую команду """
    try:
        data = await state.get_data()
        custom_commands = CustomCommands().get()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        del custom_commands[custom_command]
        CustomCommands().update(custom_commands)
        await call.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.CustomComandDeleted.text(custom_command),
                                     parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")


@router.callback_query(CallbackDatas.AutoDeliveriesPagination.filter())
async def callback_auto_delivery_pagination(callback: CallbackQuery, callback_data: CallbackDatas.AutoDeliveriesPagination, state: FSMContext):
    """ Срабатывает при пагинации в авто-выдаче """
    page = callback_data.page
    await state.update_data(last_page=page)
    try:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Pagination.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Pagination.kb(page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.AutoDeliveryPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: CallbackDatas.AutoDeliveryPage, state: FSMContext):
    """ Срабатывает при переходе на страницу редактирования авто-выдачи """
    lot_id = callback_data.lot_id
    data = await state.get_data()
    await state.update_data(auto_delivery_lot_id=lot_id)
    last_page = data.gat("last_page") if data.gat("last_page") else 0
    try:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Page.Loading.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Page.Default.kb(lot_id, last_page),
                                         parse_mode="HTML")
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Page.Default.text(lot_id),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Page.Default.kb(lot_id, last_page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Page.Error.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Page.Default.kb(lot_id, last_page),
                                         parse_mode="HTML")
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_auto_deliveries_page")
async def callback_enter_auto_deliveries_page(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод страницы авто-выдачи """
    try:
        await state.set_state(AutoDeliveriesNavigationStates.entering_custom_commands_page)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.EnterAutoDeliveryPage.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_auto_delivery_lot_id")
async def callback_enter_auto_delivery_lot_id(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод ID лота авто-выдачи """
    try:
        await state.set_state(AutoDeliveryPageNavigationStates.entering_auto_delivery_lot_id)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.EnterAutoDeliveryLotId.text(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "add_auto_delivery")
async def callback_add_auto_delivery(call: CallbackQuery, state: FSMContext):
    """ Добавляет авто-выдачу """
    try:
        data = await state.get_data()
        auto_deliveries = AutoDeliveries().get()
        auto_devliery_lot_id = data.get("auto_delivery_lot_id")
        auto_delivery_message = data.get("auto_delivery_message")
        if not auto_devliery_lot_id:
            raise Exception("ID лота доставки не была найден, повторите процесс с самого начала")
        if not auto_delivery_message:
            raise Exception("Сообщение после покупки авто-доставки не было найдено, повторите процесс с самого начала")
        
        auto_deliveries[str(auto_devliery_lot_id)] = []
        for line in auto_delivery_message.splitlines():
            auto_deliveries[str(auto_devliery_lot_id)].append(line)
        AutoDeliveries().update(auto_deliveries)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.AutoDeliveryAdded.text(auto_devliery_lot_id),
                                  parse_mode="HTML") 
        await state.clear()
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_new_auto_delivery_message")
async def callback_enter_new_auto_delivery_message(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового сообщения после покупки авто-выдачи """
    try:
        data = await state.get_data()
        auto_delivery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_delivery_lot_id:
            raise Exception("ID лота авто-накрутки не был найден, повторите процесс с самого начала")
        
        await state.set_state(AutoDeliveryPageNavigationStates.entering_new_auto_delivery_message)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.EnterNewAutoDeliveryMessage.text(auto_delivery_lot_id),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "confirm_deleting_auto_delivery")
async def callback_confirm_deleting_auto_delivery(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает подтверждения удаления авто-выдачи """
    try:
        data = await state.get_data()
        auto_delivery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_delivery_lot_id:
            raise Exception("ID лота авто-накрутки не был найден, повторите процесс с самого начала")
        
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.ConfirmDeletingAutoDelivery.text(auto_delivery_lot_id),
                                  reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.ConfirmDeletingAutoDelivery.kb(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "delete_auto_delivery")
async def callback_delete_auto_delivery(call: CallbackQuery, state: FSMContext):
    """ Удаляет пользовательскую команду """
    try:
        data = await state.get_data()
        auto_deliveries = AutoDeliveries().get()
        auto_devliery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_devliery_lot_id:
            raise Exception("ID лота доставки не была найден, повторите процесс с самого начала")
        
        del auto_deliveries[str(auto_devliery_lot_id)]
        AutoDeliveries().update(auto_deliveries)
        await call.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.AutoDeliveryDeleted.text(auto_devliery_lot_id),
                                     parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")


@router.callback_query(CallbackDatas.MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: CallbackDatas.MessagesPagination, state: FSMContext):
    """ Срабатывает при пагинации в сообщениях """
    page = callback_data.page
    await state.update_data(last_page=page)
    try:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Pagination.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Pagination.kb(page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
    
@router.callback_query(CallbackDatas.MessagePage.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: CallbackDatas.MessagePage, state: FSMContext):
    """ Срабатывает при переходе на страницу редактирования сообщения """
    message_id = callback_data.message_id
    data = await state.get_data()
    await state.update_data(message_id=message_id)
    last_page = data.get("last_page") if data.get("last_page") else 0
    try:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Page.Loading.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Page.Default.kb(message_id, last_page),
                                         parse_mode="HTML")
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Page.Default.text(message_id),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Page.Default.kb(message_id, last_page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Page.Error.text(),
                                         reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Page.Default.kb(message_id, last_page),
                                         parse_mode="HTML")
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.callback_query(F.data == "enter_messages_page")
async def callback_enter_messages_page(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод страницы сообщений """
    try:
        await state.set_state(MessagesNavigationStates.entering_messages_page)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.Messages.EnterMessagesPage.text(),
                                parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e),
                                  parse_mode="HTML")

@router.callback_query(F.data == "enter_message_text")
async def callback_enter_message_text(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового текста сообщения """
    try:
        data = await state.get_data()
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("ID сообщения не был найден, повторите процесс с самого начала")

        await state.set_state(MessagePageNavigationStates.entering_message_text)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.BotSettings.Messages.EnterMessageText.text(message_id),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")


# /---- Настройки -> Настройки лотов ----\

@router.callback_query(CallbackDatas.LotsSettingsNavigation.filter())
async def callback_lotssettings_navigation(callback: CallbackQuery, callback_data: CallbackDatas.LotsSettingsNavigation, state: FSMContext):
    """ Навигация в настройках бота """
    to = callback_data.to
    try:
        if to == "default":
            try:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.LotsSettings.Loading.text(),
                                                 reply_markup=Templates.Navigation.SettingsNavigation.LotsSettings.Default.kb(),
                                                 parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.LotsSettings.Default.text(),
                                                 reply_markup=Templates.Navigation.SettingsNavigation.LotsSettings.Default.kb(),
                                                 parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.LotsSettings.Error.text(),
                                                 reply_markup=Templates.Navigation.SettingsNavigation.LotsSettings.Default.kb(),
                                                 parse_mode="HTML")
                await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "confirm_activating_lots")
async def callback_confirm_activating_lots(call: CallbackQuery, state: FSMContext):
    """ Подтверждение активации всех лотов """
    try:
        await state.set_state(LotsSettingsNavigationStates.confirming_activating_lots)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.LotsSettings.ConfirmActivatingLots.text(),
                                  reply_markup=Templates.Navigation.SettingsNavigation.LotsSettings.ConfirmActivatingLots.kb(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
                                
@router.callback_query(F.data == "activate_lots")
async def callback_activate_lots(call: CallbackQuery, state: FSMContext):
    """ Активация всех лотов """
    try:
        await call.message.edit_text(text=Templates.Navigation.SettingsNavigation.LotsSettings.ActivatingLots.text(),
                                     parse_mode="HTML")
        funpaybot.activate_lots()
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.LotsSettings.LotsActivated.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "confirm_deactivating_lots")
async def callback_confirm_deactivating_lots(call: CallbackQuery, state: FSMContext):
    """ Подтверждение деактивации всех лотов """
    try:
        await state.set_state(LotsSettingsNavigationStates.confirming_deactivating_lots)
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.LotsSettings.ConfirmDeactivatingLots.text(),
                                reply_markup=Templates.Navigation.SettingsNavigation.LotsSettings.ConfirmDeactivatingLots.kb(),
                                parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "deactivate_lots")
async def callback_deactivate_lots(call: CallbackQuery, state: FSMContext):
    """ Деактивация всех лотов """
    try:
        await call.message.edit_text(text=Templates.Navigation.SettingsNavigation.LotsSettings.DeactivatingLots.text(),
                                    parse_mode="HTML")
        funpaybot.deactivate_lots()
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.LotsSettings.LotsDeactivated.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "save_lots")
async def callback_save_lots(call: CallbackQuery, state: FSMContext):
    """ Сохранение всех лотов """
    try:
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.LotsSettings.SavingLots.text(),
                                  parse_mode="HTML")
        funpaybot.save_lots()
        await call.message.answer(text=Templates.Navigation.SettingsNavigation.LotsSettings.LotsSaved.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        

@router.callback_query(CallbackDatas.ModulesPagination.filter())
async def callback_modules_pagination(callback: CallbackQuery, callback_data: CallbackDatas.ModulesPagination, state: FSMContext):
    """ Срабатывает при пагинации в модулях """
    page = callback_data.page
    await state.update_data(last_page=page)
    try:
        await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Modules.Pagination.text(),
                                         reply_markup=Templates.Navigation.MenuNavigation.Modules.Pagination.kb(page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.ModulePage.filter())
async def callback_module_page(callback: CallbackQuery, callback_data: CallbackDatas.ModulePage, state: FSMContext):
    """ Срабатывает при переходе на страницу управления модулем """
    module_uuid = callback_data.uuid
    data = await state.get_data()
    await state.update_data(module_uuid=module_uuid)
    last_page = data.get("last_page") if data.get("last_page") else 0
    try:
        await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Modules.Page.Loading.text(),
                                         reply_markup=Templates.Navigation.MenuNavigation.Modules.Page.Default.kb(module_uuid, last_page),
                                         parse_mode="HTML")
        await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Modules.Page.Default.text(module_uuid),
                                         reply_markup=Templates.Navigation.MenuNavigation.Modules.Page.Default.kb(module_uuid, last_page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Modules.Page.Error.text(),
                                         reply_markup=Templates.Navigation.MenuNavigation.Modules.Page.Default.kb(module_uuid, last_page),
                                         parse_mode="HTML")
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_module")
async def callback_disable_module(call: CallbackQuery, state: FSMContext):
    """ Выключение модуля """
    try:
        data = await state.get_data()
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("UUID модуля не был найден, повторите процесс с самого начала")
        if not disable_module(module_uuid):
            raise Exception("Не удалось отключить модуль, попробуйте позже (см. консоль на наличие ошибки)")
        
        callback_data = CallbackDatas.ModulePage(uuid=module_uuid)
        return await callback_module_page(call, callback_data, state)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_module")
async def callback_enable_module(call: CallbackQuery, state: FSMContext):
    """ Включение модуля """
    try:
        data = await state.get_data()
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("UUID модуля не был найден, повторите процесс с самого начала")
        if not enable_module(module_uuid):
            raise Exception("Не удалось включить модуль, попробуйте позже (см. консоль на наличие ошибки)")
        
        callback_data = CallbackDatas.ModulePage(uuid=module_uuid)
        return await callback_module_page(call, callback_data, state)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")