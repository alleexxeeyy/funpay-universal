from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError
from . import templates as templ



async def throw_float_message(state: FSMContext, message: Message, text: str, 
                              reply_markup: InlineKeyboardMarkup = None,
                              callback: CallbackQuery = None):
    """
    Изменяет плавающее сообщение (изменяет текст акцентированного сообщения) или родительское сообщение бота, переданное в аргумент `message`.\n
    Если не удалось найти акцентированное сообщение, или это сообщения - команда, отправит новое акцентированное сообщение.

    :param state: Состояние бота.
    :type state: `aiogram.fsm.context.FSMContext`
    
    :param message: Переданный в handler объект сообщения.
    :type message: `aiogram.types.Message`

    :param text: Текст сообщения.
    :type text: `str`

    :param reply_markup: Клавиатура сообщения, _опционально_.
    :type reply_markup: `aiogram.typesInlineKeyboardMarkup.`

    :param callback: CallbackQuery хендлера, для ответа пустой AnswerCallbackQuery, _опционально_.
    :type callback: `aiogram.types.CallbackQuery` or `None`
    """
    from . import get_telegram_bot
    try:
        bot = get_telegram_bot().bot
        data = await state.get_data()
        mess = None
        accent_message_id = data.get("accent_message_id") if message.from_user.id != bot.id else message.message_id
        new_mess_cond = False
        if message.text is not None:
            new_mess_cond = message.from_user.id != bot.id and message.text.startswith('/')

        if accent_message_id is not None and not new_mess_cond:
            try:
                if message.from_user.id != bot.id: 
                    await bot.delete_message(message.chat.id, message.message_id)
                mess = await bot.edit_message_text(text=text, reply_markup=reply_markup, 
                                                   chat_id=message.chat.id, message_id=accent_message_id, parse_mode="HTML")
            except TelegramAPIError as e:
                if "message to edit not found" in e.message.lower():
                    accent_message_id = None
                elif "message is not modified" in e.message.lower():
                    await bot.answer_callback_query(callback.id, show_alert=False, cache_time=0)
                    pass
                else:
                    raise e
        if callback:
            await bot.answer_callback_query(callback.id, show_alert=False, cache_time=0)
        if accent_message_id is None or new_mess_cond:
            mess = await bot.send_message(chat_id=message.chat.id, text=text, 
                                          reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        try:
            mess = await bot.edit_message_text(chat_id=message.chat.id, reply_markup=templ.destroy_kb(),
                                               text=templ.error_text(e), message_id=accent_message_id, parse_mode="HTML")
        except Exception as e:
            mess = await bot.send_message(chat_id=message.chat.id, reply_markup=templ.destroy_kb(),
                                          text=templ.error_text(e), parse_mode="HTML")
    finally:
        if mess: await state.update_data(accent_message_id=mess.message_id)