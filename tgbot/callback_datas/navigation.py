from aiogram.filters.callback_data import CallbackData


class SystemNavigation(CallbackData, prefix="sysnav"):
    to: str

class MenuNavigation(CallbackData, prefix="mennav"):
    to: str

class SettingsNavigation(CallbackData, prefix="setnav"):
    to: str

class InstructionNavigation(CallbackData, prefix="insnav"):
    to: str