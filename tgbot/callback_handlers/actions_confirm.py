from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .navigation import *
from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message


router = Router()


@router.callback_query(F.data == "confirm_deleting_custom_command")
async def callback_confirm_deleting_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(
                f"🗑️ Подтвердите <b>удаление команды</b> <code>{custom_command}</code>"
            ), 
            reply_markup=templ.confirm_kb(confirm_cb="delete_custom_command", cancel_cb=calls.CustomCommandPage(command=custom_command).pack())
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


@router.callback_query(F.data == "confirm_creating_tickets")
async def callback_confirm_creating_tickets(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.events_float_text(
            "✔️ Подтвердите <b>создание тикетов на закрытие заказов</b> ↓"
        ), 
        reply_markup=templ.confirm_kb(confirm_cb="create_tickets", cancel_cb=calls.MenuNavigation(to="events").pack())
    )


@router.callback_query(F.data == "confirm_deleting_auto_delivery")
async def callback_confirm_deleting_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        lot_id = data.get("auto_delivery_lot_id")
        lot = data.get("auto_delivery_lot")
        if not lot_id:
            raise Exception("❌ ID лота авто-выдачи не был найден, повторите процесс с самого начала")
        
        try: lot_title = lot.title_ru
        except: lot_title = lot_id
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(
                f"🗑️ Подтвердите <b>удаление авто-выдачи</b> на лот "
                f'<a href="https://funpay.com/lots/offer?id={lot_id}">{lot_title}</a> ↓'
            ), 
            reply_markup=templ.confirm_kb(
                confirm_cb="delete_auto_delivery", 
                cancel_cb=calls.AutoDeliveryPage(lot_id=lot_id).pack()
            )
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