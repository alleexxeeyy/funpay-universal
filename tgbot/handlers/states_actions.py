from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import states
from ..helpful import throw_float_message


router = Router()


@router.message(states.ActionsStates.waiting_for_message_text, F.text)
async def handler_waiting_for_message_text(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        from fpbot.funpaybot import get_funpay_bot

        data = await state.get_data()
        fpbot = get_funpay_bot()
        chat_name = data.get("chat_name")
        chat = fpbot.funpay_account.get_chat_by_name(chat_name, True)
        fpbot.send_message(chat_id=chat.id, text=message.text.strip())
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(f"✅ Пользователю <b>{chat_name}</b> было отправлено сообщение: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e), 
            reply_markup=templ.destroy_kb()
        )


@router.message(states.ActionsStates.waiting_for_review_answer_text, F.text)
async def handler_waiting_for_review_answer_text(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        from fpbot.funpaybot import get_funpay_bot

        data = await state.get_data()
        order_id = data.get("order_id")
        get_funpay_bot().funpay_account.send_review(order_id=order_id, text=message.text.strip())
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(f"✅ На отзыв по заказу <code>#{order_id}</code> был отправлен ответ: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e), 
            reply_markup=templ.destroy_kb()
        )