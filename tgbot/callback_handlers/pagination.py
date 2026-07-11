from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.callback_query(calls.CustomCommandsPagination.filter())
async def callback_custom_commands_pagination(callback: CallbackQuery, callback_data: calls.CustomCommandsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state, callback.message, templ.comms_text(), templ.comms_kb(page), callback
    )


@router.callback_query(calls.AutoDeliveriesPagination.filter())
async def callback_auto_delivery_pagination(callback: CallbackQuery, callback_data: calls.AutoDeliveriesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state, callback.message, templ.delivs_text(), templ.delivs_kb(page), callback
    )


@router.callback_query(calls.MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: calls.MessagesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state, callback.message, templ.mess_text(), templ.mess_kb(page), callback
    )


@router.callback_query(calls.ModulesPagination.filter())
async def callback_modules_pagination(callback: CallbackQuery, callback_data: calls.ModulesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state, callback.message, templ.modules_text(), templ.modules_kb(page), callback
    )


@router.callback_query(calls.FastRepliesPagination.filter())
async def callback_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.FastRepliesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.fast_replies_text(),
        reply_markup=templ.fast_replies_kb(page),
        callback=callback
    )


@router.callback_query(calls.FastSelFastReplyPagination.filter())
async def callback_fast_sel_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.FastSelFastReplyPagination, state: FSMContext):
    await state.set_state(None)
    
    chat_id = callback_data.id
    page = callback_data.page
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
        reply_markup=templ.fast_sel_fast_reply_kb(chat_id, page),
        callback=callback
    )


@router.callback_query(calls.SignedUsersPagination.filter())
async def callback_signed_users_pagination(callback: CallbackQuery, callback_data: calls.SignedUsersPagination, state: FSMContext):
    await state.set_state(None)

    page = callback_data.page
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.signed_users_text(),
        reply_markup=await templ.signed_users_kb(page),
        callback=callback
    )


@router.callback_query(calls.ChatsPagination.filter())
async def callback_chats_pagination(callback: CallbackQuery, callback_data: calls.ChatsPagination, state: FSMContext):
    try:
        await state.set_state(None)

        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        chats = data.get("chats") or []

        if upd or not chats:
            await throw_float_message(state, callback.message, "⌛️")
            from fpbot.funpaybot import get_funpay_bot as fpbot
            chats = fpbot().account.request_chats()
            await state.update_data(chats=chats)

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chats_text(chats, page),
            reply_markup=templ.chats_kb(chats, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chats_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.SelFastReplyPagination.filter())
async def callback_sel_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.SelFastReplyPagination, state: FSMContext):
    await state.set_state(None)

    chat_id = callback_data.id
    page = callback_data.page
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
        reply_markup=templ.sel_fast_reply_kb(chat_id, page),
        callback=callback
    )


@router.callback_query(calls.LotsPagination.filter())
async def callback_lots_pagination(callback: CallbackQuery, callback_data: calls.LotsPagination, state: FSMContext):
    try:
        await state.set_state(None)

        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        lots = data.get("lots") or []

        if upd or not lots:
            await throw_float_message(state, callback.message, "⌛️")
            from fpbot.funpaybot import get_funpay_bot as fpbot
            acc = fpbot().account
            profile = acc.get_user(acc.id)
            lots = profile.get_lots()
            await state.update_data(lots=lots)

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.lots_text(lots, page),
            reply_markup=templ.lots_kb(lots, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.lots_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.ReviewsPagination.filter())
async def callback_reviews_pagination(callback: CallbackQuery, callback_data: calls.ReviewsPagination, state: FSMContext):
    try:
        await state.set_state(None)

        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        reviews = data.get("reviews") or []

        if upd or not reviews:
            await throw_float_message(state, callback.message, "⌛️")
            from fpbot.funpaybot import get_funpay_bot as fpbot
            acc = fpbot().account

            reviews = []
            next_id = None
            order_ids = []
            while len(order_ids) < 48:
                next_id, sales, _loc, _sub = acc.get_sales(
                    start_from=next_id,
                    include_paid=True,
                    include_closed=True,
                    include_refunded=False,
                )
                order_ids.extend(s.id for s in sales)
                if not next_id or len(sales) < 24:
                    break

            for i in range(0, len(order_ids), 10):
                batch = order_ids[i:i+10]
                orders = acc.get_orders_by_ids(*batch, include_review=True)
                for oid, order in orders.items():
                    if order.review and (order.review.text or order.review.stars):
                        reviews.append(order.review)

            await state.update_data(reviews=reviews)

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.reviews_text(reviews, page),
            reply_markup=templ.reviews_kb(reviews, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.reviews_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.OrdersPagination.filter())
async def callback_orders_pagination(callback: CallbackQuery, callback_data: calls.OrdersPagination, state: FSMContext):
    try:
        await state.set_state(None)

        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        orders = data.get("orders") or []
        next_id = data.get("orders_next_id")
        is_all_loaded = data.get("is_all_orders_loaded") or False

        orders_filter = data.get("orders_filter")
        last_filter = data.get("last_orders_filter")
        if not orders_filter:
            orders_filter = {"statuses": []}
            await state.update_data(orders_filter=orders_filter)
        await state.update_data(last_orders_filter=orders_filter.copy())
        filter_updated = orders_filter != last_filter

        next_page_start = (page + 1) * 12
        need_more = len(orders) < next_page_start + 1

        if upd:
            next_id = None

        if (not is_all_loaded and need_more) or filter_updated or upd:
            await throw_float_message(state, callback.message, "⌛️")
            from fpbot.funpaybot import get_funpay_bot as fpbot
            acc = fpbot().account

            state_filter = orders_filter["statuses"] or None
            include_paid = True
            include_closed = True
            include_refunded = True
            if state_filter:
                include_paid = "paid" in state_filter
                include_closed = "closed" in state_filter
                include_refunded = "refunded" in state_filter

            next_id, sales, _loc, _subcats = acc.get_sales(
                start_from=next_id,
                include_paid=include_paid,
                include_closed=include_closed,
                include_refunded=include_refunded,
            )

            if filter_updated or upd:
                orders = sales
            else:
                orders.extend(sales)

            if len(sales) < 24:
                is_all_loaded = True

            await state.update_data(
                is_all_orders_loaded=is_all_loaded,
                orders_next_id=next_id,
                orders=orders,
                last_orders_filter=orders_filter.copy(),
            )

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.orders_text(orders, page),
            reply_markup=templ.orders_kb(orders, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.orders_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )