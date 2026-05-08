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