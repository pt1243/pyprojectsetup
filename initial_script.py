import sys
import subprocess
import pathlib
import shutil
import re


__version__ = "0.1.0"


def check_prerequisites():
    """Checks that all required prerequisites for running this script are satisfied."""
    global colorama, requests

    problems: dict[str, bool] = {
        "os": False,
        "git": False,
        "venv": False,
        "colorama": False,
        "requests": False,
    }

    if sys.platform != "win32":
        problems["os"] = True

    try:
        subprocess.run(["git", "-h"], capture_output=True)
    except FileNotFoundError:
        problems["git"] = True
    
    if not check_virtual_environment():
        problems["venv"] = True
    
    try:
        import colorama
        colorama.init(autoreset=False)
        ERROR = colorama.Fore.RED
        WARN = colorama.Fore.YELLOW
    except ImportError:
        problems["colorama"] = True
    
    try:
        import requests
    except ImportError:
        problems["requests"] = True  # separate per module?
    
    def print_and_format(msg: str, fmt):
        if not problems["colorama"]:
            print(fmt + msg)
        else:
            print(msg)

    if problems["os"]:
        print_and_format("ERROR: this tool is currently only supported on Windows.", ERROR)
        exit(1)
    
    if problems["git"]:
        print_and_format("ERROR: git not found.", ERROR)
        print_and_format("Please verify that git is installed by running 'git -h'.", ERROR)
        exit(1)
    
    if problems["venv"]:
        print_and_format("Warning: script is not running from a virtual environment.", WARN)
        print_and_format("This script should be run from a virtual environment to ensure that all dependencies are isolated.", WARN)
    
    if any((problems["colorama"], problems["requests"])):
        print_and_format("ERROR: the following dependencies could not be imported:", ERROR)
        if problems["colorama"]:
            print_and_format("    colorama", ERROR)
        if problems["requests"]:
            print_and_format("    requests", ERROR)
        exit(1)


def check_virtual_environment() -> bool:
    return sys.prefix != sys.base_prefix


def warn_virtual_environment() -> None:
    if not check_virtual_environment:
        print(colorama.Fore.YELLOW + "warning: not running in virtual environment")


def check_update_available() -> bool:
    url = "https://raw.githubusercontent.com/pt1243/pyprojectsetup/main/initial_script.py"
    r = requests.get(url)
    version_string = r"__version__ = ['\"]([^'\"]*)['\"]"
    match = re.search(version_string, r.text)
    if match is None:
        raise ValueError("could not match")  # add formatting
    else:
        found_version_string = match.group(1)
        if found_version_string > __version__:
            return True
        return False



def get_python_versions() -> dict[tuple[int, int], pathlib.Path]:
    found: dict[tuple[int, int], pathlib.Path] = {}

    def get_version_tuple():
        return (sys.version_info[0], sys.version_info[1])

    try:
        py_0p = subprocess.run(["py", "-0p"], capture_output=True, text=True)
        lines = py_0p.stdout.splitlines()
        for line in lines:
            line = line.strip()

            if line.startswith("*"):  # currently in a virtual environment
                executable_path = pathlib.Path(sys.base_exec_prefix) / "python.exe"
                version_tuple = get_version_tuple()  # our python version is the same as the base
                if version_tuple[0] < 3:
                    continue  # skip python 2.7
                found[version_tuple] = executable_path
            
            elif "*" in line:  # preferred environment
                version_str, _, path_str = line.split(maxsplit=2)
                version_tuple = (int(version_str[3]), int(version_str[5:]))  # todo: guard against ValueError
                if version_tuple[0] < 3:
                    continue  # skip python 2.7
                found[version_tuple] = pathlib.Path(path_str)
            
            else:  # non-preferred environment
                version_str, path_str = line.split(maxsplit=1)
                version_tuple = (int(version_str[3]), int(version_str[5:]))
                if version_tuple[0] < 3:
                    continue  # skip python 2.7
                found[version_tuple] = pathlib.Path(path_str)

    except FileNotFoundError:  # py launcher not installed
        pass  # should this log?

    if check_virtual_environment():  # in virtual environment
        executable_path = pathlib.Path(sys.base_exec_prefix) / "python.exe"
        version_tuple = get_version_tuple()  # our python version is the same as the base
        if version_tuple[0] >= 3 and version_tuple not in found.keys():
            found[version_tuple] = executable_path
    else:
        executable_path = sys.executable
        version_tuple = get_version_tuple()
        if version_tuple[0] >= 3 and version_tuple not in found.keys():
            found[version_tuple] = executable_path

    str_path = shutil.which("python")
    if str_path is not None:
        run_version = subprocess.run([str_path, "-c", "import sys; print(sys.version_info[0]); print(sys.version_info[1])"], capture_output=True, text=True)
        if run_version.returncode == 0:  # handle path not pointing to actual executable
            version_tuple = tuple(int(i) for i in run_version.stdout.split())
            if version_tuple[0] >= 3 and version_tuple not in found.keys():
                found[version_tuple] = pathlib.Path(str_path)
    
    return found


def main():
    # TODO: check windows, virtual environment, colorama, and other imports, git installed, and print warnings accordingly
    check_prerequisites()

    if not check_virtual_environment():
        print('warning: not running in virtual environment')

    # if check_update_available():
    #     pass

    python_versions = get_python_versions()


if __name__ == "__main__":
    main()
