import sys
import pathlib
import subprocess


try:
    import colorama

    colorama.init(autoreset=True)
    WARN = colorama.Fore.YELLOW
    ERROR = colorama.Fore.RED

    def print_and_format(msg: str, fmt=None):
        if fmt is None:
            print(msg)
        else:
            print(fmt + msg)

except ImportError:
    WARN = None
    ERROR = None

    def print_and_format(msg: str, fmt):
        print(msg)


def check_os_is_windows() -> bool:
    """Returns `True` if the operating system is Windows, else `False`."""
    return sys.platform == "win32"


def check_running_in_virtual_environment() -> bool:
    """Returns `True` if running in a virtual environment, else `False`."""
    return sys.prefix == sys.base_prefix


def check_git_installed() -> bool:
    """Returns `True` if git is installed, else `False`."""
    try:
        subprocess.run(["git", "-h"], capture_output=True)
        return True
    except FileNotFoundError:
        return False


def get_python_versions() -> dict[tuple[int, int], pathlib.Path]:
    """Return currently installed Python versions."""
    # to check 32 or 64 bit:
    # import struct; struct.calcsize("P") * 8
    # either 32 or 64


