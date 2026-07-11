from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from tempfile import NamedTemporaryFile
import os
import asyncio

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..callback_handlers.page import callback_chat_page, callback_order_page, callback_lot_page, callback_review_page
from ..helpful import throw_float_message


router = Router()


async def _send_mess(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")

    from fpbot.funpaybot import get_funpay_bot as fpbot
    acc = fpbot().account

    sent_msg = ""

    text = None
    if message.text:
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")
        text = message.text.strip()
        sent_msg += text

    photo_paths = []
    if message.photo:
        data = await state.get_data()
        photos_messages = data.get("album_messages", []) + [message]

        for msg in photos_messages:
            photo = msg.photo[-1]
            with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                await message.bot.download(photo, destination=tmp.name)
                photo_paths.append(tmp.name)

        if message.caption:
            text = message.caption.strip()
            sent_msg += message.caption.strip()

        sent_msg += f", <b>Изображения ({len(photo_paths)})</b>" if text else f"<b>Изображения ({len(photo_paths)})</b>"

    if text:
        acc.send_message(chat_id, text)
        if photo_paths:
            await asyncio.sleep(0.5)

    for path in photo_paths:
        try:
            acc.send_image(chat_id, path)
            await asyncio.sleep(0.5)
        finally:
            try: os.remove(path)
            except: pass

    await state.update_data(album_messages=[])

    return acc, chat_id, sent_msg


@router.message(states.FunPayStates.waiting_for_chat_message, F.text | F.photo)
async def handler_waiting_for_chat_message(message: types.Message, state: FSMContext):
    try:
        if message.media_group_id:
            data = await state.get_data()
            album = data.get("album_messages", []) + [message]
            await state.update_data(album_messages=album)
            await throw_float_message(state, message, "⌛️")
            return

        await state.set_state(None)
        await throw_float_message(state, message, "⌛️")

        data = await state.get_data()
        chat_id = data.get("chat_id")
        chat = data.get("chat")
        callback = data.get("callback")
        if not chat_id:
            raise Exception("❌ Чат не найден")

        _, _, sent_msg = await _send_mess(message, state)

        if callback is not None:
            await callback_chat_page(callback, calls.ChatPage(id=str(chat_id)), state)
        else:
            await throw_float_message(
                state=state,
                message=message,
                text=templ.do_action_text(
                    f"✅ Сообщение отправлено: <blockquote>{sent_msg}</blockquote>"
                ),
                reply_markup=templ.back_kb(calls.ChatPage(id=str(chat_id)).pack())
            )
    except Exception as e:
        data = await state.get_data()
        chat_id = data.get("chat_id")
        chat = data.get("chat")
        back = calls.ChatPage(id=str(chat_id)).pack() if chat_id else calls.ChatsPagination(page=0).pack()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.chat_float_text(chat, e),
            reply_markup=templ.back_kb(back)
        )


@router.message(states.FunPayStates.waiting_for_order_review_answer, F.text)
async def handler_waiting_for_order_review_answer(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, message, "⌛️")

        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        order_id = data.get("order_id")
        callback = data.get("callback")
        from_review = data.get("from_review", False)
        if not order_id:
            raise Exception("❌ Заказ не найден")

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        acc.send_review(order_id, message.text.strip())

        if callback is not None:
            if from_review:
                await callback_review_page(callback, calls.ReviewPage(id=str(order_id)), state)
            else:
                await callback_order_page(callback, calls.OrderPage(id=str(order_id)), state)
        else:
            back = calls.ReviewPage(id=str(order_id)) if from_review else calls.OrderPage(id=str(order_id))
            await throw_float_message(
                state=state,
                message=message,
                text=templ.do_action_text(f"✅ Ответ на отзыв <b>отправлен</b>"),
                reply_markup=templ.back_kb(back.pack())
            )
    except Exception as e:
        data = await state.get_data()
        order_id = data.get("order_id")
        from_review = data.get("from_review", False)
        if from_review:
            back = calls.ReviewPage(id=str(order_id)).pack() if order_id else calls.ReviewsPagination(page=0).pack()
        else:
            back = calls.OrderPage(id=str(order_id)).pack() if order_id else calls.OrdersPagination(page=0).pack()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.order_float_text(e),
            reply_markup=templ.back_kb(back)
        )


@router.message(states.FunPayStates.waiting_for_lot_price, F.text)
async def handler_waiting_for_lot_price(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, message, "⌛️")

        text = message.text.strip().replace(",", ".")
        try:
            price = float(text)
        except ValueError:
            raise Exception("❌ Неверный формат цены")

        data = await state.get_data()
        lot_id = data.get("lot_id")
        callback = data.get("callback")
        if not lot_id:
            raise Exception("❌ Лот не найден")

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        lf = acc.get_lot_fields(int(lot_id))
        lf.price = price
        acc.save_lot(lf)

        if callback is not None:
            await callback_lot_page(callback, calls.LotPage(id=str(lot_id)), state)
        else:
            await throw_float_message(
                state=state,
                message=message,
                text=templ.do_action_text(f"✅ Цена <b>обновлена</b>: {price}"),
                reply_markup=templ.back_kb(calls.LotPage(id=str(lot_id)).pack())
            )
    except Exception as e:
        data = await state.get_data()
        lot_id = data.get("lot_id")
        back = calls.LotPage(id=str(lot_id)).pack() if lot_id else calls.LotsPagination(page=0).pack()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.lot_float_text(e),
            reply_markup=templ.back_kb(back)
        )


@router.message(states.FunPayStates.waiting_for_lot_description, F.text)
async def handler_waiting_for_lot_description(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, message, "⌛️")

        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        lot_id = data.get("lot_id")
        callback = data.get("callback")
        if not lot_id:
            raise Exception("❌ Лот не найден")

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        lf = acc.get_lot_fields(int(lot_id))
        locale = lf.subcategory and lf.subcategory.category and "en"
        if locale == "en":
            lf.description_en = message.text.strip()
        else:
            lf.description_ru = message.text.strip()
        acc.save_lot(lf)

        if callback is not None:
            await callback_lot_page(callback, calls.LotPage(id=str(lot_id)), state)
        else:
            await throw_float_message(
                state=state,
                message=message,
                text=templ.do_action_text(f"✅ Описание <b>обновлено</b>"),
                reply_markup=templ.back_kb(calls.LotPage(id=str(lot_id)).pack())
            )
    except Exception as e:
        data = await state.get_data()
        lot_id = data.get("lot_id")
        back = calls.LotPage(id=str(lot_id)).pack() if lot_id else calls.LotsPagination(page=0).pack()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.lot_float_text(e),
            reply_markup=templ.back_kb(back)
        )


# ===== Авто-вывод =====

@router.message(states.FunPayStates.waiting_for_withdrawal_interval, F.text)
async def handler_waiting_for_withdrawal_interval(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        interval = int(message.text.strip())
        if interval < 60:
            raise Exception("❌ Минимум 60 секунд")

        from settings import Settings as sett
        config = sett.get("config")
        config["funpay"]["auto_withdrawal"]["interval"] = interval
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.withdrawal_float_text(f"✅ Интервал <b>успешно изменён</b>: {interval} сек."),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.withdrawal_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
        )


@router.message(states.FunPayStates.waiting_for_withdrawal_address, F.text)
async def handler_waiting_for_withdrawal_address(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        address = message.text.strip()
        if len(address) < 3:
            raise Exception("❌ Слишком короткие реквизиты")

        from settings import Settings as sett
        config = sett.get("config")
        config["funpay"]["auto_withdrawal"]["address"] = address
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.withdrawal_float_text(f"✅ Реквизиты <b>успешно изменены</b>: {address}"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.withdrawal_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
        )


@router.message(states.FunPayStates.waiting_for_withdrawal_amount_value, F.text)
async def handler_waiting_for_withdrawal_amount_value(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        text = message.text.strip().replace(",", ".")
        try:
            amount = float(text)
        except ValueError:
            raise Exception("❌ Вы должны ввести числовое значение")
        if amount <= 0:
            raise Exception("❌ Сумма должна быть больше 0")

        from settings import Settings as sett
        config = sett.get("config")
        config["funpay"]["auto_withdrawal"]["amount"] = amount
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.withdrawal_float_text(f"✅ Сумма <b>успешно изменена</b>: {amount}"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.withdrawal_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
        )
