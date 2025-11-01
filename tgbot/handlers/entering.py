import re
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from fpbot.funpaybot import get_funpay_bot

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()

    
def is_eng_str(str: str):
    pattern = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~ ]+$'
    return bool(re.match(pattern, str))


@router.message(states.ActionsStates.waiting_for_message_text, F.text)
async def handler_waiting_for_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        fpbot = get_funpay_bot()
        chat_name = data.get("chat_name")
        chat = fpbot.funpay_account.get_chat_by_name(chat_name, True)
        fpbot.send_message(chat_id=chat.id, text=message.text.strip())
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(f"✅ Пользователю <b>{chat_name}</b> было отправлено сообщение: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e), 
            reply_markup=templ.destroy_kb()
        )


@router.message(states.ActionsStates.waiting_for_review_answer_text, F.text)
async def handler_waiting_for_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        order_id = data.get("order_id")
        get_funpay_bot().funpay_account.send_review(order_id=order_id, text=message.text.strip())
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(f"✅ На отзыв по заказу <code>#{order_id}</code> был отправлен ответ: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e), 
            reply_markup=templ.destroy_kb()
        )


@router.message(states.SystemStates.waiting_for_password, F.text)
async def handler_waiting_for_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        config = sett.get("config")
        if message.text.strip() != config["telegram"]["bot"]["password"]:
            raise Exception("❌ Неверный ключ-пароль.")
        
        config["telegram"]["bot"]["signed_users"].append(message.from_user.id)
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.menu_text(),
            reply_markup=templ.menu_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.sign_text(e), 
            reply_markup=templ.destroy_kb()
        )


@router.message(states.MessagesStates.waiting_for_page, F.text)
async def handler_waiting_for_messages_page(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_mess_text(),
            reply_markup=templ.settings_mess_kb(int(message.text)-1)
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_mess_float_text(e),
            reply_markup=templ.back_kb(calls.MessagesPagination(page=data.get("last_page", 0)).pack())
        )
        

@router.message(states.MessagesStates.waiting_for_message_text, F.text)
async def handler_waiting_for_message_text(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        messages = sett.get("messages")
        message_split_lines = message.text.strip().split('\n')
        messages[data["message_id"]]["text"] = message_split_lines
        sett.set("messages", messages)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_mess_page_float_text(f"✅ <b>Текст сообщения</b> <code>{data['message_id']}</code> был успешно изменён на <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.back_kb(calls.MessagePage(message_id=data.get("message_id")).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_mess_page_float_text(e), 
            reply_markup=templ.back_kb(calls.MessagePage(message_id=data.get("message_id")).pack())
        )


@router.message(states.SettingsStates.waiting_for_golden_key, F.text)
async def handler_waiting_for_golden_key(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3 or len(message.text.strip()) >= 50:
            raise Exception("❌ Слишком короткое или длинное значение")

        config = sett.get("config")
        config["funpay"]["api"]["golden_key"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>golden_key</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )


@router.message(states.SettingsStates.waiting_for_user_agent, F.text)
async def handler_waiting_for_user_agent(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")

        config = sett.get("config")
        config["funpay"]["api"]["user_agent"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>user_agent</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )


@router.message(states.SettingsStates.waiting_for_proxy, F.text)
async def handler_waiting_for_proxy(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")
        if not is_eng_str(message.text.strip()):
            raise Exception("❌ Некорректный прокси")

        config = sett.get("config")
        config["funpay"]["api"]["proxy"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>Прокси</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_requests_timeout, F.text)
async def handler_waiting_for_requests_timeout(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["api"]["requests_timeout"] = int(message.text.strip())
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(f"✅ <b>Таймаут запросов</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_runner_requests_delay, F.text)
async def handler_waiting_for_runner_requests_delay(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["api"]["runner_requests_delay"] = int(message.text.strip())
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(f"✅ <b>Периодичность запросов</b> была успешна изменена на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )
            

@router.message(states.SettingsStates.waiting_for_tg_logging_chat_id, F.text)
async def handler_waiting_for_tg_logging_chat_id(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None) 
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")
        
        if message.text.strip().isdigit(): chat_id = "-100" + str(message.text.strip()).replace("-100", "")
        else: chat_id = "@" + str(message.text.strip()).replace("@", "")

        config = sett.get("config")
        config["funpay"]["tg_logging"]["chat_id"] = chat_id
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_logger_float_text(f"✅ <b>ID чата для логов</b> было успешно изменено на <b>{chat_id}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_logger_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack())
        )


@router.message(states.SettingsStates.waiting_for_auto_tickets_orders_per_ticket, F.text)
async def handler_waiting_for_auto_tickets_orders_per_ticket(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["auto_tickets"]["orders_per_ticket"] = int(message.text.strip())
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_tickets_float_text(f"✅ <b>Кол-во заказов в одном тикете</b> было успешно изменено на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
        )


@router.message(states.SettingsStates.waiting_for_auto_tickets_min_order_age, F.text)
async def handler_waiting_for_auto_tickets_min_order_age(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["auto_tickets"]["min_order_age"] = int(message.text.strip())
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_tickets_float_text(f"✅ <b>Минимальный возраст заказов</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
        )


@router.message(states.SettingsStates.waiting_for_auto_tickets_create_interval, F.text)
async def handler_waiting_for_auto_tickets_create_interval(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["auto_tickets"]["interval"] = int(message.text.strip())
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_tickets_float_text(f"✅ <b>Интервал создания тикетов</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="tickets").pack())
        )


@router.message(states.CustomCommandsStates.waiting_for_page, F.text)
async def handler_waiting_for_custom_commands_page(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_comms_text(),
            reply_markup=templ.settings_comms_kb(page=int(message.text)-1)
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_comms_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=data.get("last_page", 0)).pack())
        )
        

@router.message(states.CustomCommandsStates.waiting_for_new_custom_command, F.text)
async def handler_waiting_for_custom_command(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 32:
            raise Exception("❌ Слишком короткая или длинная команда")

        data = await state.get_data()
        await state.update_data(new_custom_command=message.text.strip())
        await state.set_state(states.CustomCommandsStates.waiting_for_new_custom_command_answer)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_comm_float_text(f"💬 Введите <b>ответ для команды</b> <code>{message.text.strip()}</code> ↓"),
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=data.get("last_page", 0)).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_comm_float_text(e), 
             reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=data.get("last_page", 0)).pack())
        )
        

@router.message(states.CustomCommandsStates.waiting_for_new_custom_command_answer, F.text)
async def handler_waiting_for_new_custom_command_answer(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий ответ")

        data = await state.get_data()
        await state.update_data(new_custom_command_answer=message.text.strip())
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_comm_float_text(f"➕ Подтвердите <b>добавление новой команды</b> <code>{data['new_custom_command']}</code> ↓"),
            reply_markup=templ.confirm_kb(confirm_cb="add_new_custom_command", cancel_cb=calls.CustomCommandsPagination(page=data.get("last_page", 0)).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_comm_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=data.get("last_page", 0)).pack())
        )


@router.message(states.CustomCommandsStates.waiting_for_custom_command_answer, F.text)
async def handler_waiting_for_custom_command_answer(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        custom_commands = sett.get("custom_commands")
        custom_commands[data["custom_command"]] = message.text.strip().split('\n')
        sett.set("custom_commands", custom_commands)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_comms_float_text(f"✅ <b>Текст ответа</b> команды <code>{data['custom_command']}</code> был успешно изменён на: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.back_kb(calls.CustomCommandPage(command=data["custom_command"]).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_comms_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandPage(command=data["custom_command"]).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_page, F.text)
async def handler_waiting_for_auto_deliveries_page(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_delivs_float_text(f"📃 Введите номер страницы для перехода ↓"),
            reply_markup=templ.settings_delivs_kb(int(message.text)-1)
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_delivs_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_lot_id, F.text)
async def handler_waiting_for_new_auto_delivery_lot_id(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 100:
            raise Exception("❌ Слишком короткий или длинный ID лота")

        data = await state.get_data()
        await state.update_data(new_auto_delivery_lot_id=int(message.text.strip()))
        await state.set_state(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(f"💬 Введите <b>сообщение авто-выдачи</b>, которое будет писаться после покупки лота ↓"),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message, F.text)
async def handler_waiting_for_new_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")

        data = await state.get_data()
        await state.update_data(new_auto_delivery_message=message.text.strip())
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(f"➕ Подтвердите <b>добавление авто-выдачи</b> на лот <b>{data['new_auto_delivery_lot_id']}</b>"),
            reply_markup=templ.confirm_kb(confirm_cb="add_new_auto_delivery", cancel_cb=calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_message, F.text)
async def handler_waiting_for_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        auto_deliveries = sett.get("auto_deliveries")
        answer_split_lines = message.text.strip().split('\n')
        auto_deliveries[data["auto_delivery_lot_id"]] = answer_split_lines
        sett.set("auto_deliveries", auto_deliveries)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(f"✅ <b>Сообщение авто-выдачи</b> лота <code>{data['auto_delivery_lot_id']}</code> было успешно изменено на: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=data.get("auto_delivery_lot_id")).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=data.get("auto_delivery_lot_id")).pack())
        )
            
        
@router.message(states.SettingsStates.waiting_for_watermark_value, F.text)
async def handler_waiting_for_watermark_value(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 150:
            raise Exception("❌ Слишком короткое или длинное значение")

        config = sett.get("config")
        config["funpay"]["watermark"]["value"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_other_float_text(f"✅ <b>Водяной знак сообщений</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
             message=message,
            text=templ.settings_other_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack())
        )