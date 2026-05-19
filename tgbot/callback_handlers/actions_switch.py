from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from settings import Settings as sett

from .navigation import *
from .page import callback_message_page, callback_module_page
from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message


router = Router()


@router.callback_query(F.data == "switch_notifications_enabled")
async def callback_switch_notifications_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["notifications"]["enabled"] = not config["funpay"]["notifications"]["enabled"]
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data.contains("switch_notifications_event"))
async def callback_switch_notifications_event(callback: CallbackQuery, state: FSMContext):
    event = str(callback.data).split("switch_notifications_event_")[1]
    config = sett.get("config")
    config["funpay"]["notifications"]["events"][event] = not config["funpay"]["notifications"]["events"][event]
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_auto_raise_lots_enabled")
async def callback_switch_auto_raise_lots_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["auto_raise_lots"] = not config["funpay"]["auto_raise_lots"]
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="other"), state
    )


@router.callback_query(F.data == "switch_auto_review_replies_enabled")
async def callback_switch_auto_review_replies_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["auto_review_replies"] = not config["funpay"]["auto_review_replies"]
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="other"), state
    )


@router.callback_query(F.data == "switch_watermark_enabled")
async def callback_switch_watermark_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["watermark"]["enabled"] = not config["funpay"]["watermark"]["enabled"]
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="other"), state
    )


@router.callback_query(F.data == "switch_auto_raise_lots_enabled")
async def callback_switch_auto_raise_lots_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["auto_raise_lots"]["enabled"] = not config["funpay"]["auto_raise_lots"]["enabled"]
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="lots"), state
    )


@router.callback_query(F.data == "switch_auto_raise_lots_all")
async def callback_switch_auto_raise_lots_all(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["auto_raise_lots"]["all"] = not config["funpay"]["auto_raise_lots"]["all"]
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="lots"), state
    )


@router.callback_query(F.data == "switch_auto_tickets_enabled")
async def callback_switch_auto_tickets_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["funpay"]["auto_tickets"]["enabled"] = not config["funpay"]["auto_tickets"]["enabled"]
    sett.set("config", config)
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="tickets"), state
    )


@router.callback_query(F.data == "switch_updates_auto_update")
async def callback_switch_updates_auto_update(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["updates"]["auto_update"] = not config["updates"]["auto_update"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="updates"), state
    )


@router.callback_query(F.data == "switch_updates_notify")
async def callback_switch_updates_notify(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["updates"]["notify"] = not config["updates"]["notify"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="updates"), state
    )


@router.callback_query(F.data == "switch_message_enabled")
async def callback_switch_message_enabled(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        messages = sett.get("messages")
        messages[message_id]["enabled"] = not messages[message_id]["enabled"]
        sett.set("messages", messages)
        
        return await callback_message_page(
            callback, calls.MessagePage(message_id=message_id), state
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.mess_float_text(e), 
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "switch_module_enabled")
async def callback_switch_module_enabled(callback: CallbackQuery, state: FSMContext):
    from core.modules import get_module_by_uuid, disable_module, enable_module
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("❌ UUID модуля не был найден, повторите процесс с самого начала")
        
        module = get_module_by_uuid(module_uuid)
        if not module:
            raise Exception("❌ Модуль с этим UUID не был найден, повторите процесс с самого начала")

        await disable_module(module_uuid) if module.enabled else await enable_module(module_uuid)
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