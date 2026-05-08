from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from tempfile import NamedTemporaryFile
import os
import asyncio

from .. import templates as templ
from .. import states
from ..helpful import throw_float_message


router = Router()


async def _send_mess(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")

    data = await state.get_data()
    chat_name = data.get("chat_name")

    from fpbot.funpaybot import get_funpay_bot as fpbot
    acc = fpbot().account
    
    chat = acc.get_chat_by_name(chat_name, True)
    
    sent_msg = ""
    
    if message.text:
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")
            
        acc.send_message(chat.id, message.text.strip())
    
    elif message.photo:
        photo = message.photo[-1]
        with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            await message.bot.download(photo, destination=tmp.name)
            tmp_path = tmp.name

        if message.caption:
            fpbot.send_message(chat.id, message.caption.strip())
            sent_msg += f"{message.caption.strip()}, "
            await asyncio.sleep(0.5)

        acc.send_image(chat.id, tmp_path)
        os.remove(tmp_path)
        sent_msg += f"<b>Изображение</b>"

    return acc, chat, sent_msg


@router.message(states.ActionsStates.waiting_for_fast_answer_message, F.text | F.photo)
async def handler_waiting_for_fast_answer_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, message, "⌛")

        _, _, sent_msg = await _send_mess(message, state)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(
                f"✅ Сообщение отправлено: <blockquote>{sent_msg}</blockquote>"
            ),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )


@router.message(states.ActionsStates.waiting_for_fast_review_answer, F.text)
async def handler_waiting_for_fast_review_answer(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        await throw_float_message(state, message, "⌛")

        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        data = await state.get_data()
        order_id = data.get("order_id")

        acc.send_review(order_id, message.text.strip())
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(f"✅ На отзыв <b>отправлен ответ</b>: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e), 
            reply_markup=templ.destroy_kb()
        )