from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from pathlib import Path
from collections import deque
import shutil
import os

from settings import Settings as sett

from .navigation import *
from .pagination import *
from .page import callback_module_page
from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message, do_auth


router = Router()


@router.callback_query(F.data == "destroy")
async def callback_destroy(callback: CallbackQuery):
    await callback.message.delete()

@router.callback_query(F.data == "null_answer")
async def callback_null_answer(callback: CallbackQuery):
    await callback.bot.answer_callback_query(callback.id)


@router.callback_query(calls.DeleteSignedUser.filter())
async def callback_delete_signed_user(callback: CallbackQuery, callback_data: calls.DeleteSignedUser, state: FSMContext):
    try:
        await state.set_state(None)
        id = callback_data.id

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        config = sett.get("config")
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


@router.callback_query(F.data == "change_password")
async def callback_change_password(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    new_password = data.get("new_password")
    
    config = sett.get("config")
    config["telegram"]["bot"]["password"] = new_password
    config["telegram"]["bot"]["signed_users"] = [callback.from_user.id]
    sett.set("config", config)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.signed_users_float_text(f"✅ Пароль <b>успешно изменён</b>"),
        reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack()),
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