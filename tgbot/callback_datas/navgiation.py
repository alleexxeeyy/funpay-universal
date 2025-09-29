from aiogram.filters.callback_data import CallbackData
from uuid import UUID



class SystemNavigation(CallbackData, prefix="sysnav"):
    to: str


class MenuNavigation(CallbackData, prefix="mennav"):
    to: str

class SettingsNavigation(CallbackData, prefix="setnav"):
    to: str

class InstructionNavigation(CallbackData, prefix="insnav"):
    to: str


class ModulesPagination(CallbackData, prefix="modpag"):
    page: int

class ModulePage(CallbackData, prefix="modpage"):
    uuid: UUID


class CustomCommandsPagination(CallbackData, prefix="cucopag"):
    page: int

class CustomCommandPage(CallbackData, prefix="cucopage"):
    command: str


class AutoDeliveriesPagination(CallbackData, prefix="audepag"):
    page: int

class AutoDeliveryPage(CallbackData, prefix="audepage"):
    lot_id: int


class MessagesPagination(CallbackData, prefix="msgpag"):
    page: int

class MessagePage(CallbackData, prefix="msgpage"):
    message_id: str