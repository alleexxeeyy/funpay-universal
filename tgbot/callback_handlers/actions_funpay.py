from aiogram import F, Router
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
        fpbot().account.refund(order_id)

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


@router.callback_query(calls.SendFastReply.filter())
async def callback_send_fast_reply(callback: CallbackQuery, callback_data: calls.SendFastReply, state: FSMContext):
    try:
        await state.set_state(None)

        chat_id = int(callback_data.id)
        index = callback_data.index

        fast_replies = sett.get("fast_replies")
        reply_text = fast_replies[index]

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        acc.send_message(chat_id, reply_text)

        await callback_chat_page(callback, calls.ChatPage(id=str(chat_id)), state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )


@router.callback_query(F.data == "enter_chat_message")
async def callback_enter_chat_message(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.FunPayStates.waiting_for_chat_message)
    await state.update_data(callback=callback)
    data = await state.get_data()
    chat_id = data.get("chat_id")
    chat = data.get("chat")

    if not chat_id:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chat_float_text(chat, "❌ Чат не найден, вернитесь в раздел чатов"),
            reply_markup=templ.back_kb(calls.ChatsPagination(page=0).pack()),
            callback=callback
        )
        return

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.chat_float_text(
            chat,
            "💬 Введите <b>текст сообщения</b> для ответа:"
            "\n\n🖼️ Вы также можете отправить <b>изображение</b>"
        ),
        reply_markup=templ.back_kb(calls.ChatPage(id=str(chat_id)).pack()),
        callback=callback
    )


@router.callback_query(calls.RefundOrder.filter())
async def callback_refund_order(callback: CallbackQuery, callback_data: calls.RefundOrder, state: FSMContext):
    try:
        await state.set_state(None)

        order_id = callback_data.id

        from fpbot.funpaybot import get_funpay_bot as fpbot
        fpbot().account.refund(order_id)

        await callback_order_page(callback, calls.OrderPage(id=order_id), state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.back_kb(calls.OrderPage(id=callback_data.id).pack())
        )


@router.callback_query(calls.AnswerOrderReview.filter())
async def callback_answer_order_review(callback: CallbackQuery, callback_data: calls.AnswerOrderReview, state: FSMContext):
    await state.set_state(states.FunPayStates.waiting_for_order_review_answer)
    await state.update_data(order_id=callback_data.id, callback=callback, from_review=False)

    data = await state.get_data()
    last_page = data.get("last_page") or 0

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.order_float_text("💬 Введите <b>ответ на отзыв</b>:"),
        reply_markup=templ.back_kb(calls.OrderPage(id=callback_data.id).pack()),
        callback=callback
    )


@router.callback_query(calls.DeleteOrderReview.filter())
async def callback_delete_order_review(callback: CallbackQuery, callback_data: calls.DeleteOrderReview, state: FSMContext):
    try:
        await state.set_state(None)

        order_id = callback_data.id

        from fpbot.funpaybot import get_funpay_bot as fpbot
        fpbot().account.delete_review(order_id)

        await callback_order_page(callback, calls.OrderPage(id=order_id), state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.back_kb(calls.OrderPage(id=callback_data.id).pack())
        )


@router.callback_query(F.data == "orders_filter")
async def callback_orders_filter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page") or 0
    orders_filter = data.get("orders_filter") or {"statuses": []}

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.orders_float_text("✨ Настройте <b>фильтр</b> заказов:"),
        reply_markup=templ.orders_filter_kb(orders_filter, last_page),
        callback=callback
    )


@router.callback_query(calls.ChangeOrdersFilter.filter())
async def callback_change_orders_filter(callback: CallbackQuery, callback_data: calls.ChangeOrdersFilter, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page") or 0
    orders_filter = data.get("orders_filter") or {"statuses": []}

    st = callback_data.st
    statuses = orders_filter["statuses"]

    if st == 1:
        if "paid" in statuses: statuses.remove("paid")
        else: statuses.append("paid")
    elif st == 2:
        if "closed" in statuses: statuses.remove("closed")
        else: statuses.append("closed")
    elif st == 3:
        if "refunded" in statuses: statuses.remove("refunded")
        else: statuses.append("refunded")
    elif st == 4:
        statuses.clear()

    orders_filter["statuses"] = statuses
    await state.update_data(
        orders_filter=orders_filter,
        orders=[],
        orders_next_id=None,
        is_all_orders_loaded=False,
    )

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.orders_float_text("✨ Настройте <b>фильтр</b> заказов:"),
        reply_markup=templ.orders_filter_kb(orders_filter, last_page),
        callback=callback
    )


@router.callback_query(calls.DeleteLot.filter())
async def callback_delete_lot(callback: CallbackQuery, callback_data: calls.DeleteLot, state: FSMContext):
    await state.set_state(None)

    lot_id = callback_data.id
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.lot_float_text("🗑 Подтвердите <b>удаление лота</b>:"),
        reply_markup=templ.confirm_kb(
            confirm_cb=calls.ConfirmDeleteLot(id=lot_id).pack(),
            cancel_cb=calls.LotPage(id=lot_id).pack()
        ),
        callback=callback
    )


@router.callback_query(calls.ConfirmDeleteLot.filter())
async def callback_confirm_delete_lot(callback: CallbackQuery, callback_data: calls.ConfirmDeleteLot, state: FSMContext):
    try:
        await state.set_state(None)

        lot_id = callback_data.id

        from fpbot.funpaybot import get_funpay_bot as fpbot
        fpbot().account.delete_lot(int(lot_id))

        data = await state.get_data()
        last_page = data.get("last_page") or 0
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.lots_float_text(f"✅ Лот <b>удалён</b>"),
            reply_markup=templ.back_kb(calls.LotsPagination(page=last_page, upd=True).pack()),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.back_kb(calls.LotPage(id=callback_data.id).pack())
        )


@router.callback_query(calls.ToggleLotActive.filter())
async def callback_toggle_lot_active(callback: CallbackQuery, callback_data: calls.ToggleLotActive, state: FSMContext):
    try:
        await state.set_state(None)

        lot_id = callback_data.id

        from fpbot.funpaybot import get_funpay_bot as fpbot
        acc = fpbot().account

        lf = acc.get_lot_fields(int(lot_id))
        lf.active = not lf.active
        acc.save_lot(lf)

        await callback_lot_page(callback, calls.LotPage(id=lot_id), state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.back_kb(calls.LotPage(id=callback_data.id).pack())
        )


@router.callback_query(calls.EditLotPrice.filter())
async def callback_edit_lot_price(callback: CallbackQuery, callback_data: calls.EditLotPrice, state: FSMContext):
    await state.set_state(states.FunPayStates.waiting_for_lot_price)
    await state.update_data(lot_id=callback_data.id, callback=callback)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.lot_float_text("💬 Введите <b>новую цену</b>:"),
        reply_markup=templ.back_kb(calls.LotPage(id=callback_data.id).pack()),
        callback=callback
    )


@router.callback_query(calls.EditLotDescription.filter())
async def callback_edit_lot_description(callback: CallbackQuery, callback_data: calls.EditLotDescription, state: FSMContext):
    await state.set_state(states.FunPayStates.waiting_for_lot_description)
    await state.update_data(lot_id=callback_data.id, callback=callback)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.lot_float_text("💬 Введите <b>новое описание</b>:"),
        reply_markup=templ.back_kb(calls.LotPage(id=callback_data.id).pack()),
        callback=callback
    )


@router.callback_query(calls.AnswerReview.filter())
async def callback_answer_review(callback: CallbackQuery, callback_data: calls.AnswerReview, state: FSMContext):
    await state.set_state(states.FunPayStates.waiting_for_order_review_answer)
    await state.update_data(order_id=callback_data.id, callback=callback, from_review=True)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.review_float_text("💬 Введите <b>ответ на отзыв</b>:"),
        reply_markup=templ.back_kb(calls.ReviewPage(id=callback_data.id).pack()),
        callback=callback
    )


@router.callback_query(calls.DeleteReview.filter())
async def callback_delete_review(callback: CallbackQuery, callback_data: calls.DeleteReview, state: FSMContext):
    try:
        await state.set_state(None)

        order_id = callback_data.id

        from fpbot.funpaybot import get_funpay_bot as fpbot
        fpbot().account.delete_review(order_id)

        await callback_review_page(callback, calls.ReviewPage(id=order_id), state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.back_kb(calls.ReviewPage(id=callback_data.id).pack())
        )


# ===== Авто-вывод =====

@router.callback_query(F.data == "switch_auto_withdrawal_enabled")
async def callback_switch_auto_withdrawal_enabled(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    config["funpay"]["auto_withdrawal"]["enabled"] = not config["funpay"]["auto_withdrawal"]["enabled"]
    sett.set("config", config)
    await callback_menu_navigation(callback, calls.MenuNavigation(to="withdrawal"), state)


@router.callback_query(F.data == "enter_withdrawal_interval")
async def callback_enter_withdrawal_interval(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.FunPayStates.waiting_for_withdrawal_interval)
    config = sett.get("config")
    interval = config["funpay"]["auto_withdrawal"]["interval"]
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.withdrawal_float_text(
            f"⏰ Введите <b>интервал</b> в секундах:\n\n・ <b>Текущий:</b> {interval} сек."
        ),
        reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack()),
        callback=callback
    )


@router.callback_query(F.data == "select_withdrawal_wallet")
async def callback_select_withdrawal_wallet(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.withdrawal_float_text("💳 Выберите <b>способ вывода</b>:"),
        reply_markup=templ.withdrawal_wallets_kb(),
        callback=callback
    )


@router.callback_query(F.data.startswith("sel_withdrawal_wallet:"))
async def callback_sel_withdrawal_wallet(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    wallet_type = callback.data.split(":", 1)[1]
    config = sett.get("config")
    config["funpay"]["auto_withdrawal"]["wallet_type"] = wallet_type
    cur_map = {"CARD_RUB": "rub", "CARD_USD": "usd", "CARD_EUR": "eur", "TRC": "rub",
               "YOUMONEY": "rub", "QIWI": "rub", "BINANCE": "rub", "WEBMONEY": "usd"}
    config["funpay"]["auto_withdrawal"]["currency"] = cur_map.get(wallet_type, "rub")
    sett.set("config", config)
    await callback_menu_navigation(callback, calls.MenuNavigation(to="withdrawal"), state)


@router.callback_query(F.data == "enter_withdrawal_address")
async def callback_enter_withdrawal_address(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.FunPayStates.waiting_for_withdrawal_address)
    config = sett.get("config")
    address = config["funpay"]["auto_withdrawal"]["address"] or "Не указано"
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.withdrawal_float_text(
            f"📬 Введите <b>реквизиты</b> для вывода:\n\n・ <b>Текущие:</b> {address}"
        ),
        reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack()),
        callback=callback
    )


@router.callback_query(F.data == "switch_withdrawal_amount_type")
async def callback_switch_withdrawal_amount_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    wd = config["funpay"]["auto_withdrawal"]
    wd["amount_type"] = "fixed" if wd["amount_type"] == "all" else "all"
    sett.set("config", config)
    if wd["amount_type"] == "fixed":
        await state.set_state(states.FunPayStates.waiting_for_withdrawal_amount_value)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.withdrawal_float_text("💰 Введите <b>сумму</b> для вывода:"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack()),
            callback=callback
        )
    else:
        await callback_menu_navigation(callback, calls.MenuNavigation(to="withdrawal"), state)


@router.callback_query(F.data == "confirm_withdrawal")
async def callback_confirm_withdrawal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    wd = config["funpay"]["auto_withdrawal"]
    amount_str = "Весь баланс" if wd["amount_type"] == "all" else f"{wd['amount']} {wd['currency'].upper()}"
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.withdrawal_float_text(
            f"✔️ Подтвердите <b>вывод средств</b>:\n\n"
            f"・ Сумма: {amount_str}\n"
            f"・ Способ: {wd['wallet_type']}\n"
            f"・ Реквизиты: {wd['address'] or 'Не указано'}"
        ),
        reply_markup=templ.confirm_kb("request_withdrawal", calls.MenuNavigation(to="withdrawal").pack()),
        callback=callback
    )


@router.callback_query(F.data == "request_withdrawal")
async def callback_request_withdrawal(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.withdrawal_float_text("💸 Создаю <b>вывод средств</b>, ожидайте (см. консоль)..."),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack()),
            callback=callback
        )
        from fpbot.funpaybot import get_funpay_bot as fpbot
        success, amount, error = fpbot().request_withdrawal()
        if success:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.withdrawal_float_text(f"✅ Вывод <b>успешно создан</b>: {amount}"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack()),
                callback=callback
            )
        else:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.withdrawal_float_text(f"❌ Ошибка при выводе: <blockquote>{error}</blockquote>"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack()),
                callback=callback
            )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.withdrawal_float_text(f"❌ Ошибка: <blockquote>{e}</blockquote>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack()),
            callback=callback
        )