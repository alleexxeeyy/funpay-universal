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
            f"\n・ Текущее: <code>{golden_key}</code>"
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
            f"\n・ Текущее: <code>{user_agent}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
    )


@router.callback_query(F.data == "enter_fp_proxy")
async def callback_enter_fp_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_fp_proxy)
    config = sett.get("config")
    proxy = config["funpay"]["api"]["proxy"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_conn_float_text(
            "🌐 Введите новый HTTP <b>прокси для FunPay</b> (формат: user:pass@ip:port или ip:port) ↓"
            f"\n・ Текущее: <code>{proxy}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
    )


@router.callback_query(F.data == "enter_tg_proxy")
async def callback_enter_tg_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_tg_proxy)
    config = sett.get("config")
    proxy = config["telegram"]["api"]["proxy"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_conn_float_text(
            "🌐 Введите новый HTTP <b>прокси для Telegram</b> (формат: user:pass@ip:port или ip:port) ↓"
            f"\n・ Текущее: <code>{proxy}</code>"
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
            f"\n・ Текущее: <code>{requests_timeout}</code>"
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
            f"\n・ Текущее: <code>{requests_delay}</code>"
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
            f"\n・ Текущее: <code>{watermark_value}</code>"
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
                f"\n・ Текущее: <blockquote>{custom_command_answer}</blockquote>"
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


@router.callback_query(F.data == "enter_new_auto_delivery_lot_link")
async def callback_enter_new_auto_delivery_lot_link(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_lot_link)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_deliv_float_text(
            "🔗 Введите <b>ссылку на лот</b>, на который нужно добавить авто-выдачу ↓"
        ), 
        reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_auto_delivery_lot_link")
async def callback_enter_auto_delivery_lot_link(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        lot_id = data.get("auto_delivery_lot_id")
        lot = data.get("auto_delivery_lot")
        if not any((lot_id, lot)):
            raise Exception("❌ Лот авто-выдачи не был найден, повторите процесс с самого начала")
        
        try: lot_title = lot.title_ru
        except: lot_title = lot_id
        
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_lot_link)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(
                f"🔗 Введите новую <b>ссылку на лот</b> авто-выдачи"
                f'\n・ Текущий: <a href="https://funpay.com/lots/offer?id={lot_id}">{lot_title}</a>'
            ), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=lot_id).pack())
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
                f"\n・ Текущее: <blockquote>{auto_delivery_message}</blockquote>"
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
                f"\n・ Текущее: <blockquote>{mess_text}</blockquote>"
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
            f"\n・ Текущее: <code>{tg_logging_chat_id}</code>"
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
            f"\n・ Текущее: <code>{auto_tickets_orders_per_ticket}</code>"
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
            f"\n・ Текущее: <code>{auto_tickets_min_order_age}</code>"
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
            f"\n・ Текущее: <code>{auto_tickets_create_interval}</code>"
        ), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
    )


@router.callback_query(F.data == "enter_logs_max_file_size")
async def callback_enter_logs_max_file_size(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_logs_max_file_size)
    config = sett.get("config")
    max_file_size = config["logs"]["max_file_size"] or "❌ Не указано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.logs_float_text(
            f"📄 Введите новый <b>максимальный размер файла логов</b> (в мегабайтах) ↓"
            f"\n・ Текущее: <b>{max_file_size} MB</b>"
        ), 
        reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
    )