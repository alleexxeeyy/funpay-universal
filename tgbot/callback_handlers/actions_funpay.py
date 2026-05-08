from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message

from .navigation import *
from .pagination import *
from .page import *


router = Router()


@router.callback_query(calls.FastSendFastReply.filter())
async def callback_fast_send_fast_reply(callback: CallbackQuery, callback_data: calls.FastSendFastReply, state: FSMContext):
    try:
        await state.set_state(None)

        chat_name = callback_data.name
        index = callback_data.index

        fast_replies = sett.get("fast_replies")
        reply_text = fast_replies[index]

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        chat = acc.get_chat_by_name(chat_name, True)
        acc.send_message(chat.id, reply_text)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(
                f"✅ Быстрое сообщение <b>успешно отправлено</b>: <blockquote>{reply_text}</blockquote>"
            ),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )


@router.callback_query(calls.FastRefundOrder.filter())
async def callback_fast_refund_order(callback: CallbackQuery, callback_data: calls.FastRefundOrder, state: FSMContext):
    try:
        await state.set_state(None)
        
        order_id = callback_data.id

        from fpbot.funpaybot import get_funpay_bot as fpbot
        fpbot().acc.refund(order_id)

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text("✅ Успешно оформлен <b>возврат заказа</b>"),
            reply_markup=templ.destroy_kb(),
            reply_to=callback.message.message_id
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb(),
            reply_to=callback.message.message_id
        )