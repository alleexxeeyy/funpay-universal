from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.callback_query(calls.CustomCommandPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: calls.CustomCommandPage, state: FSMContext):
    await state.set_state(None)
    command = callback_data.command
    await state.update_data(custom_command=command)
    
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.comm_page_text(command), 
        reply_markup=templ.comm_page_kb(command, last_page), 
        callback=callback
    )


@router.callback_query(calls.AutoDeliveryPage.filter())
async def callback_auto_delivery_page(callback: CallbackQuery, callback_data: calls.AutoDeliveryPage, state: FSMContext):
    await state.set_state(None)
    
    from fpbot.funpaybot import get_funpay_bot
    lot_id = callback_data.lot_id
    try: lot = get_funpay_bot().account.get_lot_fields(lot_id)
    except: lot = None

    await state.update_data(
        auto_delivery_lot_id=lot_id,
        auto_delivery_lot=lot
    )
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.deliv_page_text(lot_id, lot), 
        reply_markup=templ.deliv_page_kb(lot_id, lot, last_page), 
        callback=callback
    )
    

@router.callback_query(calls.MessagePage.filter())
async def callback_message_page(callback: CallbackQuery, callback_data: calls.MessagePage, state: FSMContext):
    await state.set_state(None)
    message_id = callback_data.message_id
    await state.update_data(message_id=message_id)
    
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.mess_page_text(message_id), 
        reply_markup=templ.mess_page_kb(message_id, last_page), 
        callback=callback
    )


@router.callback_query(calls.ModulePage.filter())
async def callback_module_page(callback: CallbackQuery, callback_data: calls.ModulePage, state: FSMContext):
    await state.set_state(None)
    module_uuid = callback_data.uuid
    await state.update_data(module_uuid=module_uuid)

    data = await state.get_data()
    last_page = data.get("last_page") or 0

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.module_page_text(module_uuid),
        reply_markup=templ.module_page_kb(module_uuid, last_page),
        callback=callback
    )


@router.callback_query(calls.ChatPage.filter())
async def callback_chat_page(callback: CallbackQuery, callback_data: calls.ChatPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")

        chat_id_raw = callback_data.id
        try:
            chat_id = int(chat_id_raw)
        except (ValueError, TypeError):
            chat_id = chat_id_raw
        await state.update_data(chat_id=chat_id, callback=callback)

        data = await state.get_data()
        last_page = data.get("last_page") or 0

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        chat = acc.get_chat(chat_id)
        await state.update_data(chat=chat)

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chat_text(chat),
            reply_markup=templ.chat_kb(chat, last_page),
            callback=callback
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        chat = data.get("chat")
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chat_float_text(chat, e),
            reply_markup=templ.back_kb(calls.ChatsPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(calls.OrderPage.filter())
async def callback_order_page(callback: CallbackQuery, callback_data: calls.OrderPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")

        order_id = callback_data.id
        await state.update_data(order_id=order_id, callback=callback)

        data = await state.get_data()
        last_page = data.get("last_page") or 0

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        order = acc.get_order(order_id)
        await state.update_data(order=order)

        shortcut = next((o for o in (data.get("orders") or []) if str(o.id) == str(order_id)), None)
        order_date = shortcut.date if shortcut is not None else None

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.order_text(order, order_date),
            reply_markup=templ.order_kb(order, last_page),
            callback=callback
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        order = data.get("order")
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.order_float_text(e),
            reply_markup=templ.back_kb(calls.OrdersPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(calls.LotPage.filter())
async def callback_lot_page(callback: CallbackQuery, callback_data: calls.LotPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")

        lot_id = callback_data.id
        await state.update_data(lot_id=lot_id, callback=callback)

        data = await state.get_data()
        last_page = data.get("last_page") or 0

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        lf = acc.get_lot_fields(int(lot_id))
        await state.update_data(lot_fields=lf)

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.lot_text(lf),
            reply_markup=templ.lot_kb(lf, last_page),
            callback=callback
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.lot_float_text(e),
            reply_markup=templ.back_kb(calls.LotsPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(calls.ReviewPage.filter())
async def callback_review_page(callback: CallbackQuery, callback_data: calls.ReviewPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")

        review_id = callback_data.id
        await state.update_data(order_id=review_id, callback=callback)

        data = await state.get_data()
        last_page = data.get("last_page") or 0

        review = next((r for r in (data.get("reviews") or []) if str(r.order_id) == str(review_id)), None)

        if review is None:
            from fpbot.funpaybot import get_funpay_bot as fpbot
            acc = fpbot().account
            order = acc.get_order(review_id, include_review=True)
            review = order.review

        if review is None:
            raise Exception("Отзыв не найден")

        await state.update_data(review=review)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.review_text(review),
            reply_markup=templ.review_kb(review, last_page),
            callback=callback
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.review_float_text(e),
            reply_markup=templ.back_kb(calls.ReviewsPagination(page=last_page).pack()),
            callback=callback
        )