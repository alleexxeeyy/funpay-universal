import ctypes

def set_title(title):
    """ 
    Задаёт заголовок командной строке
    
    :param title: Текст заголовка
    """
    ctypes.windll.kernel32.SetConsoleTitleW(title)