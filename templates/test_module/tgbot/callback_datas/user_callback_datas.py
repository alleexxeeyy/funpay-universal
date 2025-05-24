from aiogram.filters.callback_data import CallbackData



class TestModule_MenuNavigation(CallbackData, prefix="tm_menpag"):
    """ Навигация в меню """
    to: str

class TestModule_SettingsNavigation(CallbackData, prefix="tm_spag"):
    """ Навигация в настройках """
    to: str

class TestModule_InstructionNavigation(CallbackData, prefix="tm_ipag"):
    """ Навигация в инструкции """
    to: str