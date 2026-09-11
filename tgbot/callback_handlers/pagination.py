import math
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import asyncio

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message


router = Router()


async def render_custom_commands(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state, message, templ.comms_text(), templ.comms_kb(page), callback
    )


@router.callback_query(calls.CustomCommandsPagination.filter())
async def callback_custom_commands_pagination(callback: CallbackQuery, callback_data: calls.CustomCommandsPagination, state: FSMContext):
    await state.set_state(None)
    await render_custom_commands(callback.message, state, callback_data.page, callback)


async def render_auto_deliveries(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state, message, templ.delivs_text(), templ.delivs_kb(page), callback
    )


@router.callback_query(calls.AutoDeliveriesPagination.filter())
async def callback_auto_delivery_pagination(callback: CallbackQuery, callback_data: calls.AutoDeliveriesPagination, state: FSMContext):
    await state.set_state(None)
    await render_auto_deliveries(callback.message, state, callback_data.page, callback)


async def render_messages(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state, message, templ.mess_text(), templ.mess_kb(page), callback
    )


@router.callback_query(calls.MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: calls.MessagesPagination, state: FSMContext):
    await state.set_state(None)
    await render_messages(callback.message, state, callback_data.page, callback)


async def render_modules(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state, message, templ.modules_text(), templ.modules_kb(page), callback
    )


@router.callback_query(calls.ModulesPagination.filter())
async def callback_modules_pagination(callback: CallbackQuery, callback_data: calls.ModulesPagination, state: FSMContext):
    await state.set_state(None)
    await render_modules(callback.message, state, callback_data.page, callback)


async def render_fast_replies(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.fast_replies_text(),
        reply_markup=templ.fast_replies_kb(page),
        callback=callback
    )


@router.callback_query(calls.FastRepliesPagination.filter())
async def callback_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.FastRepliesPagination, state: FSMContext):
    await state.set_state(None)
    await render_fast_replies(callback.message, state, callback_data.page, callback)


async def render_fast_sel_fast_reply(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    data = await state.get_data()
    chat_name = data.get("fast_reply_chat_name")
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
        reply_markup=templ.fast_sel_fast_reply_kb(chat_name, page),
        callback=callback
    )


@router.callback_query(calls.FastSelFastReplyPagination.filter())
async def callback_fast_sel_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.FastSelFastReplyPagination, state: FSMContext):
    await state.set_state(None)
    await state.update_data(fast_reply_chat_name=callback_data.id)
    await render_fast_sel_fast_reply(callback.message, state, callback_data.page, callback)


async def render_signed_users(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.signed_users_text(),
        reply_markup=await templ.signed_users_kb(page),
        callback=callback
    )


@router.callback_query(calls.SignedUsersPagination.filter())
async def callback_signed_users_pagination(callback: CallbackQuery, callback_data: calls.SignedUsersPagination, state: FSMContext):
    await state.set_state(None)
    await render_signed_users(callback.message, state, callback_data.page, callback)


async def render_chats(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        await state.update_data(last_page=page)

        data = await state.get_data()
        chats = data.get("chats") or []

        if upd or not chats:
            await throw_float_message(state, message, "⌛️")
            from fpbot.funpaybot import get_funpay_bot as fpbot
            chats = fpbot().account.request_chats()
            await state.update_data(chats=chats)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.chats_text(chats, page),
            reply_markup=templ.chats_kb(chats, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.chats_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.ChatsPagination.filter())
async def callback_chats_pagination(callback: CallbackQuery, callback_data: calls.ChatsPagination, state: FSMContext):
    await state.set_state(None)
    await render_chats(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


async def render_sel_fast_reply(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    data = await state.get_data()
    chat_id = data.get("fast_reply_chat_id")
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
        reply_markup=templ.sel_fast_reply_kb(chat_id, page),
        callback=callback
    )


@router.callback_query(calls.SelFastReplyPagination.filter())
async def callback_sel_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.SelFastReplyPagination, state: FSMContext):
    await state.set_state(None)
    await state.update_data(fast_reply_chat_id=callback_data.id)
    await render_sel_fast_reply(callback.message, state, callback_data.page, callback)


async def render_lots(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        await state.update_data(last_page=page)

        data = await state.get_data()
        lots = data.get("lots") or []

        if upd or not lots:
            await throw_float_message(state, message, "⌛️")
            from fpbot.funpaybot import get_funpay_bot as fpbot
            acc = fpbot().account
            profile = acc.get_user(acc.id)
            lots = profile.get_lots()
            await state.update_data(lots=lots)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.lots_text(lots, page),
            reply_markup=templ.lots_kb(lots, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.lots_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.LotsPagination.filter())
async def callback_lots_pagination(callback: CallbackQuery, callback_data: calls.LotsPagination, state: FSMContext):
    await state.set_state(None)
    await render_lots(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


async def render_reviews(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        await state.update_data(last_page=page)

        data = await state.get_data()
        reviews = data.get("reviews") or []

        if upd or not reviews:
            await throw_float_message(state, message, "⌛️")
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
            message=message,
            text=templ.reviews_text(reviews, page),
            reply_markup=templ.reviews_kb(reviews, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.reviews_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.ReviewsPagination.filter())
async def callback_reviews_pagination(callback: CallbackQuery, callback_data: calls.ReviewsPagination, state: FSMContext):
    await state.set_state(None)
    await render_reviews(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


MAX_PAGE_LOAD_REQUESTS = 10


async def load_cursor_list(state: FSMContext, message: Message, key: str, page: int, fetch, reset: bool = False) -> list:
    data = await state.get_data()
    objects = [] if reset else (data.get(key) or [])
    next_id = None if reset else data.get(f"{key}_next_id")
    is_all_loaded = False if reset else (data.get(f"is_all_{key}_loaded") or False)

    requests = 0
    while not is_all_loaded and len(objects) < (page + 1) * 12 + 1 and requests < MAX_PAGE_LOAD_REQUESTS:
        if requests == 0:
            await throw_float_message(state, message, "⌛️")

        batch, next_id = await asyncio.to_thread(fetch, next_id)
        objects.extend(batch or [])
        if len(batch or []) < 24 or not next_id:
            is_all_loaded = True
        requests += 1

    if requests:
        await state.update_data(**{
            key: objects,
            f"{key}_next_id": next_id,
            f"is_all_{key}_loaded": is_all_loaded
        })
    return objects


async def render_orders(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        data = await state.get_data()
        orders_filter = data.get("orders_filter")
        last_filter = data.get("last_orders_filter")
        if not orders_filter:
            orders_filter = {"statuses": []}
            await state.update_data(orders_filter=orders_filter)
        await state.update_data(last_orders_filter=orders_filter.copy())
        filter_updated = orders_filter != last_filter

        state_filter = orders_filter["statuses"] or None
        include_paid = True
        include_closed = True
        include_refunded = True
        if state_filter:
            include_paid = "paid" in state_filter
            include_closed = "closed" in state_filter
            include_refunded = "refunded" in state_filter

        from fpbot.funpaybot import get_funpay_bot as fpbot

        def fetch(next_id):
            next_id, sales, _loc, _subcats = fpbot().account.get_sales(
                start_from=next_id,
                include_paid=include_paid,
                include_closed=include_closed,
                include_refunded=include_refunded,
            )
            return sales, next_id

        orders = await load_cursor_list(state, message, "orders", page, fetch, reset=upd or filter_updated)
        page = min(page, max(math.ceil(len(orders) / 12), 1) - 1)
        await state.update_data(last_page=page)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.orders_text(orders, page),
            reply_markup=templ.orders_kb(orders, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.orders_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.OrdersPagination.filter())
async def callback_orders_pagination(callback: CallbackQuery, callback_data: calls.OrdersPagination, state: FSMContext):
    await state.set_state(None)
    await render_orders(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


async def render_releases(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    from updater import get_cached_releases

    await state.update_data(rel_last_page=page)

    try:
        releases = await asyncio.to_thread(get_cached_releases)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.releases_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="updates").pack()),
            callback=callback
        )
        return

    await throw_float_message(
        state=state,
        message=message,
        text=templ.releases_text(releases),
        reply_markup=templ.releases_kb(releases, page),
        callback=callback
    )


@router.callback_query(calls.ReleasesPagination.filter())
async def callback_releases_pagination(callback: CallbackQuery, callback_data: calls.ReleasesPagination, state: FSMContext):
    await state.set_state(None)
    await render_releases(callback.message, state, callback_data.page, callback)


PAGES = {
    "custom_commands": (render_custom_commands, templ.comms_float_text),
    "auto_deliveries": (render_auto_deliveries, templ.delivs_float_text),
    "messages": (render_messages, templ.mess_float_text),
    "modules": (render_modules, templ.modules_float_text),
    "fast_replies": (render_fast_replies, templ.fast_replies_float_text),
    "fast_sel_fast_reply": (render_fast_sel_fast_reply, templ.do_action_text),
    "signed_users": (render_signed_users, templ.signed_users_float_text),
    "chats": (render_chats, templ.chats_float_text),
    "sel_fast_reply": (render_sel_fast_reply, templ.do_action_text),
    "lots": (render_lots, templ.lots_float_text),
    "reviews": (render_reviews, templ.reviews_float_text),
    "orders": (render_orders, templ.orders_float_text),
    "releases": (render_releases, templ.releases_float_text)
}


@router.callback_query(calls.PageEnter.filter())
async def callback_page_enter(callback: CallbackQuery, callback_data: calls.PageEnter, state: FSMContext):
    enter = callback_data.model_dump()
    enter["state"] = await state.get_state()
    await state.update_data(page_enter=enter)
    await state.set_state(states.PageStates.waiting_for_page)

    _, float_text = PAGES[callback_data.to]
    pages_range = f" (1–{callback_data.total})" if callback_data.total else ""
    await throw_float_message(
        state=state,
        message=callback.message,
        text=float_text(f"📃 Введите <b>номер страницы</b> для перехода{pages_range}:"),
        reply_markup=templ.back_kb(calls.PageBack(to=callback_data.to, page=callback_data.page).pack()),
        callback=callback
    )


@router.callback_query(calls.PageBack.filter())
async def callback_page_back(callback: CallbackQuery, callback_data: calls.PageBack, state: FSMContext):
    if await state.get_state() == states.PageStates.waiting_for_page:
        data = await state.get_data()
        await state.set_state(data["page_enter"]["state"])

    render, _ = PAGES[callback_data.to]
    await render(callback.message, state, callback_data.page, callback)
