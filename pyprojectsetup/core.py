import sys
import pathlib
import subprocess


_third_party_import_errors = {
    "colorama": False,
    "requests": False,
    "virtualenv": False,
}


_BASE_PREFIX_PATH = pathlib.Path(sys.base_prefix)
_BASE_EXECUTABLE_PATH = _BASE_PREFIX_PATH / "python.exe"
_CURRENT_EXECUTABLE = pathlib.Path(sys.executable)
_ROOT_FOLDER = pathlib.Path(__file__).resolve().parents[1]
_IS_VIRTUAL_ENVIRONMENT = sys.prefix != sys.base_prefix


try:
    import colorama

    colorama.init(autoreset=True)
    WARN = colorama.Fore.YELLOW
    ERROR = colorama.Fore.RED

    def print_and_format(msg: str, fmt=None, **kwargs):
        if fmt is None:
            print(msg, **kwargs)
        else:
            print(fmt + msg, **kwargs)

except ImportError:
    _third_party_import_errors["colorama"] = True

    WARN = None
    ERROR = None

    def print_and_format(msg: str, fmt=None, **kwargs):
        print(msg, **kwargs)


if not _IS_VIRTUAL_ENVIRONMENT:
    print_and_format("ERROR: not running from a virtual environment.", ERROR)
    print_and_format(
        "Follow the instructions at https://github.com/pt1243/pyprojectsetup#readme to install this tool correctly.",
        WARN,
    )
    exit(1)


try:
    import tkinter as tk
    import tkinter.filedialog
except ImportError:
    print_and_format("ERROR: unable to import tkinter. Ensure Python is installed with tkinter support.", ERROR)
    print_and_format(
        "See https://github.com/pt1243/python-guide/blob/main/practical-matters/installing-and-managing-python.md for more information.",
        WARN,
    )
    exit(1)

_root = tk.Tk()
_root.wm_attributes("-topmost", -1)
_root.withdraw()

try:
    import requests
except ImportError:
    _third_party_import_errors["requests"] = True
try:
    import virtualenv
except ImportError:
    _third_party_import_errors["virtualenv"] = True

if any(v for v in _third_party_import_errors.values()):
    print_and_format("ERROR: unable to import the following third party dependencies:", ERROR)
    for module, import_error in _third_party_import_errors.items():
        if import_error:
            print_and_format(f"    {module}", ERROR)
    print_and_format(
        "Would you like to install these dependencies now? This will run the appropriate 'pip' commands to do so."
    )

    ...  # TODO: prompt library
    # if True:
    install_deps = True

    if install_deps:
        pip_install_call = subprocess.run(
            [str(_CURRENT_EXECUTABLE), "-m", "pip", "install", "requests", "colorama", "virtualenv"],
            capture_output=True,
            text=True,
        )
        if pip_install_call.returncode != 0:
            print_and_format(
                f"ERROR: pip failed with exit code {pip_install_call.returncode} and the following stdout and stderr:",
                ERROR,
            )
            print_and_format("\nstdout:", ERROR)
            for line in pip_install_call.stdout.splitlines():
                print("    " + line)
            print_and_format("\nstderr:", ERROR)
            for line in pip_install_call.stderr.splitlines():
                print("    " + line)
            exit(1)

        else:
            print_and_format("All dependencies successfully installed.")


def check_os_is_windows() -> bool:
    """Returns `True` if the operating system is Windows, else `False`."""
    return sys.platform == "win32"


def check_git_installed() -> bool:
    """Returns `True` if git is installed, else `False`."""
    try:
        if subprocess.run(["git", "-h"], capture_output=True).returncode != 0:
            return False
        return True
    except OSError:
        return False


def get_is_64_bit(executable: pathlib.Path) -> bool:
    """Returns `True` if the executable is 64-bit Python, else `False`."""
    return (
        subprocess.run(
            [str(executable), "-c", "import sys; print(sys.maxsize > 2**32)"], capture_output=True, text=True
        ).stdout.strip()
        == "True"
    )


def get_version_info(executable: pathlib.Path) -> tuple[int, int]:
    """Returns a tuple of the major and minor Python version, eg. (3, 11)."""
    res = subprocess.run(
        [str(executable), "-c", "import sys; print(sys.version_info[0], sys.version_info[1])"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    return int(res[0]), int(res[2:])


def verify_executable_is_python(executable: pathlib.Path) -> bool:
    """Return `True` if the executable seems to be a functional a Python interpreter, else `False`."""
    return (
        pathlib.Path(
            subprocess.run(
                [str(executable), "-c", "import sys; print(sys.executable)"], capture_output=True, text=True
            ).stdout.strip()
        )
        == executable
    )


def verify_executable_is_venv(executable: pathlib.Path) -> bool:
    """Returns `True` if the Python executable is a virtual environment, else `False`."""
    return (
        subprocess.run(
            [str(executable), "-c", "import sys; print(sys.prefix != sys.base_prefix)"], capture_output=True, text=True
        ).stdout.strip()
        == "True"
    )


def get_python_versions() -> dict[tuple[int, int], pathlib.Path]:
    """Return currently installed Python versions."""

    import winreg

    def enum_keys(key):  # iterate over subkeys
        i = 0
        while True:
            try:
                yield winreg.EnumKey(key, i)
            except OSError:
                break
            i += 1

    found_path_strings = set()

    for hive, flags in (
        (winreg.HKEY_CURRENT_USER, 0),  # local user installation
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),  # 64 bit
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),  # 32 bit
    ):
        try:
            with winreg.OpenKeyEx(hive, r"Software\Python\PythonCore", access=winreg.KEY_READ | flags) as python_core:
                for version in enum_keys(python_core):
                    with winreg.OpenKey(
                        python_core, rf"{version}\InstallPath"
                    ) as install_path:  # TODO: this probably needs error handling as well
                        try:
                            exec_str = winreg.QueryValueEx(install_path, "ExecutablePath")[0]
                            found_path_strings.add(exec_str)
                        except OSError:
                            print_and_format(
                                f"Warning: registry entry for Python version {version} does not have an associated executable path.",
                                WARN,
                            )
                            continue
        except OSError:  # move to the next hive
            continue

    paths_64_bit: dict[tuple[int, int], pathlib.Path] = {}
    paths_32_bit: dict[tuple[int, int], pathlib.Path] = {}

    for path_string in found_path_strings:
        executable = pathlib.Path(path_string)
        if executable.exists():
            if verify_executable_is_python(executable):
                if get_is_64_bit(executable):
                    paths_64_bit[get_version_info(executable)] = executable
                else:
                    paths_32_bit[get_version_info(executable)] = executable
            else:
                print_and_format(
                    f"Warning: executable at '{path_string}' does not appear to be a Python interpreter.", WARN
                )
                print_and_format("Consider (re)running the uninstaller to correctly remove all registry keys.", WARN)
                continue
        else:
            print_and_format(f"Warning: Python registry entry at '{path_string}' does not exist.", WARN)
            print_and_format("Consider (re)running the uninstaller to correctly remove all registry keys.", WARN)
            continue

    if len(paths_64_bit) == 0:
        if len(paths_32_bit) == 0:
            print_and_format("Error: could not obtain any Python installations from registry keys.", ERROR)
            print_and_format(
                "Falling back to current executable; additional installations will need to be selected manually.", WARN
            )
            return {(sys.version_info[0], sys.version_info[1]): _BASE_EXECUTABLE_PATH}
        else:
            print_and_format("Warning: no 64-bit versions of Python found.", WARN)
            print_and_format("Consider installing 64-bit Python.", WARN)
            for k in paths_32_bit:
                if k[0] == 2 or k[1] < 8:
                    # TODO: distinguish between completely unsupported, and just unsupported by tox etc
                    print_and_format(
                        f"Note: Python version {'.'.join(str(i) for i in k)} is no longer supported. This can still be selected manually.",
                    )
            return dict(sorted({k: v for k, v in paths_32_bit.items() if k[0] >= 3 and k[1] >= 8}.items()))

    if len(paths_32_bit) > 0:
        print_and_format("Warning: the following 32-bit Python installations were found:", WARN)
        for path in paths_32_bit.values():
            print_and_format(f"    {path}", WARN)
        print_and_format("Consider upgrading these versions to 64-bit Python.", WARN)

    for k in paths_64_bit:
        if k[0] == 2 or k[1] < 8:
            # TODO: distinguish between completely unsupported, and just unsupported by tox etc
            print_and_format(
                f"Note: Python version {'.'.join(str(i) for i in k)} is no longer supported. This can still be selected manually."
            )
    return dict(sorted({k: v for k, v in paths_64_bit.items() if k[0] >= 3 and k[1] >= 8}.items()))


def choose_directory(
    prompt: str = "Please select a folder...",
    title: str = "Select folder",
    initialdir: str | pathlib.Path = _ROOT_FOLDER,
    must_be_empty: bool = False,
) -> pathlib.Path:
    """Opens a tkinter folder choice dialog and returns the path to the folder."""
    while True:
        print_and_format(prompt)
        dir_str = tkinter.filedialog.askdirectory(title=title, initialdir=initialdir)
        if dir_str == "":
            try:
                input(
                    "Directory selection cancelled; press any key to continue... ",
                )
            except KeyboardInterrupt:
                exit(1)
            continue
        dir_path = pathlib.Path(dir_str)
        if must_be_empty:
            if next(dir_path.iterdir(), None) is None:
                break
            print_and_format(
                f"Warning: selected directory '{dir_path}' is not empty; press any key to re-select... ", WARN, end=""
            )
        else:
            break
    return dir_path
