from aiogram.filters.callback_data import CallbackData
from uuid import UUID


class ModulePage(CallbackData, prefix="modpage"):
    uuid: UUID

class MessagePage(CallbackData, prefix="msgpage"):
    message_id: str

class AutoDeliveryPage(CallbackData, prefix="audepage"):
    lot_id: int

class CustomCommandPage(CallbackData, prefix="cucopage"):
    command: str