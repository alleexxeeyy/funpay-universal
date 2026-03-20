import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def settings_conn_text():
    config = sett.get("config")
    
    fp_proxy = config["funpay"]["api"]["proxy"] or "❌ Не задано"
    tg_proxy = config["telegram"]["api"]["proxy"] or "❌ Не задано"
    
    requests_timeout = config["funpay"]["api"]["requests_timeout"] or "❌ Не задано"
    runner_requests_delay = config["funpay"]["api"]["runner_requests_delay"] or "❌ Не задано"
    
    txt = textwrap.dedent(f"""
        <b>📶 Соединение</b>

        <b>🌐 Прокси для FunPay:</b> {fp_proxy}
        <b>🌐 Прокси для Telegram:</b> {tg_proxy}
        
        <b>🛜 Таймаут подключения к funpay.com:</b> {requests_timeout}
        <b>⏱️ Периодичность запросов к funpay.com:</b> {runner_requests_delay}

        <b>Что за таймаут подключения к funpay.com?</b>
        Это максимальное время, за которое должен прийти ответ на запрос с сайта FunPay. Если время истекло, а ответ не пришёл — бот выдаст ошибку. Если у вас слабый интернет, указывайте значение больше

        <b>Что за периодичность запросов к funpay.com?</b>
        С какой периодичностью будут отправляться запросы на FunPay для получения событий. Не рекомендуем ставить ниже 4 секунд, так как FunPay попросту может забанить ваш IP адрес, и вы уже не сможете отправлять с него запросы
    """)
    return txt


def settings_conn_kb():
    config = sett.get("config")
    
    fp_proxy = config["funpay"]["api"]["proxy"] or "❌ Не задано"
    tg_proxy = config["telegram"]["api"]["proxy"] or "❌ Не задано"
    
    requests_timeout = config["funpay"]["api"]["requests_timeout"] or "❌ Не задано"
    runner_requests_delay = config["funpay"]["api"]["runner_requests_delay"] or "❌ Не задано"
    
    rows = [
        [InlineKeyboardButton(text=f"🌐 Прокси для FunPay: {fp_proxy}", callback_data="enter_fp_proxy")],
        [InlineKeyboardButton(text=f"🌐 Прокси для Telegram: {tg_proxy}", callback_data="enter_tg_proxy")],
        [InlineKeyboardButton(text=f"🛜 Таймаут подключения к funpay.com: {requests_timeout}", callback_data="enter_funpayapi_requests_timeout")],
        [InlineKeyboardButton(text=f"⏱️ Периодичность запросов к funpay.com: {runner_requests_delay}", callback_data="enter_funpayapi_runner_requests_delay")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack())]
    ]
    if config["funpay"]["api"]["proxy"]: 
        rows[0].append(InlineKeyboardButton(text=f"❌ Убрать прокси", callback_data="clean_fp_proxy"))
    if config["telegram"]["api"]["proxy"]: 
        rows[1].append(InlineKeyboardButton(text=f"❌ Убрать прокси", callback_data="clean_tg_proxy"))
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_conn_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📶 Соединение</b>
        \n{placeholder}
    """)
    return txt
