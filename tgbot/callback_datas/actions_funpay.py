from aiogram.filters.callback_data import CallbackData


class SendFastReply(CallbackData, prefix="sere"):
    id: str
    index: int

class FastSendFastReply(CallbackData, prefix="fsere"):
    name: str
    index: int


class FastRefundOrder(CallbackData, prefix="frf"):
    id: str

class FastAnswerReview(CallbackData, prefix="far"):
    id: str


class RefundOrder(CallbackData, prefix="orf"):
    id: str

class AnswerOrderReview(CallbackData, prefix="orar"):
    id: str

class DeleteOrderReview(CallbackData, prefix="ordr"):
    id: str


class ChangeOrdersFilter(CallbackData, prefix="cof"):
    st: int


class DeleteLot(CallbackData, prefix="lotdel"):
    id: str

class ConfirmDeleteLot(CallbackData, prefix="lotcdel"):
    id: str

class ToggleLotActive(CallbackData, prefix="lottgl"):
    id: str

class EditLotPrice(CallbackData, prefix="lotprc"):
    id: str

class EditLotDescription(CallbackData, prefix="lotdesc"):
    id: str


class AnswerReview(CallbackData, prefix="revans"):
    id: str

class DeleteReview(CallbackData, prefix="revdel"):
    id: str
