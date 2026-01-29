from aiogram.filters.callback_data import CallbackData


class ModulesPagination(CallbackData, prefix="modpag"):
    page: int

class CustomCommandsPagination(CallbackData, prefix="cucopag"):
    page: int

class AutoDeliveriesPagination(CallbackData, prefix="audepag"):
    page: int

class MessagesPagination(CallbackData, prefix="msgpag"):
    page: int