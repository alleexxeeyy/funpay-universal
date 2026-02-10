from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from tempfile import NamedTemporaryFile
import os
import asyncio

from .. import templates as templ
from .. import states
from ..helpful import throw_float_message


router = Router()


@router.message(states.ActionsStates.waiting_for_message_content, F.text | F.photo)
async def handler_waiting_for_message_text(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        await throw_float_message(state, message, "⌛")

        data = await state.get_data()
        chat_name = data.get("chat_name")

        from fpbot.funpaybot import get_funpay_bot
        fpbot = get_funpay_bot()
        chat = fpbot.funpay_account.get_chat_by_name(chat_name, True)
        
        sent_msg = ""
        
        if message.text:
            if len(message.text.strip()) <= 0:
                raise Exception("❌ Слишком короткий текст")
            fpbot.account.send_message(chat_id=chat.id, text=message.text.strip())
        
        elif message.photo:
            photo = message.photo[-1]
            with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                await message.bot.download(photo, destination=tmp.name)
                tmp_path = tmp.name

            if message.caption:
                fpbot.send_message(chat_id=chat.id, text=message.caption.strip())
                sent_msg += f"{message.caption.strip()}, "
                await asyncio.sleep(0.5)

            fpbot.account.send_image(chat_id=chat.id, image=tmp_path)
            os.remove(tmp_path)
            sent_msg += f"<b>Изображение</b>"
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(f"✅ Пользователю <b>{chat_name}</b> было отправлено сообщение: <blockquote>{sent_msg}</blockquote>"),
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
        await throw_float_message(state, message, "⌛")

        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        from fpbot.funpaybot import get_funpay_bot

        data = await state.get_data()
        order_id = data.get("order_id")

        fpbot = get_funpay_bot()
        fpbot.funpay_account.send_review(order_id=order_id, text=message.text.strip())
        
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