from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.message(states.AutoDeliveriesStates.waiting_for_page, F.text)
async def handler_waiting_for_auto_deliveries_page(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.delivs_float_text(f"📃 Введите номер страницы для перехода ↓"),
            reply_markup=templ.delivs_kb(int(message.text)-1)
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.delivs_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_lot_link, F.text)
async def handler_waiting_for_new_auto_delivery_lot_link(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if (
            "funpay.com/lots/offer" not in message.text.strip() 
            and "funpay.com/lots/offerEdit" not in message.text.strip()
        ):
            raise Exception("❌ Вы ввели некорректную ссылку на лот. Пример: https://funpay.com/lots/offer?id=12345")
        
        if "funpay.com/lots/offer" in message.text.strip():
            lot_id_dirty = message.text.strip().split("?id=")[1]
        elif "funpay.com/lots/offerEdit" in message.text.strip():
            lot_id_dirty = message.text.strip().split("&offer=")[1]
        
        lot_id = int(''.join([ch for ch in lot_id_dirty if ch.isdigit()]))

        from fpbot.funpaybot import get_funpay_bot
        try: lot = get_funpay_bot().account.get_lot_fields(lot_id)
        except: raise Exception("❌ Лот не был найден. Убедитесь, что вы указали верную ссылку")

        data = await state.get_data()
        await state.update_data(
            new_auto_delivery_lot_id=lot_id,
            new_auto_delivery_lot=lot
        )
        await state.set_state(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_float_text(f"💬 Введите <b>сообщение авто-выдачи</b>, которое будет писаться после покупки лота ↓"),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message, F.text)
async def handler_waiting_for_new_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await state.update_data(new_auto_delivery_message=message.text.strip())

        lot_id = data.get("new_auto_delivery_lot_id")
        lot = data.get("new_auto_delivery_lot")
        msg = message.text.strip()

        try: lot_title = lot.title_ru
        except: lot_title = lot_id
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_float_text(
                f"✔️ Подтвердите <b>добавление авто-выдачи:</b>"
                f'\n\n<b>· Лот:</b> <a href="https://funpay.com/lots/offer?id={lot_id}">{lot_title}</a>'
                f"\n<b>· Сообщение:</b> {msg}"
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb="add_new_auto_delivery", 
                cancel_cb=calls.AutoDeliveriesPagination(page=last_page).pack()
            )
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_lot_link, F.text)
async def handler_waiting_for_auto_delivery_lot_link(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if (
            "funpay.com/lots/offer" not in message.text.strip() 
            and "funpay.com/lots/offerEdit" not in message.text.strip()
        ):
            raise Exception("❌ Вы ввели некорректную ссылку на лот. Пример: https://funpay.com/lots/offer?id=12345")
        
        if "funpay.com/lots/offer" in message.text.strip():
            lot_id_dirty = message.text.strip().split("?id=")[1]
        elif "funpay.com/lots/offerEdit" in message.text.strip():
            lot_id_dirty = message.text.strip().split("&offer=")[1]
        
        lot_id = int(''.join([ch for ch in lot_id_dirty if ch.isdigit()]))

        from fpbot.funpaybot import get_funpay_bot
        try: lot = get_funpay_bot().account.get_lot_fields(lot_id)
        except: raise Exception("❌ Лот не был найден. Убедитесь, что вы указали верную ссылку")

        data = await state.get_data()
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[str(lot_id)] = auto_deliveries.pop(data["auto_delivery_lot_id"])
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deliv_page_float_text(
                f"✅ <b>Лот авто-выдачи</b> был успешно изменён на: "
                f'<a href="https://funpay.com/lots/offer?id={lot_id}">{lot.title_ru}</a>'
            ),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=data.get("auto_delivery_lot_id")).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=data.get("auto_delivery_lot_id")).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_message, F.text)
async def handler_waiting_for_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        auto_deliveries = sett.get("auto_deliveries")
        answer_split_lines = message.text.strip().split('\n')
        auto_deliveries[data["auto_delivery_lot_id"]] = answer_split_lines
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deliv_page_float_text(f"✅ <b>Сообщение авто-выдачи</b> лота <code>{data['auto_delivery_lot_id']}</code> было успешно изменено на: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=data.get("auto_delivery_lot_id")).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(lot_id=data.get("auto_delivery_lot_id")).pack())
        )