import sys
import ctypes

def set_title(title):
    """
    Устанавливает заголовок консоли (кросс-платформенно).
    Работает на Windows, Linux и macOS.
    """
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    elif sys.platform.startswith("linux"):
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()
    elif sys.platform == "darwin":
        sys.stdout.write(f"\x1b]0;{title}\x07")
        sys.stdout.flush()
    else:
        print(f"Заголовок консоли не поддерживается на {sys.platform}")