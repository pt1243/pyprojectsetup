import sys
import shutil


def is_virtual_environment():
    return sys.prefix != sys.base_prefix


def is_windows():
    return sys.platform == "win32"


def has_git_installed():
    return shutil.which("git") is not None
