"""Initial setup script."""


import subprocess
import sys
import pathlib
import shutil

try:
    from . import (
        check_os_is_windows,
        check_running_in_virtual_environment,
        get_python_versions,
        print_and_format,
        WARN,
        ERROR
    )
except ImportError:
    try:
        import colorama

        colorama.init(autoreset=True)
        print(colorama.Fore.RED + "Error: unable to perform relative imports.")
        print(colorama.Fore.YELLOW + "Follow the instructions at https://github.com/pt1243/pyprojectsetup#readme")
        print(colorama.Fore.YELLOW + "to create a virtual environment and install this as a package.")

    except ImportError:
        print("Error: unable to perform relative imports.")
        print("Follow the instructions at https://github.com/pt1243/pyprojectsetup#readme")
        print("to create a virtual environment and install this as a package.")
    
    finally:
        exit(1)


def main():
    if not check_os_is_windows():
        print_and_format("ERROR: this tool is currently only supported on Windows.", ERROR)
    



if __name__ == "__main__":
    main()
