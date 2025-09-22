from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from settings import Settings as sett
from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states

from ..helpful import throw_float_message
from .navigation import *

router = Router()



@router.callback_query(F.data == "destroy")
async def callback_back(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(F.data == "confirm_creating_support_tickets")
async def callback_confirm_creating_support_tickets(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.events_float_text(f"📞✔️ Подтвердите <b>создание тикетов на закрытие заказов</b> ↓"), 
                              reply_markup=templ.confirm_kb(confirm_cb="create_support_tickets", cancel_cb=calls.MenuNavigation(to="events").pack()))

@router.callback_query(F.data == "create_support_tickets")
async def callback_create_support_tickets(callback: CallbackQuery, state: FSMContext):
    try:
        from fpbot import get_funpay_bot
        await state.set_state(None)
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.events_float_text(f"📞 Идёт <b>создание тикетов на закрытие заказов</b>, ожидайте (см. консоль)..."), 
                                  reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack()))
        fpbot = get_funpay_bot()
        fpbot.create_support_tickets()
        await throw_float_message(state=state, 
                                message=callback.message, 
                                text=templ.events_float_text(f"📞✅ <b>Тикеты на закрытие заказов</b> были созданы"), 
                                reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.events_float_text(e), 
                                      reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack()))


@router.callback_query(F.data == "enter_golden_key")
async def callback_enter_golden_key(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_golden_key)
    config = sett.get("config")
    golden_key = config["funpay"]["api"]["golden_key"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_auth_float_text(f"🔑 Введите новый <b>golden_key</b> вашего аккаунта ↓\n┗ Текущее: <code>{golden_key}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack()))

@router.callback_query(F.data == "enter_user_agent")
async def callback_enter_user_agent(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_user_agent)
    config = sett.get("config")
    user_agent = config["funpay"]["api"]["user_agent"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_auth_float_text(f"🎩 Введите новый <b>user_agent</b> вашего браузера ↓\n┗ Текущее: <code>{user_agent}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack()))


@router.callback_query(F.data == "remove_proxy")
async def callback_remove_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    proxy = config["funpay"]["api"]["proxy"] = ""
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="conn"), state)

@router.callback_query(F.data == "enter_proxy")
async def callback_enter_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_proxy)
    config = sett.get("config")
    proxy = config["funpay"]["api"]["proxy"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_conn_float_text(f"🌐 Введите новый <b>прокси-сервер</b> (формат: user:pass@ip:port или ip:port) ↓\n┗ Текущее: <code>{proxy}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))

@router.callback_query(F.data == "enter_funpayapi_requests_timeout")
async def callback_enter_funpayapi_requests_timeout(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_requests_timeout)
    config = sett.get("config")
    requests_timeout = config["funpay"]["api"]["requests_timeout"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_conn_float_text(f"🛜 Введите новый <b>таймаут подключения</b> (в секундах) ↓\n┗ Текущее: <code>{requests_timeout}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))

@router.callback_query(F.data == "enter_funpayapi_runner_requests_delay")
async def callback_enter_funpayapi_runner_requests_delay(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_runner_requests_delay)
    config = sett.get("config")
    requests_timeout = config["funpay"]["api"]["runner_requests_delay"] or "❌ Не задано"
    await throw_float_message(state=state, 
                                message=callback.message, 
                                text=templ.settings_conn_float_text(f"⏱️ Введите новую <b>периодичность запросов</b> (в секундах) ↓\n┗ Текущее: <code>{requests_timeout}</code>"), 
                                reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))


@router.callback_query(F.data == "switch_auto_raising_lots_enabled")
async def callback_switch_auto_raising_lots_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["auto_raising_lots_enabled"] = False if config["funpay"]["bot"]["auto_raising_lots_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="lots"), state)

@router.callback_query(F.data == "switch_auto_reviews_replies_enabled")
async def callback_switch_auto_reviews_replies_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["auto_reviews_replies_enabled"] = False if config["funpay"]["bot"]["auto_reviews_replies_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "switch_first_message_enabled")
async def callback_switch_first_message_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["first_message_enabled"] = False if config["funpay"]["bot"]["first_message_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "switch_custom_commands_enabled")
async def callback_switch_custom_commands_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["custom_commands_enabled"] = False if config["funpay"]["bot"]["custom_commands_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "switch_auto_deliveries_enabled")
async def callback_switch_auto_deliveries_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["auto_deliveries_enabled"] = False if config["funpay"]["bot"]["auto_deliveries_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "switch_messages_watermark_enabled")
async def callback_switch_messages_watermark_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["messages_watermark_enabled"] = False if config["funpay"]["bot"]["messages_watermark_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "enter_messages_watermark")
async def callback_enter_messages_watermark(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_messages_watermark)
    config = sett.get("config")
    messages_watermark = config["funpay"]["bot"]["messages_watermark"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_other_float_text(f"✍️©️ Введите новый <b>водяной знак</b> под сообщениями ↓\n┗ Текущее: <code>{messages_watermark}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack()))
    


@router.callback_query(F.data == "enter_custom_commands_page")
async def callback_enter_custom_commands_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.CustomCommandsStates.entering_page)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_comm_float_text(f"📃 Введите номер страницы для перехода ↓"), 
                              reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_new_custom_command")
async def callback_enter_new_custom_command(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.CustomCommandsStates.entering_new_custom_command)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_new_comm_float_text(f"⌨️ Введите <b>новую команду</b> (например, <code>!тест</code>) ↓"), 
                              reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "add_new_custom_command")
async def callback_add_new_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        custom_commands = sett.get("custom_commands")
        new_custom_command = data.get("new_custom_command")
        new_custom_command_answer = data.get("new_custom_command_answer")
        if not new_custom_command:
            raise Exception("❌ Новая пользовательская команда не была найдена, повторите процесс с самого начала")
        if not new_custom_command_answer:
            raise Exception("❌ Ответ на новую пользовательскую команду не был найден, повторите процесс с самого начала")

        custom_commands[new_custom_command] = new_custom_command_answer.splitlines()
        sett.set("custom_commands", custom_commands)
        last_page = data.get("last_page") or 0
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_comm_float_text(f"✅ <b>Пользовательская команда</b> <code>{new_custom_command}</code> была добавлена"), 
                                  reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_comm_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_custom_command_answer")
async def callback_enter_custom_command_answer(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        custom_commands = sett.get("custom_commands")
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await state.set_state(states.CustomCommandPageStates.entering_custom_command_answer)
        custom_command_answer = "\n".join(custom_commands[custom_command]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_comm_page_float_text(f"💬 Введите новый <b>текст ответа</b> команды <code>{custom_command}</code> ↓\n┗ Текущее: <blockquote>{custom_command_answer}</blockquote>"), 
                                  reply_markup=templ.back_kb(calls.CustomCommandPage(command=custom_command).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_comm_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "confirm_deleting_custom_command")
async def callback_confirm_deleting_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_comm_page_float_text(f"🗑️ Подтвердите <b>удаление пользовательской команды</b> <code>{custom_command}</code>"), 
                                  reply_markup=templ.confirm_kb(confirm_cb="delete_custom_command", cancel_cb=calls.CustomCommandPage(command=custom_command).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_comm_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "delete_custom_command")
async def callback_delete_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        custom_commands = sett.get("custom_commands")
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        del custom_commands[custom_command]
        sett.set("custom_commands", custom_commands)
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_comm_page_float_text(f"✅ <b>Пользовательская команда</b> <code>{custom_command}</code> была удалена"), 
                                  reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_comm_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))


@router.callback_query(F.data == "enter_auto_deliveries_page")
async def callback_enter_auto_deliveries_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.AutoDeliveriesStates.entering_page)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_deliv_float_text(f"📃 Введите номер страницы для перехода ↓"), 
                              reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_new_auto_delivery_lot_id")
async def callback_enter_new_auto_delivery_lot_id(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.AutoDeliveriesStates.entering_new_auto_delivery_lot_id)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_new_deliv_float_text(f"🆔 Введите <b>ID лота</b>, на который нужно добавить авто-выдачу ↓"), 
                              reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "add_new_auto_delivery")
async def callback_add_new_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        auto_deliveries = sett.get("auto_deliveries")
        new_auto_delivery_lot_id = data.get("new_auto_delivery_lot_id")
        new_auto_delivery_message = data.get("new_auto_delivery_message")
        if not new_auto_delivery_lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        if not new_auto_delivery_message:
            raise Exception("❌ Сообщение авто-выдачи не было найдено, повторите процесс с самого начала")
        
        auto_deliveries[str(new_auto_delivery_lot_id)] = new_auto_delivery_message.splitlines()
        sett.set("auto_deliveries", auto_deliveries)
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_deliv_float_text(f"✅ <b>Авто-выдача</b> на лот <code>{new_auto_delivery_lot_id}</code> была добавлена"), 
                                  reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_deliv_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_auto_delivery_message")
async def callback_enter_auto_delivery_message(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_delivery_lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        
        await state.set_state(states.AutoDeliveryPageStates.entering_auto_delivery_message)
        auto_delivery_message = "\n".join(auto_deliveries[str(auto_delivery_lot_id)]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_deliv_page_float_text(f"💬 Введите новое <b>сообщение после покупки</b> лота <code>{auto_delivery_lot_id}</code>\n┗ Текущее: <blockquote>{auto_delivery_message}</blockquote>"), 
                                  reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=auto_delivery_lot_id).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "confirm_deleting_auto_delivery")
async def callback_confirm_deleting_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_delivery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_delivery_lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_deliv_page_float_text(f"🗑️ Подтвердите <b>удаление пользовательской авто-выдачи</b> на лот <code>{auto_delivery_lot_id}</code>"), 
                                  reply_markup=templ.confirm_kb(confirm_cb="delete_auto_delivery", cancel_cb=calls.AutoDeliveryPage(lot_id=auto_delivery_lot_id).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "delete_auto_delivery")
async def callback_delete_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        auto_deliveries = sett.get("auto_deliveries")
        auto_devliery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_devliery_lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        
        del auto_deliveries[str(auto_devliery_lot_id)]
        sett.set("auto_deliveries", auto_deliveries)
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_deliv_page_float_text(f"✅ <b>Авто-выдача</b> на лот <code>{auto_devliery_lot_id}</code> была удалена"), 
                                  reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))


@router.callback_query(F.data == "enter_messages_page")
async def callback_enter_messages_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.MessagesStates.entering_page)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_mess_float_text(f"📃 Введите номер страницы для перехода ↓"), 
                              reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_message_text")
async def callback_enter_message_text(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        await state.set_state(states.MessagePageStates.entering_message_text)
        messages = sett.get("messages")
        mess_text = "\n".join(messages[message_id]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_mess_float_text(f"💬 Введите новый <b>текст сообщения</b> <code>{message_id}</code> ↓\n┗ Текущее: <blockquote>{mess_text}</blockquote>"), 
                                  reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_mess_float_text(e), 
                                      reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack()))


@router.callback_query(F.data == "switch_tg_logging_enabled")
async def callback_switch_tg_logging_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["tg_logging_enabled"] = not config["funpay"]["bot"]["tg_logging_enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "enter_tg_logging_chat_id")
async def callback_enter_tg_logging_chat_id(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_tg_logging_chat_id)
    config = sett.get("config")
    tg_logging_chat_id = config["funpay"]["bot"]["tg_logging_chat_id"] or "✔️ Ваш чат с ботом"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_logger_float_text(f"💬 Введите новый <b>ID чата для логов</b> (вы можете указать как цифровой ID, так и юзернейм чата) ↓\n┗ Текущее: <code>{tg_logging_chat_id}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack()))

@router.callback_query(F.data == "switch_tg_logging_event_new_user_message")
async def callback_switch_tg_logging_event_new_user_message(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["tg_logging_events"]["new_user_message"] = not config["funpay"]["bot"]["tg_logging_events"]["new_user_message"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_new_system_message")
async def callback_switch_tg_logging_event_new_system_message(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["tg_logging_events"]["new_system_message"] = not config["funpay"]["bot"]["tg_logging_events"]["new_system_message"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_new_order")
async def callback_switch_tg_logging_event_new_order(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["tg_logging_events"]["new_order"] = not config["funpay"]["bot"]["tg_logging_events"]["new_order"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_order_status_changed")
async def callback_switch_tg_logging_event_order_status_changed(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["tg_logging_events"]["order_status_changed"] = not config["funpay"]["bot"]["tg_logging_events"]["order_status_changed"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_new_review")
async def callback_switch_tg_logging_event_new_review(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["tg_logging_events"]["new_review"] = not config["funpay"]["bot"]["tg_logging_events"]["new_review"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "clean_tg_logging_chat_id")
async def callback_clean_tg_logging_chat_id(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["tg_logging_chat_id"] = ""
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_auto_support_tickets_enabled")
async def callback_switch_auto_support_tickets_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["bot"]["auto_support_tickets_enabled"] = False if config["funpay"]["bot"]["auto_support_tickets_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="tickets"), state)

@router.callback_query(F.data == "enter_auto_support_tickets_orders_per_ticket")
async def callback_enter_auto_support_tickets_orders_per_ticket(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_auto_support_tickets_orders_per_ticket)
    config = sett.get("config")
    auto_support_tickets_orders_per_ticket = config["funpay"]["bot"]["auto_support_tickets_orders_per_ticket"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_tickets_float_text(f"📋 Введите новое <b>кол-во заказов в одном тикете</b> ↓\n┗ Текущее: <code>{auto_support_tickets_orders_per_ticket}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack()))

@router.callback_query(F.data == "enter_auto_support_tickets_create_interval")
async def callback_enter_enter_auto_support_tickets_create_interval(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_auto_support_tickets_create_interval)
    config = sett.get("config")
    auto_support_tickets_create_interval = config["funpay"]["bot"]["auto_support_tickets_create_interval"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_tickets_float_text(f"⏱️ Введите новый <b>интервал создания тикетов</b> (в секундах) ↓\n┗ Текущее: <code>{auto_support_tickets_create_interval}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack()))


@router.callback_query(F.data == "switch_module_enabled")
async def callback_disable_module(callback: CallbackQuery, state: FSMContext):
    from core.modules_manager import ModulesManager as modman
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("❌ UUID модуля не был найден, повторите процесс с самого начала")

        module = modman.get_module_by_uuid(module_uuid)
        modman.disable_module(module_uuid) if module.enabled else modman.enable_module(module_uuid)
        return await callback_module_page(callback, calls.ModulePage(uuid=module_uuid), state)
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.module_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack()))