from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .funpaybot import FunPayBot

_funpay_bot: 'FunPayBot' = None

def get_funpay_bot() -> 'FunPayBot':
    global _funpay_bot
    return _funpay_bot

def set_funpay_bot(new: 'FunPayBot') -> 'FunPayBot':
    global _funpay_bot
    _funpay_bot = new