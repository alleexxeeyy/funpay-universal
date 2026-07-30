import os
import traceback
from html import escape
from logging import getLogger
from aiogram import types, Router, Bot, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from core.configs import (
    MAX_IMPORT_SIZE,
    SUPPORTED_EXTENSIONS,
    safe_file_name,
    prepare_import_dir,
    clear_import_dir,
    clear_temp_dir,
    peek_import
)
from core.modules import (
    MODULE_EXTENSIONS,
    MAX_MODULE_SIZE,
    ModuleImportError,
    prepare_module_import_dir,
    clear_module_import_dir,
    import_modules_from_archive
)

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message

from utils import (
    is_golden_key_valid,
    is_user_agent_valid,
    is_proxy_valid,
    is_proxy_working,
    is_url_valid,
    is_custom_api_url_working,
    normalize_custom_api_url
)


logger = getLogger("universal.telegram")

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
            text=templ.auth_float_text(f"✅ <b>Golden Key</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="auth").pack())
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
            text=templ.auth_float_text(f"✅ <b>User Agent</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="auth").pack())
        )


@router.message(states.SettingsStates.waiting_for_fp_proxy, F.text)
async def handler_waiting_for_fp_proxy(message: types.Message, state: FSMContext):
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
            text=templ.auth_float_text(f"✅ <b>Прокси для FunPay</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_tg_proxy, F.text)
async def handler_waiting_for_tg_proxy(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")
        if not is_proxy_valid(message.text.strip()):
            raise Exception("❌ Неверный формат прокси. Правильный формат: user:pass@ip:port или ip:port")
        if not is_proxy_working(message.text.strip(), "https://api.telegram.org/"):
            raise Exception("❌ Указанный вами прокси не работает. Нет подключения к api.telegram.org")

        config = sett.get("config")
        config["telegram"]["api"]["proxy"] = message.text.strip()
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(f"✅ <b>Прокси для Telegram</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_tg_custom_api_url, F.text)
async def handler_waiting_for_tg_custom_api_url(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        cust_api_url = normalize_custom_api_url(message.text.strip())

        if not is_url_valid(cust_api_url):
            raise Exception("❌ Неверный формат URL. Пример: https://tg-proxy.ваш-поддомен.workers.dev")
        if not is_custom_api_url_working(cust_api_url):
            raise Exception("❌ По указанному URL Telegram API не отвечает. Убедитесь, что прокси развёрнут и работает")

        config = sett.get("config")
        config["telegram"]["api"]["custom_api_url"] = cust_api_url
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.conn_float_text(
                f"✅ <b>Кастомный URL Telegram API</b> был успешно изменён на <b>{cust_api_url}</b>"
                f"\n\n❗ Изменения применятся после перезагрузки бота"
            ),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.conn_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
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
            text=templ.conn_float_text(f"✅ <b>Таймаут запросов</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.conn_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
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
            text=templ.conn_float_text(f"✅ <b>Периодичность запросов</b> была успешна изменена на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.conn_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
            

@router.message(states.SettingsStates.waiting_for_notifications_chat_id, F.text)
async def handler_waiting_for_notifications_chat_id(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None) 
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")
        
        if message.text.strip().isdigit(): 
            chat_id = "-100" + str(message.text.strip()).replace("-100", "")
        else: 
            chat_id = "@" + str(message.text.strip()).replace("@", "")

        config = sett.get("config")
        config["funpay"]["notifications"]["chat_id"] = chat_id
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.notifications_float_text(f"✅ <b>ID чата для логов</b> было успешно изменено на <b>{chat_id}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="notifications").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.notifications_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="notifications").pack())
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
            text=templ.tickets_float_text(f"✅ <b>Кол-во заказов в одном тикете</b> было успешно изменено на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
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
            text=templ.tickets_float_text(f"✅ <b>Мин. возраст заказов</b> был успешно изменён на <b>{message.text.strip()} сек.</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
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
            text=templ.tickets_float_text(f"✅ <b>Интервал создания тикетов</b> был успешно изменён на <b>{message.text.strip()} сек.</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
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
            text=templ.other_float_text(f"✅ <b>Водяной знак сообщений</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="other").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
             message=message,
            text=templ.other_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="other").pack())
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


@router.message(states.SettingsStates.waiting_for_new_fast_reply_text, F.text)
async def handler_waiting_for_new_fast_reply_text(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        text = message.text

        data = await state.get_data()
        last_page = data.get("last_page", 0)

        fast_replies = sett.get("fast_replies")
        fast_replies.append(text)
        sett.set("fast_replies", fast_replies)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_fast_reply_text(f"✅ <b>Быстрый ответ</b> успешно добавлен: <blockquote>{text}</blockquote>"),
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_fast_reply_text(e), 
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )
            

@router.message(states.SettingsStates.waiting_for_fast_reply_text, F.text)
async def handler_waiting_for_fast_reply_text(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        text = message.text

        data = await state.get_data()
        index = data.get("fast_reply_index")
        last_page = data.get("last_page", 0)

        fast_replies = sett.get("fast_replies")
        fast_replies[index] = text
        sett.set("fast_replies", fast_replies)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_fast_reply_text(f"✅ <b>Текст авто-ответ</b> был успешно изменён на: <blockquote>{text}</blockquote>"),
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_fast_reply_text(e), 
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )


@router.message(states.SettingsStates.waiting_for_module_file, F.document)
async def handler_waiting_for_module_file(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    data = await state.get_data()
    last_page = data.get("last_page", 0)

    try:
        await state.set_state(None)

        file_name = safe_file_name(message.document.file_name)
        if not file_name.lower().endswith(MODULE_EXTENSIONS):
            raise ModuleImportError("❌ Нужен архив в формате <b>.zip</b> или <b>.rar</b>")
        if (message.document.file_size or 0) > MAX_MODULE_SIZE:
            raise ModuleImportError(f"❌ Файл слишком большой (максимум {MAX_MODULE_SIZE // 1024 // 1024} МБ)")

        archive_path = os.path.join(prepare_module_import_dir(user_id), file_name)
        await bot.download(message.document, destination=archive_path)

        installed = import_modules_from_archive(archive_path)

        if len(installed) == 1:
            result = f"✅ Модуль <b>успешно импортирован</b>: <code>{file_name}</code>"
        else:
            str_installed = "\n".join(f"・ <b>{name}</b>" for name in installed)
            result = (
                f"✅ Успешно импортировано <b>{len(installed)} модулей</b> из <code>{file_name}</code>:"
                f"\n\n<blockquote>{str_installed}</blockquote>"
            )

        await throw_float_message(
            state=state,
            message=message,
            text=templ.modules_float_text(
                f"{result}"
                f"\n\n❗ Для подключения <b>необходима перезагрузка</b> — /restart"
            ),
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )
    except Exception as e:
        if not isinstance(e, ModuleImportError):
            logger.error(f"Не удалось импортировать модуль: {traceback.format_exc()}")
        text = str(e) if isinstance(e, ModuleImportError) else (
            f"❌ Не удалось импортировать модуль: <blockquote>{escape(str(e))}</blockquote>"
        )

        await throw_float_message(
            state=state,
            message=message,
            text=templ.modules_float_text(text),
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )
    finally:
        clear_module_import_dir(user_id)
        clear_temp_dir()


@router.message(states.SettingsStates.waiting_for_module_file)
async def handler_waiting_for_module_file_wrong(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.modules_float_text("❌ Нужен <b>архив</b> с модулем в формате <b>.zip</b> или <b>.rar</b>"),
        reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
    )


@router.message(states.SettingsStates.waiting_for_config_file, F.document)
async def handler_waiting_for_config_file(message: types.Message, state: FSMContext, bot: Bot):
    from ..callback_handlers.actions_configs import apply_import

    user_id = message.from_user.id
    try:
        await state.set_state(None)

        file_name = safe_file_name(message.document.file_name)
        if not file_name.lower().endswith(SUPPORTED_EXTENSIONS):
            raise Exception("❌ Нужен файл в формате <b>.json</b> или архив <b>.zip</b> / <b>.rar</b>")
        if (message.document.file_size or 0) > MAX_IMPORT_SIZE:
            raise Exception(f"❌ Файл слишком большой (максимум {MAX_IMPORT_SIZE // 1024 // 1024} МБ)")

        import_path = os.path.join(prepare_import_dir(user_id), file_name)
        await bot.download(message.document, destination=import_path)
        await state.update_data(import_config_path=import_path)

        if "config" in peek_import(import_path):
            return await throw_float_message(
                state=state,
                message=message,
                text=templ.configs_float_text(
                    "📥 Файл принят. Что делать с <b>Golden Key, токеном Telegram бота и ключ-паролем</b>?"
                    "\n\n<blockquote><b>(?)</b> Список авторизованных пользователей останется вашим в любом случае, "
                    "чтобы вы не потеряли доступ к боту.</blockquote>"
                ),
                reply_markup=templ.configs_secrets_kb()
            )

        return await apply_import(state, message, user_id, keep_secrets=True)
    except Exception as e:
        clear_import_dir(user_id)
        await state.update_data(import_config_path=None)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.configs_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="configs").pack())
        )