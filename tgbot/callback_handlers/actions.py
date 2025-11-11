from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from settings import Settings as sett

from .navigation import *
from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message


router = Router()


@router.callback_query(F.data == "destroy")
async def callback_back(callback: CallbackQuery):
    await callback.message.delete()


# --- Действия с классами CallbackData  ---

@router.callback_query(calls.RememberChatName.filter())
async def callback_remember_chat_name(callback: CallbackQuery, callback_data: calls.RememberChatName, state: FSMContext):
    await state.set_state(None)
    chat_name = callback_data.name
    do = callback_data.do
    await state.update_data(chat_name=chat_name)
    if do == "send_mess":
        await state.set_state(states.ActionsStates.waiting_for_message_text)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.do_action_text(
                "💬 Введите <b>сообщение</b> для отправки <b>{chat_name}</b> ↓"
            ), 
            reply_markup=templ.destroy_kb(),
            callback=callback,
            send=True
        )

@router.callback_query(calls.RememberOrderId.filter())
async def callback_remember_order_id(callback: CallbackQuery, callback_data: calls.RememberOrderId, state: FSMContext):
    await state.set_state(None)
    order_id = callback_data.or_id
    do = callback_data.do
    await state.update_data(order_id=order_id)
    if do == "refund":
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.do_action_text(
                "📦✔️ Подтвердите <b>возврат</b> заказа <b>#{order_id}</b> ↓"
            ), 
            reply_markup=templ.confirm_kb(confirm_cb="refund_order", cancel_cb="destroy"),
            callback=callback,
            send=True
        )
    elif do == "answer_rev":
        await state.set_state(states.ActionsStates.waiting_for_review_answer_text)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.do_action_text(
                "💬🌟 Введите <b>ответ</b> на отзыв по заказу <b>#{order_id}</b> ↓"
            ), 
            reply_markup=templ.destroy_kb(),
            callback=callback,
            send=True
        )


# --- Действия с классом FunPayBot  ---

@router.callback_query(F.data == "refund_order")
async def callback_refund_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    from fpbot.funpaybot import get_funpay_bot
    data = await state.get_data()
    order_id = data.get("order_id")
    get_funpay_bot().funpay_account.refund(order_id)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.do_action_text(
            "✅ По заказу <code>#{order_id}</code> был оформлен возврат"
        ), 
        reply_markup=templ.destroy_kb()
    )


@router.callback_query(F.data == "create_tickets")
async def callback_create_tickets(callback: CallbackQuery, state: FSMContext):
    try:
        from fpbot.funpaybot import get_funpay_bot
        await state.set_state(None)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.events_float_text(
                "📞 Идёт <b>создание тикетов на закрытие заказов</b>, ожидайте (см. консоль)..."
            ),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )
        get_funpay_bot().create_tickets()
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.events_float_text(
                "📞✅ <b>Тикеты на закрытие заказов</b> были созданы"
            ), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.events_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )


# --- Очистка данных в конфиге  ---

@router.callback_query(F.data.regexp(r"^clean_.*\|.*"))
async def callback_switch(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    to = callback.data.split("|")[0].split("_")[1]
    params = callback.data.split("|")[1:]

    field_to_toggle = params[-1]
    config_path = params[:-1]
    current_level = config["funpay"]
    for key in config_path[:-1]:
        current_level = current_level[key]

    last_key = config_path[-1]
    if isinstance(current_level[last_key][field_to_toggle], str): clean_value = ""
    elif isinstance(current_level[last_key][field_to_toggle], int): clean_value = 0
    elif isinstance(current_level[last_key][field_to_toggle], list): clean_value = []
    elif isinstance(current_level[last_key][field_to_toggle], dict): clean_value = {}
    current_level[last_key][field_to_toggle] = clean_value
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to=to), state)


# --- Переключение данных в конфиге ---

@router.callback_query(F.data.regexp(r"^switch_.*\|.*"))
async def callback_switch(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    to = callback.data.split("|")[0].split("_")[1]
    params = callback.data.split("|")[1:]

    field_to_toggle = params[-1]
    config_path = params[:-1]
    current_level = config["funpay"]
    for key in config_path[:-1]:
        current_level = current_level[key]

    last_key = config_path[-1]
    current_level[last_key][field_to_toggle] = not current_level[last_key][field_to_toggle]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to=to), state)


@router.callback_query(F.data == "switch_message_enabled")
async def callback_switch_message_enabled(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        messages = sett.get("messages")
        messages[message_id]["enabled"] = not messages[message_id]["enabled"]
        sett.set("messages", messages)
        return await callback_message_page(callback, calls.MessagePage(message_id=message_id), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_mess_float_text(e), 
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "switch_module_enabled")
async def callback_switch_module_enabled(callback: CallbackQuery, state: FSMContext):
    from core.modules import get_module_by_uuid, disable_module, enable_module
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("❌ UUID модуля не был найден, повторите процесс с самого начала")
        module = get_module_by_uuid(module_uuid)
        if not module:
            raise Exception("❌ Модуль с этим UUID не был найден, повторите процесс с самого начала")

        await disable_module(module_uuid) if module.enabled else await enable_module(module_uuid)
        return await callback_module_page(callback, calls.ModulePage(uuid=module_uuid), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.module_page_float_text(e), 
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )


# --- Ввод значений ---

@router.callback_query(F.data == "enter_golden_key")
async def callback_enter_golden_key(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_golden_key)
    config = sett.get("config")
    golden_key = config["funpay"]["api"]["golden_key"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_auth_float_text(
            "🔑 Введите новый <b>golden_key</b> вашего аккаунта ↓"
            f"\n┗ Текущее: <code>{golden_key}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
    )


@router.callback_query(F.data == "enter_user_agent")
async def callback_enter_user_agent(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_user_agent)
    config = sett.get("config")
    user_agent = config["funpay"]["api"]["user_agent"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_auth_float_text(
            "🎩 Введите новый <b>user_agent</b> вашего браузера ↓"
            f"\n┗ Текущее: <code>{user_agent}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
    )


@router.callback_query(F.data == "enter_proxy")
async def callback_enter_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_proxy)
    config = sett.get("config")
    proxy = config["funpay"]["api"]["proxy"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_conn_float_text(
            "🌐 Введите новый <b>прокси-сервер</b> (формат: user:pass@ip:port или ip:port) ↓"
            f"\n┗ Текущее: <code>{proxy}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
    )


@router.callback_query(F.data == "enter_funpayapi_requests_timeout")
async def callback_enter_funpayapi_requests_timeout(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_requests_timeout)
    config = sett.get("config")
    requests_timeout = config["funpay"]["api"]["requests_timeout"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_conn_float_text(
            "🛜 Введите новый <b>таймаут подключения</b> (в секундах) ↓"
            f"\n┗ Текущее: <code>{requests_timeout}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
    )


@router.callback_query(F.data == "enter_funpayapi_runner_requests_delay")
async def callback_enter_funpayapi_runner_requests_delay(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_runner_requests_delay)
    config = sett.get("config")
    requests_delay = config["funpay"]["api"]["runner_requests_delay"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_conn_float_text(
            "⏱️ Введите новую <b>периодичность запросов</b> (в секундах) ↓"
            f"\n┗ Текущее: <code>{requests_delay}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
    )


@router.callback_query(F.data == "enter_watermark_value")
async def callback_enter_watermark_value(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_watermark_value)
    config = sett.get("config")
    watermark_value = config["funpay"]["watermark"]["value"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_other_float_text(
            "✍️©️ Введите новый <b>водяной знак</b> под сообщениями ↓"
            f"\n┗ Текущее: <code>{watermark_value}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack())
    )


@router.callback_query(F.data == "enter_custom_commands_page")
async def callback_enter_custom_commands_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.CustomCommandsStates.waiting_for_page)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_comms_float_text(
            "📃 Введите номер страницы для перехода ↓"
        ), 
        reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_new_custom_command")
async def callback_enter_new_custom_command(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.CustomCommandsStates.waiting_for_new_custom_command)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_comm_float_text(
            "⌨️ Введите <b>новую команду</b> (например, <code>!тест</code>) ↓"
        ), 
        reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_custom_command_answer")
async def callback_enter_custom_command_answer(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        custom_commands = sett.get("custom_commands")
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await state.set_state(states.CustomCommandsStates.waiting_for_custom_command_answer)
        custom_command_answer = "\n".join(custom_commands[custom_command]) or "❌ Не задано"
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(
                f"💬 Введите новый <b>текст ответа</b> команды <code>{custom_command}</code> ↓"
                f"\n┗ Текущее: <blockquote>{custom_command_answer}</blockquote>"
            ), 
            reply_markup=templ.back_kb(calls.CustomCommandPage(command=custom_command).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_auto_deliveries_page")
async def callback_enter_auto_deliveries_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.AutoDeliveriesStates.waiting_for_page)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_deliv_float_text(
            "📃 Введите номер страницы для перехода ↓"
        ), 
        reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_new_auto_delivery_lot_id")
async def callback_enter_new_auto_delivery_lot_id(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_lot_id)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_deliv_float_text(
            "🆔 Введите <b>ID лота</b>, на который нужно добавить авто-выдачу ↓"
        ), 
        reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_auto_delivery_message")
async def callback_enter_auto_delivery_message(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_delivery_lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_message)
        auto_delivery_message = "\n".join(auto_deliveries[str(auto_delivery_lot_id)]) or "❌ Не задано"
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(
                f"💬 Введите новое <b>сообщение после покупки</b> лота <code>{auto_delivery_lot_id}</code>"
                f"\n┗ Текущее: <blockquote>{auto_delivery_message}</blockquote>"
            ), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=auto_delivery_lot_id).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_messages_page")
async def callback_enter_messages_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.MessagesStates.waiting_for_page)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_mess_float_text(
            "📃 Введите номер страницы для перехода ↓"
        ), 
        reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_message_text")
async def callback_enter_message_text(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        await state.set_state(states.MessagesStates.waiting_for_message_text)
        messages = sett.get("messages")
        mess_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_mess_float_text(
                f"💬 Введите новый <b>текст сообщения</b> <code>{message_id}</code> ↓"
                f"\n┗ Текущее: <blockquote>{mess_text}</blockquote>"
            ), 
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_mess_float_text(e), 
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_tg_logging_chat_id")
async def callback_enter_tg_logging_chat_id(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_tg_logging_chat_id)
    config = sett.get("config")
    tg_logging_chat_id = config["funpay"]["tg_logging"]["chat_id"] or "✔️ Ваш чат с ботом"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_logger_float_text(
            "💬 Введите новый <b>ID чата для логов</b> (вы можете указать как цифровой ID, так и юзернейм чата) ↓"
            f"\n┗ Текущее: <code>{tg_logging_chat_id}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack())
    )


@router.callback_query(F.data == "enter_auto_tickets_orders_per_ticket")
async def callback_enter_auto_tickets_orders_per_ticket(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_auto_tickets_orders_per_ticket)
    config = sett.get("config")
    auto_tickets_orders_per_ticket = config["funpay"]["auto_tickets"]["orders_per_ticket"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_tickets_float_text(
            "📋 Введите новое <b>кол-во заказов в одном тикете</b> ↓"
            f"\n┗ Текущее: <code>{auto_tickets_orders_per_ticket}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
    )


@router.callback_query(F.data == "enter_auto_tickets_min_order_age")
async def callback_enter_auto_tickets_min_order_age(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_auto_tickets_min_order_age)
    config = sett.get("config")
    auto_tickets_min_order_age = config["funpay"]["auto_tickets"]["min_order_age"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_tickets_float_text(
            "👴 Введите новый <b>минимальный возраст заказов</b> (в секундах) ↓"
            f"\n┗ Текущее: <code>{auto_tickets_min_order_age}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
    )


@router.callback_query(F.data == "enter_auto_tickets_create_interval")
async def callback_enter_enter_auto_tickets_create_interval(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_auto_tickets_create_interval)
    config = sett.get("config")
    auto_tickets_create_interval = config["funpay"]["auto_tickets"]["interval"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_tickets_float_text(
            "⏱️ Введите новый <b>интервал создания тикетов</b> (в секундах) ↓"
            f"\n┗ Текущее: <code>{auto_tickets_create_interval}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
    )


# --- Добавление новых данных в конфиг  ---

@router.callback_query(F.data == "add_new_custom_command")
async def callback_add_new_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        custom_commands = sett.get("custom_commands")
        new_custom_command = data.get("new_custom_command")
        new_custom_command_answer = data.get("new_custom_command_answer")
        if not new_custom_command:
            raise Exception("❌ Новая пользовательская команда не была найдена, повторите процесс с самого начала")
        if not new_custom_command_answer:
            raise Exception("❌ Ответ на новую пользовательскую команду не был найден, повторите процесс с самого начала")

        custom_commands[new_custom_command] = new_custom_command_answer.splitlines()
        sett.set("custom_commands", custom_commands)
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_new_comm_float_text(
                f"✅ <b>Пользовательская команда</b> <code>{new_custom_command}</code> была добавлена"
            ), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_new_comm_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "add_new_auto_delivery")
async def callback_add_new_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        auto_deliveries = sett.get("auto_deliveries")
        new_auto_delivery_lot_id = data.get("new_auto_delivery_lot_id")
        new_auto_delivery_message = data.get("new_auto_delivery_message")
        if not new_auto_delivery_lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        if not new_auto_delivery_message:
            raise Exception("❌ Сообщение авто-выдачи не было найдено, повторите процесс с самого начала")
        
        auto_deliveries[str(new_auto_delivery_lot_id)] = new_auto_delivery_message.splitlines()
        sett.set("auto_deliveries", auto_deliveries)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_new_deliv_float_text(
                f"✅ <b>Авто-выдача</b> на лот <code>{new_auto_delivery_lot_id}</code> была добавлена"
            ), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


# --- Подтверждение действия  ---

@router.callback_query(F.data == "confirm_deleting_custom_command")
async def callback_confirm_deleting_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(
                f"🗑️ Подтвердите <b>удаление пользовательской команды</b> <code>{custom_command}</code>"
            ), 
            reply_markup=templ.confirm_kb(confirm_cb="delete_custom_command", cancel_cb=calls.CustomCommandPage(command=custom_command).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "confirm_creating_tickets")
async def callback_confirm_creating_tickets(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.events_float_text(
            "📞✔️ Подтвердите <b>создание тикетов на закрытие заказов</b> ↓"
        ), 
        reply_markup=templ.confirm_kb(confirm_cb="create_tickets", cancel_cb=calls.MenuNavigation(to="events").pack())
    )


@router.callback_query(F.data == "confirm_deleting_auto_delivery")
async def callback_confirm_deleting_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_delivery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_delivery_lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(
                f"🗑️ Подтвердите <b>удаление пользовательской авто-выдачи</b> на лот <code>{auto_delivery_lot_id}</code>"
            ), 
            reply_markup=templ.confirm_kb(confirm_cb="delete_auto_delivery", cancel_cb=calls.AutoDeliveryPage(lot_id=auto_delivery_lot_id).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


# --- Удаление данных из конфига  ---

@router.callback_query(F.data == "delete_custom_command")
async def callback_delete_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        custom_commands = sett.get("custom_commands")
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        del custom_commands[custom_command]
        sett.set("custom_commands", custom_commands)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(
                f"✅ <b>Пользовательская команда</b> <code>{custom_command}</code> была удалена"
            ), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "delete_auto_delivery")
async def callback_delete_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_lot_id = data.get("auto_delivery_lot_id")
        if not auto_delivery_lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        
        del auto_deliveries[str(auto_delivery_lot_id)]
        sett.set("auto_deliveries", auto_deliveries)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(
                f"✅ <b>Авто-выдача</b> на лот <code>{auto_delivery_lot_id}</code> была удалена"
            ), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


# --- Различные действия ---

@router.callback_query(F.data == "reload_module")
async def callback_reload_module(callback: CallbackQuery, state: FSMContext):
    from core.modules import reload_module
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        module_uuid = data.get("module_uuid")
        
        await reload_module(module_uuid)
        return await callback_module_page(callback, calls.ModulePage(uuid=module_uuid), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.module_page_float_text(e), 
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )