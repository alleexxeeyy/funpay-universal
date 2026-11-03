from aiogram import F, Router
from html import escape
from aiogram.types import CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
from pathlib import Path
from collections import deque
import shutil
import asyncio
import os

from settings import Settings as sett
from core.blacklist import get_blacklist_entry, add_to_blacklist, remove_from_blacklist
from core.modules import install_staged_module, clear_module_import_dir, ModuleImportError

from .navigation import *
from .pagination import *
from .page import callback_module_page
from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message, do_auth, notify, answer_callback, show_module_checks


router = Router()


@router.callback_query(F.data == "destroy")
async def callback_destroy(callback: CallbackQuery):
    await callback.message.delete()

@router.callback_query(F.data == "null_answer")
async def callback_null_answer(callback: CallbackQuery):
    await callback.bot.answer_callback_query(callback.id)


@router.callback_query(calls.DeleteSignedUser.filter())
async def callback_delete_signed_user(callback: CallbackQuery, callback_data: calls.DeleteSignedUser, state: FSMContext):
    from core import access

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)
        id = callback_data.id

        if not access.is_signed(callback.from_user.id): # у удалённого юзера могло остаться старое меню
            return await answer_callback(callback.bot, callback)
        
        config = sett.get("config")
        if config["telegram"]["bot"]["signed_users"] == [id]:
            raise Exception("❌ Это последний пользователь — без него у бота не останется владельца")
        config["telegram"]["bot"]["signed_users"].remove(id)
        sett.set("config", config)
        
        if callback.from_user.id == id:
            return await do_auth(callback.message, state)
        else:
            return await callback_signed_users_pagination(
                callback, calls.SignedUsersPagination(page=last_page), state
            )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.signed_users_float_text(e),
            reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack())
        )


@router.callback_query(calls.AccessRequest.filter())
async def callback_access_request(callback: CallbackQuery, callback_data: calls.AccessRequest, state: FSMContext):
    from core import access

    if not access.is_signed(callback.from_user.id): # callback_data подделывается — проверяем, кто жмёт
        return await answer_callback(callback.bot, callback)

    user_id = callback_data.id
    request = access.get_request(user_id) or {}
    username, name = request.get("username"), request.get("name")
    await state.set_state(None)

    if callback_data.do == "deny":
        return await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.access_request_text(user_id, username, name, "❌ Запрос отклонён"),
            reply_markup=templ.destroy_kb(),
            callback=callback
        )

    if callback_data.do == "cancel":
        return await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.access_request_text(user_id, username, name),
            reply_markup=templ.access_request_kb(user_id),
            callback=callback
        )

    if access.is_signed(user_id):
        return await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.access_request_text(user_id, username, name, "✅ У этого человека уже есть доступ"),
            reply_markup=templ.destroy_kb(),
            callback=callback
        )

    await state.set_state(states.SystemStates.waiting_for_access_confirm)
    await state.update_data(access_user_id=user_id, access_request={"username": username, "name": name})
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.access_confirm_text(user_id, username, name),
        reply_markup=templ.access_confirm_kb(user_id),
        callback=callback
    )


@router.callback_query(calls.DeleteFastReply.filter())
async def callback_delete_fast_reply(callback: CallbackQuery, callback_data: calls.DeleteFastReply, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_fast_replies_pagination(
                callback, calls.FastRepliesPagination(page=last_page), state
            )
        
        fast_replies = sett.get("fast_replies")
        fast_replies.pop(index)
        sett.set("fast_replies", fast_replies)
        
        return await callback_fast_replies_pagination(
            callback, calls.FastRepliesPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.fast_replies_float_text(e),
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "clean_fp_proxy")
async def callback_clean_fp_proxy(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["api"]["proxy"] = ""
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="conn"), state
    )


@router.callback_query(F.data == "clean_tg_proxy")
async def callback_clean_tg_proxy(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["telegram"]["api"]["proxy"] = ""
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="conn"), state
    )


@router.callback_query(F.data == "clean_tg_custom_api_url")
async def callback_clean_tg_custom_api_url(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["telegram"]["api"]["custom_api_url"] = ""
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="conn"), state
    )


@router.callback_query(F.data == "clean_notifications_chat_id")
async def callback_clean_notifications_chat_id(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["notifications"]["chat_id"] = ""
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


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
            text=templ.new_comm_float_text(
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
            text=templ.new_comm_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "add_new_auto_delivery")
async def callback_add_new_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        auto_deliveries = sett.get("auto_deliveries")
        
        lot_id = data.get("new_auto_delivery_lot_id")
        lot = data.get("new_auto_delivery_lot")
        message = data.get("new_auto_delivery_message")
        if not all((lot_id, message)):
            raise Exception("❌ Не удалось найти данные авто-выдачи, повторите процесс с самого начала")
        
        auto_deliveries[str(lot_id)] = message.splitlines()
        sett.set("auto_deliveries", auto_deliveries)

        try: lot_title = lot.title_ru
        except: lot_title = lot_id
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.new_deliv_float_text(
                f"✅ <b>Авто-выдача</b> на лот "
                f'<a href="https://funpay.com/lots/offer?id={lot_id}">{lot_title}</a> была добавлена'
            ), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "send_module_file")
async def callback_send_module_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.SettingsStates.waiting_for_module_file)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.modules_float_text(
            "🗂 Отправьте <b>архив</b> с модулем/модулями (zip, rar) "
            "или одиночный файл модуля (<b>.py</b>):"
        ),
        reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
    )


@router.callback_query(F.data.startswith("modimp_"))
async def callback_module_import_action(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id
    data = await state.get_data()
    pending = data.get("import_pending")
    last_page = (pending or {}).get("last_page", data.get("last_page", 0))

    # забираем и сбрасываем сразу — повторный клик уже не найдёт pending
    await state.update_data(import_pending=None)

    fresh = (pending or {}).get("fresh_installed") or []
    collided = (pending or {}).get("collided") or []

    if not pending or action not in ("merge", "replace", "duplicate", "cancel"):
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.modules_float_text("❌ Сессия импорта истекла — повторите импорт заново."),
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )
        await callback.answer()
        return

    fresh_note = ""
    if fresh:
        fresh_note = "\n\n✅ Новые модули из архива установлены: " + ", ".join(f"<b>{n}</b>" for n in fresh)

    if action == "cancel":
        clear_module_import_dir(user_id)
        await callback.answer()
        return await show_module_checks(
            callback.message, state,
            "✖️ Импорт существующих модулей отменён." + fresh_note,
            fresh, calls.ModulesPagination(page=last_page).pack()
        )

    if any(not os.path.exists(mod["source"]) for mod in collided):
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.modules_float_text("❌ Сессия импорта истекла — повторите импорт заново."),
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )
        clear_module_import_dir(user_id)
        await callback.answer()
        return

    installed = []
    try:
        for mod in collided:
            installed.append(install_staged_module(mod, action))
        verb = {"merge": "обновлены", "replace": "переустановлены", "duplicate": "добавлены копией"}[action]
        str_installed = "\n".join(f"・ <b>{name}</b>" for name in installed)
        text = f"✅ Модули {verb}:\n<blockquote>{str_installed}</blockquote>{fresh_note}"
    except Exception as e:
        done = ("\n\nУспели установиться: " + ", ".join(f"<b>{n}</b>" for n in installed)) if installed else ""
        text = (str(e) if isinstance(e, ModuleImportError) else
                f"❌ Не удалось установить модуль: <blockquote>{escape(str(e))}</blockquote>") + done

    clear_module_import_dir(user_id)
    await callback.answer()
    await show_module_checks(callback.message, state, text, installed + fresh, calls.ModulesPagination(page=last_page).pack())


_module_check_lock = asyncio.Lock() # два быстрых нажатия не должны откатить и тут же удалить модуль


@router.callback_query(calls.ModuleCheckAction.filter())
async def callback_module_check_action(callback: CallbackQuery, callback_data: calls.ModuleCheckAction, state: FSMContext):
    from core.access import is_signed
    from core.modules import remove_module, restore_module_backup, drop_module_backup

    if not is_signed(callback.from_user.id):
        return await answer_callback(callback.bot, callback)

    async with _module_check_lock:
        data = await state.get_data()
        checks = data.get("module_checks") or []
        back_cb = data.get("module_checks_back") or calls.ModulesPagination(page=0).pack()
        token = data.get("module_checks_token")
        if callback_data.token != token or callback_data.idx >= len(checks):
            return await notify(callback, "Меню устарело — импортируйте модуль заново", alert=True)

        check = checks[callback_data.idx]
        do = callback_data.do
        if do == "trace":
            await callback.bot.send_document(
                chat_id=callback.from_user.id,
                document=BufferedInputFile(check["trace"].encode("utf-8"), filename=f"{check['name']}_error.txt"),
                reply_markup=templ.destroy_kb()
            )
            return await answer_callback(callback.bot, callback)

        if check["status"] not in ("error", "timeout"):
            return await answer_callback(callback.bot, callback)

        try:
            if do in ("delete", "rollback"): # проверка вне бота может ошибиться — удаление и откат только со второго нажатия
                check["confirm"] = do
            elif do == "cancel":
                check.pop("confirm", None)
            elif do == "rollback_yes" and check.get("confirm") == "rollback":
                restore_module_backup(check["name"])
                check["status"] = "rolled_back"
                check.pop("confirm", None)
            elif do == "delete_yes" and check.get("confirm") == "delete":
                remove_module(check["name"])
                drop_module_backup(check["name"])
                check["status"] = "deleted"
                check.pop("confirm", None)
            else:
                return await answer_callback(callback.bot, callback)
        except Exception as e:
            check.pop("confirm", None)
            await state.update_data(module_checks=checks)
            return await notify(callback, str(e) if isinstance(e, ModuleImportError) else f"❌ Не получилось: {e}", alert=True)

        await state.update_data(module_checks=checks)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.modules_float_text(templ.module_check_text(data.get("module_checks_header", ""), checks)),
            reply_markup=templ.module_check_kb(checks, back_cb, token),
            callback=callback
        )


@router.callback_query(F.data == "module_check_restart")
async def callback_module_check_restart(callback: CallbackQuery, state: FSMContext):
    from core.utils import restart
    from core.bootreport import set_marker
    from core.access import is_signed

    if not is_signed(callback.from_user.id):
        return await answer_callback(callback.bot, callback)

    await state.set_state(None)
    mess = await throw_float_message(
        state=state,
        message=callback.message,
        text="🔄️ <b>Перезагружаю бота</b>, подождите...",
        reply_markup=templ.destroy_kb(),
        callback=callback
    )
    set_marker("restart", callback.message.chat.id, mess.message_id if mess else callback.message.message_id)
    restart(from_tg=True)


@router.callback_query(F.data == "reload_module")
async def callback_reload_module(callback: CallbackQuery, state: FSMContext):
    from core.modules import reload_module
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        module_uuid = data.get("module_uuid")
        
        await reload_module(module_uuid)
        return await callback_module_page(
            callback, calls.ModulePage(uuid=module_uuid), state
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.module_page_float_text(e), 
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )


@router.callback_query(calls.RememberChatName.filter())
async def callback_remember_chat_name(callback: CallbackQuery, callback_data: calls.RememberChatName, state: FSMContext):
    await state.set_state(None)
    
    chat_name = callback_data.name
    do = callback_data.do
    
    await state.update_data(chat_name=chat_name)
    
    if do == "send_mess":
        await state.set_state(states.ActionsStates.waiting_for_fast_answer_message)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(f"💬 Введите <b>сообщение</b> для отправки в чат:"),
            reply_markup=templ.destroy_kb(),
            callback=callback,
            reply_to=callback.message.message_id
        )

    elif do == "send_fast_reply":
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
            reply_markup=templ.fast_sel_fast_reply_kb(chat_name=chat_name, page=0),
            callback=callback,
            reply_to=callback.message.message_id
        )

    elif do == "blacklist":
        await state.update_data(blacklist_chat_user=chat_name)
        entry = get_blacklist_entry(chat_name)
        if entry:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.do_action_text(f"🚫 Покупатель уже <b>в чёрном списке</b>:\n{templ.blacklist_entry_text(entry)}"),
                reply_markup=templ.chat_blacklisted_kb(),
                callback=callback,
                reply_to=callback.message.message_id
            )
        else:
            await state.update_data(chat_blacklist_reason=None)
            await state.set_state(states.BlacklistStates.waiting_for_chat_blacklist_reason)
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.do_action_text(f"🚫 Введите <b>причину</b> добавления <code>{escape(chat_name)}</code> в чёрный список:"),
                reply_markup=templ.chat_blacklist_reason_kb(),
                callback=callback,
                reply_to=callback.message.message_id
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
            text=templ.do_action_text("✔️ Подтвердите <b>возврат</b> заказа:"), 
            reply_markup=templ.confirm_kb(
                confirm_cb=calls.FastRefundOrder(id=order_id).pack(), 
                cancel_cb="destroy"
            ),
            callback=callback,
            reply_to=callback.message.message_id
        )
        
    elif do == "answer_rev":
        await state.set_state(states.ActionsStates.waiting_for_fast_review_answer)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.do_action_text("💬 Введите <b>ответ на отзыв</b> по заказу:"), 
            reply_markup=templ.destroy_kb(),
            callback=callback,
            reply_to=callback.message.message_id
        )


@router.callback_query(F.data == "add_chat_to_blacklist")
async def callback_add_chat_to_blacklist(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        chat_name = data.get("blacklist_chat_user")
        if not chat_name:
            raise Exception("❌ Чат не был найден, повторите процесс с самого начала")

        if not add_to_blacklist(chat_name, data.get("chat_blacklist_reason") or ""):
            raise Exception(f"❌ Покупатель <code>{escape(chat_name)}</code> уже в чёрном списке")
        await state.update_data(chat_blacklist_reason=None)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(f"✅ Покупатель <code>{escape(chat_name)}</code> добавлен <b>в чёрный список</b>"),
            reply_markup=templ.destroy_kb(),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb(),
            callback=callback
        )


@router.callback_query(F.data == "remove_chat_from_blacklist")
async def callback_remove_chat_from_blacklist(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        chat_name = data.get("blacklist_chat_user")
        if not chat_name:
            raise Exception("❌ Чат не был найден, повторите процесс с самого начала")

        if not remove_from_blacklist(chat_name):
            raise Exception(f"❌ Покупателя <code>{escape(chat_name)}</code> нет в чёрном списке")
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(f"✅ Покупатель <code>{escape(chat_name)}</code> убран <b>из чёрного списка</b>"),
            reply_markup=templ.destroy_kb(),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb(),
            callback=callback
        )


@router.callback_query(F.data == "add_new_blacklist_user")
async def callback_add_new_blacklist_user(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        username = data.get("new_blacklist_user")
        if not username:
            raise Exception("❌ Никнейм покупателя не был найден, повторите процесс с самого начала")

        if not add_to_blacklist(username):
            raise Exception(f"❌ Покупатель <code>{escape(username)}</code> уже в чёрном списке")
        await state.update_data(new_blacklist_user=None)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.new_blacklist_user_float_text(f"✅ Покупатель <code>{escape(username)}</code> добавлен в чёрный список"),
            reply_markup=templ.back_kb(calls.BlacklistPagination(page=last_page).pack()),
            callback=callback
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.new_blacklist_user_float_text(e),
            reply_markup=templ.back_kb(calls.BlacklistPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(F.data == "remove_blacklist_user")
async def callback_remove_blacklist_user(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        username = data.get("blacklist_user")
        if not username:
            raise Exception("❌ Покупатель не был найден, повторите процесс с самого начала")

        remove_from_blacklist(username)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.blacklist_page_float_text(f"✅ Покупатель <code>{escape(username)}</code> убран из чёрного списка"),
            reply_markup=templ.back_kb(calls.BlacklistPagination(page=last_page).pack()),
            callback=callback
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.blacklist_page_float_text(e),
            reply_markup=templ.back_kb(calls.BlacklistPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(F.data == "create_tickets")
async def callback_create_tickets(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.tickets_float_text(
                "📞 Идёт <b>создание тикета на закрытие заказов</b>, ожидайте (см. консоль)..."
            ),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )
        
        from fpbot.funpaybot import get_funpay_bot as fpbot
        success, url, cnt, error = fpbot().create_ticket()
        
        if success:
            await throw_float_message(
                state=state, 
                message=callback.message, 
                text=templ.tickets_float_text(
                    f"📞✅ Успешно создан <b><a href=\"{url}\">тикет</a></b> на закрытие {cnt} заказов"
                ), 
                reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
            )
        else:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.tickets_float_text(f"❌ Не удалось <b>создать тикет</b>: <blockquote>{error}</blockquote>"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
            )
    except Exception as e:
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )


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
            text=templ.comm_page_float_text(
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
            text=templ.comm_page_float_text(e), 
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
            text=templ.deliv_page_float_text(
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
            text=templ.deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "select_logs_file_lines")
async def callback_select_logs_file_lines(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.logs_float_text(f"Выберите объём файла:"), 
        reply_markup=templ.logs_file_lines_kb()
    )


@router.callback_query(calls.SendLogsFile.filter())
async def callback_send_logs_file(callback: CallbackQuery, callback_data: calls.SendLogsFile, state: FSMContext):
    await state.set_state(None)
    lines = callback_data.lines
    
    try:
        src_dir = Path(__file__).resolve().parents[2]
        logs_file = os.path.join(src_dir, "logs", "latest.log")
        txt_file = os.path.join(src_dir, "logs", "Лог работы.txt")
        
        if lines > 0:
            with open(logs_file, 'r', encoding='utf-8') as f:
                last_lines = deque(f, lines)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.writelines(last_lines)
        else:
            shutil.copy(logs_file, txt_file)
        
        await callback.message.answer_document(
            document=FSInputFile(txt_file),
            reply_markup=templ.destroy_kb()
        )
        try: await callback.bot.answer_callback_query(callback.id, cache_time=0)
        except: pass

        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.logs_text(), 
            reply_markup=templ.logs_kb()
        )
    finally:
        try: os.remove(txt_file)
        except: pass


@router.callback_query(F.data == "install_update")
async def callback_install_update(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)

        mess = await throw_float_message(
            state=state,
            message=callback.message,
            text="<b>🚀 Устанавливаю обновление...</b>" ,
            callback=callback,
            reply_to=callback.message.message_id
        )

        from updater import download_update, install_update, latest_release
        from core.utils import restart
        from core.bootreport import set_marker

        bytes = download_update(latest_release)
        if not bytes:
            return
        
        if install_update(latest_release, bytes):
            await throw_float_message(
                state=state,
                message=mess,
                text="<b>✅ Обновление установлено</b>" ,
                callback=callback
            )

            mess = await throw_float_message(
                state=state,
                message=mess,
                text="🔄️ <b>Перезагружаю бота</b>, подождите...",
                reply_markup=templ.destroy_kb(),
                callback=callback,
                send=True
            )
            
            set_marker("update", callback.message.chat.id, mess.message_id if mess else None)
            restart(from_tg=True)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.error_text(e),
            reply_markup=templ.destroy_kb(),
            callback=callback
        )


@router.callback_query(calls.BootErrorFile.filter())
async def callback_boot_error_file(callback: CallbackQuery, callback_data: calls.BootErrorFile):
    from core import bootreport

    if callback.from_user.id not in sett.get("config")["telegram"]["bot"]["signed_users"]:
        return await answer_callback(callback.bot, callback)

    errors = bootreport.get_errors()
    if callback_data.boot != bootreport.boot_id or callback_data.idx >= len(errors):
        return await notify(callback, "Этот отчёт от прошлого запуска бота — ошибки в нём уже неактуальны", alert=True)

    error = errors[callback_data.idx]
    content = f"Модуль: {error['module']}\nЭтап: {error['stage']}\n\n{error['trace']}"
    await callback.bot.send_document(
        chat_id=callback.from_user.id,
        document=BufferedInputFile(content.encode("utf-8"), filename=f"{error['module']}_error.txt"),
        reply_markup=templ.destroy_kb()
    )
    await answer_callback(callback.bot, callback)


@router.callback_query(calls.BootModuleDisable.filter())
async def callback_boot_module_disable(callback: CallbackQuery, callback_data: calls.BootModuleDisable):
    from core import bootreport
    from core.modules import get_modules, disable_module, set_module_disabled

    if callback.from_user.id not in sett.get("config")["telegram"]["bot"]["signed_users"]:
        return await answer_callback(callback.bot, callback)

    errors = bootreport.get_errors()
    if callback_data.boot != bootreport.boot_id or callback_data.idx >= len(errors):
        return await notify(callback, "Этот отчёт от прошлого запуска бота — ошибки в нём уже неактуальны", alert=True)

    name = errors[callback_data.idx]["module"]
    module = next((m for m in get_modules() if m._dir_name == name), None)
    if not module:
        return await notify(callback, f"Модуль {name} не загружен", alert=True)

    if module.enabled:
        await disable_module(module.uuid)
    set_module_disabled(name, True)
    await notify(callback, f"🔴 Модуль {name} выключен и не будет включаться при запуске. Включить обратно можно на его странице в «Модулях»", alert=True)
