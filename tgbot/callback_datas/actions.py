from aiogram.filters.callback_data import CallbackData


class DeleteSignedUser(CallbackData, prefix="desu"):
    id: int
    
class RememberChatName(CallbackData, prefix="rech"):
    name: str
    do: str

class RememberOrderId(CallbackData, prefix="reor"):
    or_id: str
    do: str


class EnterFastReplyText(CallbackData, prefix="enrepl"):
    index: int

class DeleteFastReply(CallbackData, prefix="delrepl"):
    index: int


class DeleteIncludedRaiseCategory(CallbackData, prefix="delinra"):
    index: int

class DeleteExcludedRaiseCategory(CallbackData, prefix="delexra"):
    index: int


class SendLogsFile(CallbackData, prefix="selogs"):
    lines: int