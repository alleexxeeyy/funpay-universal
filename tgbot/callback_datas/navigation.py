from aiogram.filters.callback_data import CallbackData
from uuid import UUID


# --- Навигация по разделам ---

class SystemNavigation(CallbackData, prefix="sysnav"):
    to: str


class MenuNavigation(CallbackData, prefix="mennav"):
    to: str


class SettingsNavigation(CallbackData, prefix="setnav"):
    to: str


class InstructionNavigation(CallbackData, prefix="insnav"):
    to: str


# --- Пагинация по страницам ---

class ModulesPagination(CallbackData, prefix="modpag"):
    page: int


class CustomCommandsPagination(CallbackData, prefix="cucopag"):
    page: int


class AutoDeliveriesPagination(CallbackData, prefix="audepag"):
    page: int


class MessagesPagination(CallbackData, prefix="msgpag"):
    page: int


# --- Страницы меню пагинаций ---

class ModulePage(CallbackData, prefix="modpage"):
    uuid: UUID


class MessagePage(CallbackData, prefix="msgpage"):
    message_id: str


class AutoDeliveryPage(CallbackData, prefix="audepage"):
    lot_id: int


class CustomCommandPage(CallbackData, prefix="cucopage"):
    command: str