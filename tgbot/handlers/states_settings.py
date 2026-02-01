from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message

from core.utils import (
    is_golden_key_valid,
    is_user_agent_valid,
    is_proxy_valid, 
    is_proxy_working
)


router = Router()


@router.message(states.SettingsStates.waiting_for_golden_key, F.text)
async def handler_waiting_for_golden_key(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not is_golden_key_valid(message.text.strip()):
            raise Exception("❌ Неверный формат Golden Key. Пример: bzhzi9n5x9y1xaaa9j48kp6bu4671xxy")

        config = sett.get("config")
        config["funpay"]["api"]["golden_key"] = message.text.strip()
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>Golden Key</b> был успешно изменён на <b>{message.text.strip()}</b>"),
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
        if not is_user_agent_valid(message.text.strip()):
            raise Exception("❌ Неверный формат User Agent. Пример: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")

        config = sett.get("config")
        config["funpay"]["api"]["user_agent"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>User Agent</b> был успешно изменён на <b>{message.text.strip()}</b>"),
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
        if not is_proxy_valid(message.text.strip()):
            raise Exception("❌ Неверный формат прокси. Правильный формат: user:pass@ip:port или ip:port")
        if not is_proxy_working(message.text.strip()):
            raise Exception("❌ Указанный вами прокси не работает. Нет подключения к funpay.com")

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


@router.message(states.SettingsStates.waiting_for_logs_max_file_size, F.text)
async def handler_waiting_for_logs_max_file_size(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        max_size = message.text.strip()
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")
        max_size = int(max_size)

        config = sett.get("config")
        config["logs"]["max_file_size"] = max_size
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.logs_float_text(f"✅ <b>Максимальный размер файла логов</b> был успешно изменён на <b>{max_size} MB</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.logs_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
        )