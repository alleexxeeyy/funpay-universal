from aiogram.filters.callback_data import CallbackData


class ModulesPagination(CallbackData, prefix="modpag"):
    page: int

class SignedUsersPagination(CallbackData, prefix="supag"):
    page: int
    

class CustomCommandsPagination(CallbackData, prefix="cucopag"):
    page: int

class AutoDeliveriesPagination(CallbackData, prefix="audepag"):
    page: int

class MessagesPagination(CallbackData, prefix="msgpag"):
    page: int


class FastRepliesPagination(CallbackData, prefix="fspag"):
    page: int

class FastSelFastReplyPagination(CallbackData, prefix="fsrpag"):
    id: str
    page: int

class SelFastReplyPagination(CallbackData, prefix="srpag"):
    id: str
    page: int