import sys
import pathlib
import subprocess
import os


_third_party_import_errors = {
    "colorama": False,
    "requests": False,
}


_BASE_PREFIX_PATH = pathlib.Path(sys.base_prefix)
_BASE_EXECUTABLE_PATH = _BASE_PREFIX_PATH / "python.exe"
_CURRENT_EXECUTABLE_PATH = pathlib.Path(sys.executable)


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
    _third_party_import_errors["colorama"] = True

    WARN = None
    ERROR = None

    def print_and_format(msg: str, fmt=None):
        print(msg)


try:
    import requests
except ImportError:
    _third_party_import_errors["requests"] = True

if any((v for v in _third_party_import_errors.values())):
    print_and_format("ERROR: unable to import the following third party dependencies:", ERROR)
    for module, import_error in _third_party_import_errors.items():
        if import_error:
            print_and_format(f"    {module}", ERROR)
    print_and_format(
        "\nFollow the instructions at https://github.com/pt1243/pyprojectsetup#readme to create a virtual environment and install all required dependencies.",
        WARN,
    )
    exit(1)


def check_os_is_windows() -> bool:
    """Returns `True` if the operating system is Windows, else `False`."""
    return sys.platform == "win32"


def check_running_in_virtual_environment() -> bool:
    """Returns `True` if running in a virtual environment, else `False`."""
    return sys.prefix != sys.base_prefix


def check_git_installed() -> bool:
    """Returns `True` if git is installed, else `False`."""
    try:
        subprocess.run(["git", "-h"], capture_output=True)
        return True
    except OSError:
        return False


def is_64_bit(executable: pathlib.Path) -> bool:
    """Returns `True` if the executable is 64-bit Python, else `False`."""
    return (
        subprocess.run(
            [str(executable), "-c", "import struct; print(struct.calcsize('P') * 8)"], capture_output=True, text=True
        ).stdout.strip()
        == "64"
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
    """Return `True` if the executable is a Python interpreter, else `False`."""
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

    possible_executable_paths: set[pathlib.Path] = set()

    try:
        py_launcher_result = subprocess.run(["py", "-0p"], capture_output=True, text=True)
        lines = py_launcher_result.stdout.splitlines()
        for line in lines:
            line = line.strip()

            if line.startswith("*"):  # current virtual environment
                executable_path = _BASE_EXECUTABLE_PATH
                # print(f"current virtual environment, {executable_path = }")

            elif "*" in line:  # preferred environment
                executable_path = pathlib.Path(line.split(maxsplit=2)[-1])
                # print(f"preferred environment, {executable_path = }")

            else:  # non-preferred envionment
                executable_path = pathlib.Path(line.split(maxsplit=1)[-1])
                # print(f"non-preferred environment, {executable_path = }")

            possible_executable_paths.add(executable_path)

    except OSError:  # py launcher not installed
        print_and_format(
            "Warning: py launcher for Windows is not installed. Some installed Python versions may not be automatically detected.",
            WARN,
        )
        print_and_format(
            "See https://github.com/pt1243/python-guide/blob/main/practical-matters/installing-and-managing-python.md for more information.",
            WARN,
        )

    path_entries = subprocess.run("echo %PATH%", shell=True, capture_output=True, text=True).stdout.strip()
    for entry in path_entries.split(";"):
        if "Python" in entry:
            if entry.endswith("/Scripts/"):
                root_dir = pathlib.Path(entry).parent
            else:
                root_dir = pathlib.Path(entry)
            possible_executable = root_dir / "python.exe"
            if possible_executable.exists():
                # print(f"found from PATH search, {possible_executable = }")
                possible_executable_paths.add(possible_executable)

    try:
        env = {"VIRTUAL_ENV": "", "PATH": os.environ["_OLD_VIRTUAL_PATH"]}
    except KeyError:
        env = None

    shutil_text = subprocess.run(
        [str(_BASE_EXECUTABLE_PATH), "-c", "import shutil; print(shutil.which('python'))"],
        env=env,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if shutil_text != "":
        possible_executable_paths.add(pathlib.Path(shutil_text))

    if check_running_in_virtual_environment():  # current interpreter
        possible_executable_paths.add(_BASE_EXECUTABLE_PATH)
    else:
        possible_executable_paths.add(_CURRENT_EXECUTABLE_PATH)

    from pprint import pprint

    # pprint(sorted(possible_executable_paths))
    for i in possible_executable_paths:
        print(i, verify_executable_is_python(i))
