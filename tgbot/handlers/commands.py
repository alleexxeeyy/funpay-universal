from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import tgbot.templates.all as templ
from tgbot.states.all import *

from settings import Settings as sett
from ..helpful import throw_float_message


router = Router()


@router.message(Command("start"))
async def handler_start(message: types.Message, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    if message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        await state.set_state(SystemStates.entering_password)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.sign_text("🔑 Введите ключ-пароль, указанный вами в конфиге бота ↓"),
                                  reply_markup=templ.destroy_kb())
        return
    await throw_float_message(state=state,
                              message=message,
                              text=templ.menu_text(),
                              reply_markup=templ.menu_kb())