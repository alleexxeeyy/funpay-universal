from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message, do_auth

from settings import Settings as sett


router = Router()


@router.callback_query(calls.MenuNavigation.filter())
async def callback_menu_navigation(callback: CallbackQuery, callback_data: calls.MenuNavigation, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    if callback.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(callback.message, state)

    await state.set_state(None)
    to = callback_data.to
    
    if to == "default":
        await throw_float_message(
            state, callback.message, templ.menu_text(), templ.menu_kb(), callback
        )
    elif to == "events":
        await throw_float_message(
            state, callback.message, templ.events_text(), templ.events_kb(), callback
        )
    elif to == "stats":
        await throw_float_message(
            state, callback.message, templ.stats_text(), templ.stats_kb(), callback
        )
    elif to == "profile":
        await throw_float_message(
            state, callback.message, templ.profile_text(), templ.profile_kb(), callback
        )
    elif to == "logs":
        await throw_float_message(
            state, callback.message, templ.logs_text(), templ.logs_kb(), callback
        )
    elif to == "updates":
        await throw_float_message(
            state, callback.message, templ.updates_text(), templ.updates_kb(), callback
        )

    elif to == "auth":
        await throw_float_message(
            state, callback.message, templ.auth_text(), templ.auth_kb(), callback
        )
    elif to == "conn":
        await throw_float_message(
            state, callback.message, templ.conn_text(), templ.conn_kb(), callback
        )
    elif to == "lots":
        await throw_float_message(
            state, callback.message, templ.lots_text(), templ.lots_kb(), callback
        )
    elif to == "notifications":
        await throw_float_message(
            state, callback.message, templ.notifications_text(), templ.notifications_kb(), callback
        )
    elif to == "tickets":
        await throw_float_message(
            state, callback.message, templ.tickets_text(), templ.tickets_kb(), callback
        )
    elif to == "withdrawal":
        await throw_float_message(
            state, callback.message, templ.withdrawal_text(), templ.withdrawal_kb(), callback
        )
    elif to == "other":
        await throw_float_message(
            state, callback.message, templ.other_text(), templ.other_kb(), callback
        )


@router.callback_query(calls.StatsNavigation.filter())
async def callback_stats_navigation(callback: CallbackQuery, callback_data: calls.StatsNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    
    await throw_float_message(
        state, callback.message, templ.stats_text(to), templ.stats_kb(to), callback
    )


@router.callback_query(calls.PlaceholdersNavigation.filter())
async def callback_placeholders_navigation(callback: CallbackQuery, callback_data: calls.PlaceholdersNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    by = callback_data.by

    data = await state.get_data()
    last_page = data.get("last_page", 0)

    await throw_float_message(
        state, callback.message, templ.plholders_text(to), templ.plholders_kb(to, by, last_page), callback
    )