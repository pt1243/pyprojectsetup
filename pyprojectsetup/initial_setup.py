"""Initial setup script."""


import subprocess
import sys
import pathlib
import shutil

try:
    from core import (
        check_os_is_windows,
        check_running_in_virtual_environment,
        check_git_installed,
        get_python_versions,
        print_and_format,
        WARN,
        ERROR,
    )
except ImportError:
    try:
        import colorama

        colorama.init(autoreset=True)
        print(colorama.Fore.RED + "ERROR: unable to perform relative imports.")
        print(
            colorama.Fore.YELLOW
            + "Follow the instructions at https://github.com/pt1243/pyprojectsetup#readme to create a virtual environment and install this tool as a package."
        )

    except ImportError:
        print("ERROR: unable to perform relative imports.")
        print(
            "Follow the instructions at https://github.com/pt1243/pyprojectsetup#readme to create a virtual environment and install this tool as a package."
        )

    finally:
        exit(1)

import requests
import colorama


def main():
    if not check_os_is_windows():
        print_and_format("ERROR: this tool is currently only supported on Windows.", ERROR)
        exit(1)

    if not check_running_in_virtual_environment():
        print_and_format("Warning: not running in a virtual environment.", WARN)
        print_and_format(
            "Follow the instructions at https://github.com/pt1243/pyprojectsetup#readme to create a virtual environment and install this tool as a package.",
            WARN,
        )

    if not check_git_installed():
        print_and_format("Warning: git is not installed.", WARN)
        print_and_format(
            "This install script will continue to run, but git must be installed for the main script to function.", WARN
        )

    python_versions = get_python_versions()


if __name__ == "__main__":
    main()