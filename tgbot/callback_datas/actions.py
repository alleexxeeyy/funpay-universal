from aiogram.filters.callback_data import CallbackData


class RememberChatName(CallbackData, prefix="rech"):
    name: str
    do: str

class RememberOrderId(CallbackData, prefix="reor"):
    or_id: str
    do: str

class DeleteIncludedRaiseCategory(CallbackData, prefix="delinra"):
    index: int

class DeleteExcludedRaiseCategory(CallbackData, prefix="delexra"):
    index: int