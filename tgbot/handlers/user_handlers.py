from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import tgbot.templates.user_templates as Templates
from tgbot.states.states import *

from settings import Config, Messages, CustomCommands, AutoDeliveries

router = Router()


# /---- Команды ----\

@router.message(Command('start'))
async def handler_start(message: types.Message, state: FSMContext):
    """ Отрабатывает команду /start """
    try:
        await state.clear()
        config = Config().get()
        if message.from_user.id != config["tg_admin_id"]:
            return
        await message.answer(text=Templates.Navigation.MenuNavigation.Default.Default.text(message.bot.bots_manager), 
                                reply_markup=Templates.Navigation.MenuNavigation.Default.Default.kb(message.bot.bots_manager),
                                parse_mode="HTML")
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(Command('stats'))
async def handler_stats(message: types.Message, state: FSMContext):
    """ Отрабатывает команду /stats """
    try:
        await state.clear()
        config = Config().get()
        if message.from_user.id != config["tg_admin_id"]:
            return
        await message.answer(text=Templates.Navigation.MenuNavigation.Stats.Default.text(),
                                reply_markup=Templates.Navigation.MenuNavigation.Stats.Default.kb(),
                                parse_mode="HTML")
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(Command('settings'))
async def handler_stats(message: types.Message, state: FSMContext):
    """ Отрабатывает команду /settings """
    try:
        await state.clear()
        config = Config().get()
        if message.from_user.id != config["tg_admin_id"]:
            return
        await message.answer(text=Templates.Navigation.SettingsNavigation.Default.text(), 
                                reply_markup=Templates.Navigation.SettingsNavigation.Default.kb(),
                                parse_mode="HTML")
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

# /---- Настройки бота ----\

@router.message(MessagesNavigationStates.entering_messages_page)
async def handler_entering_messages_page(message: types.Message, state: FSMContext):
    """ Считывает введёный пользователем номер страницы сообщений и переходит на неё """
    try: 
        await state.clear()
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Pagination.text(),
            reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.Messages.Pagination.kb(page=int(message.text)-1),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(MessagePageNavigationStates.entering_message_text)
async def handler_entering_message_text(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем новый текст сообщения и изменяет его в сообщениях """ 
    try:
        await state.clear()
        await state.clear()
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий текст"), parse_mode="HTML")

        data = await state.get_data()
        messages = Messages().get()
        messages[data["message_id"]] = []
        message_split_lines = message.text.strip().split('\n')
        for line in message_split_lines:
            messages[data["message_id"]].append(line)
        Messages().update(messages)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.Messages.MessageTextChanged.text(message.text.strip(), data["message_id"]),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_golden_key)
async def handler_entering_golden_key(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем golden_key и изменяет его в конфиге """ 
    try:
        await state.clear()
        if len(message.text.strip()) <= 3 or len(message.text.strip()) >= 50:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий или длинный golden_key"), parse_mode="HTML")

        config = Config().get()
        config["golden_key"] = message.text.strip()
        Config().update(config)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.GoldenKeyChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_user_agent)
async def handler_entering_user_agent(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем user_agent и изменяет его в конфиге """ 
    try:
        await state.clear()
        if len(message.text.strip()) <= 3:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий user_agent"), parse_mode="HTML")

        config = Config().get()
        config["user_agent"] = message.text.strip()
        Config().update(config)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.Authorization.UserAgentChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_funpayapi_timeout)
async def handler_entering_funpayapi_timeout(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем funpayapi_timeout и изменяет его в конфиге """ 
    try:
        await state.clear()
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text.strip()):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        if int(message.text.strip()) < 0:
            return await message.answer(text=Templates.System.Error.text("Слишком низкое значение"), parse_mode="HTML")

        config = Config().get()
        config["funpayapi_timeout"] = int(message.text.strip())
        Config().update(config)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.Connection.FunpayApiTimeoutChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_runner_requests_delay)
async def handler_entering_runner_requests_delay(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем runner_requests_delay и изменяет его в конфиге """ 
    try:
        await state.clear()
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text.strip()):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        if int(message.text.strip()) < 0:
            return await message.answer(text=Templates.System.Error.text("Слишком низкое значение"), parse_mode="HTML")

        config = Config().get()
        config["runner_requests_delay"] = int(message.text.strip())
        Config().update(config)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.Connection.RunnerRequestsDelayChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_lots_saving_interval)
async def handler_entering_lots_saving_interval(message: types.Message, state: FSMContext):
    """ Считывает введёный интервал сохранения лотов и изменяет его в конфиге """ 
    try:
        await state.clear()
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text.strip()):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")

        if int(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком низкий интервал"), parse_mode="HTML")

        config = Config().get()
        config["lots_saving_interval"] = int(message.text.strip())
        Config().update(config)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.Lots.LotsSavingIntervalChanged.text(message.text),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")


@router.message(CustomCommandsNavigationStates.entering_custom_commands_page)
async def handler_entering_custom_commands_page(message: types.Message, state: FSMContext):
    """ Считывает введёный пользователем номер страницы пользовательских комманд и переходит на неё """
    try: 
        await state.clear()
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Pagination.text(),
            reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.Pagination.kb(page=int(message.text)-1),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(CustomCommandPageNavigationStates.entering_custom_command)
async def handler_entering_custom_command(message: types.Message, state: FSMContext):
    """ Считывает введённую пользователем пользовательскую команду и запоминает """ 
    try:
        await state.clear()
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 32:
            return await message.answer(text=Templates.System.Error.text("Слишком короткая или длинная команда"), parse_mode="HTML")

        await state.update_data(new_custom_command=message.text.strip())
        await state.set_state(CustomCommandPageNavigationStates.entering_custom_command_answer)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.EnterCustomCommandAnswer.text(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(CustomCommandPageNavigationStates.entering_custom_command_answer)
async def handler_entering_custom_command_answer(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем ответ на пользовательскую команду и запоминает """ 
    try:
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий ответ"), parse_mode="HTML")

        await state.update_data(new_custom_command_answer=message.text.strip())
        data = await state.get_data()
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.ConfirmAddingCustomCommand.text(data["new_custom_command"], data["new_custom_command_answer"]),
            reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.ConfirmAddingCustomCommand.kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(CustomCommandPageNavigationStates.entering_new_custom_command_answer)
async def handler_entering_new_custom_command_answer(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем новый текст ответа на пользовательскую команду и изменяет его в конфиге """ 
    try:
        await state.clear()
        data = await state.get_data()
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий текст"), parse_mode="HTML")

        custom_commands = CustomCommands().get()
        custom_commands[data["custom_command"]] = []
        answer_split_lines = message.text.strip().split('\n')
        for line in answer_split_lines:
            custom_commands[data["custom_command"]].append(line)
        CustomCommands().update(custom_commands)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.CustomCommands.CustomCommandAnswerChanged.text(message.text.strip(), data["custom_command"]),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")


@router.message(AutoDeliveriesNavigationStates.entering_custom_commands_page)
async def handler_entering_custom_commands_page(message: types.Message, state: FSMContext):
    """ Считывает введёный пользователем номер страницы авто-выдач и переходит на неё """
    try: 
        await state.clear()
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Pagination.text(),
            reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.Pagination.kb(page=int(message.text)-1),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(AutoDeliveryPageNavigationStates.entering_auto_delivery_lot_id)
async def handler_entering_auto_delivery_lot_id(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем ID лота выто-выдачи и запоминает """ 
    try:
        await state.clear()
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 100:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий или длинный ID лота"), parse_mode="HTML")

        await state.update_data(auto_delivery_lot_id=int(message.text.strip()))
        await state.set_state(AutoDeliveryPageNavigationStates.entering_auto_delivery_message)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.EnterAutoDeliveryMessage.text(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(AutoDeliveryPageNavigationStates.entering_auto_delivery_message)
async def handler_entering_auto_delivery_message(message: types.Message, state: FSMContext):
    """ Считывает введённое пользователем сообщение после покупки на авто-выдачу и запоминает """ 
    try:
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий ответ"), parse_mode="HTML")

        await state.update_data(auto_delivery_message=message.text.strip())
        data = await state.get_data()
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.ConfirmAddingAutoDelivery.text(data["auto_delivery_lot_id"], data["auto_delivery_message"]),
            reply_markup=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.ConfirmAddingAutoDelivery.kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(AutoDeliveryPageNavigationStates.entering_new_auto_delivery_message)
async def handler_entering_new_auto_delivery_message(message: types.Message, state: FSMContext):
    """ Считывает введённое пользователем новое сообщение после покупки на авто-выдачу и изменяет его в конфиге """ 
    try:
        data = await state.get_data()
        await state.clear()
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий текст"), parse_mode="HTML")

        auto_deliveries = AutoDeliveries().get()
        auto_deliveries[data["auto_delivery_lot_id"]] = []
        answer_split_lines = message.text.strip().split('\n')
        for line in answer_split_lines:
            auto_deliveries[data["auto_delivery_lot_id"]].append(line)
        AutoDeliveries().update(auto_deliveries)
        await message.answer(
            text=Templates.Navigation.SettingsNavigation.BotSettings.AutoDeliveries.AutoDeliveryMessageChanged.text(message.text.strip(), data["auto_delivery_lot_id"]),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")