from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .navigation import *
from .page import callback_module_page
from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message


router = Router()


@router.callback_query(F.data == "destroy")
async def callback_destroy(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(F.data == "clean_proxy")
async def callback_clean_proxy(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["api"]["proxy"] = ""
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="conn"), state)


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
            text=templ.settings_new_deliv_float_text(
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
            text=templ.settings_new_deliv_float_text(e), 
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
                f"💬 Введите <b>сообщение</b> для отправки <b>{chat_name}</b> ↓"
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
                f"✔️ Подтвердите <b>возврат</b> заказа "
                f'<b><a href="https://funpay.com/orders/{order_id}/?">#{order_id}</a></b> ↓'
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
                f"💬🌟 Введите <b>ответ</b> на отзыв по заказу "
                f'<b><a href="https://funpay.com/orders/{order_id}/?">#{order_id}</a></b> ↓'
            ), 
            reply_markup=templ.destroy_kb(),
            callback=callback,
            send=True
        )


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
            f"✅ По заказу <code>#{order_id}</code> был оформлен возврат"
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