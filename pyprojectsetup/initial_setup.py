"""Initial setup script."""


try:
    from .core import (
        check_os_is_windows,
        check_git_installed,
        get_python_versions,
        print_and_format,
        choose_directory,
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
        raise SystemExit(1)


from pathlib import Path
import shutil
from InquirerPy import inquirer

import sys

print(sys.executable)


def main():
    if not check_os_is_windows():
        print_and_format("ERROR: this tool is currently only supported on Windows.", ERROR)
        exit(1)

    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)  # make tkinter not blurry

    if not check_git_installed():
        print_and_format("Warning: git is not installed.", WARN)
        print_and_format(
            "This install script will continue to run, but update checking will not be available, and git must be installed for the main script to function.",
            WARN,
        )

    python_versions = get_python_versions()
    from pprint import pprint

    pprint(python_versions)

    if shutil.which("pyprojectsetup") is None:
        ...  # prompt to add

        add_to_path = inquirer.select(
            message="Note: 'pyprojectsetup' is not registered as a command on your system PATH.\nWould you like to add it now?",
            choices=["Yes (recommended)", "No"],
            long_instruction="This alows you to run 'pyprojectsetup' from anywhere without first activating this virtual environment.\nThis is strongly recommended.",
            filter=lambda res: True if res == "Yes (recommended)" else False,
        ).execute()

        if add_to_path:
            chosen_directory = choose_directory(
                "Select a directory to add the script to...",
            )

    else:
        ...  # TODO: figure out what to do here

    # choose_directory(must_be_empty=True)


if __name__ == "__main__":
    main()
