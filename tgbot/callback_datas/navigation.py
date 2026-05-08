from aiogram.filters.callback_data import CallbackData


class SystemNavigation(CallbackData, prefix="sysnav"):
    to: str

class MenuNavigation(CallbackData, prefix="mennav"):
    to: str

class StatsNavigation(CallbackData, prefix="stnav"):
    to: str