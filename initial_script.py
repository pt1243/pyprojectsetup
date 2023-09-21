import sys
import subprocess
import pathlib
import shutil
import re


__version__ = "0.1.0"


def assert_is_windows() -> None:
    if sys.platform != "win32":
        # add formatting
        print("Error: this tool is currently only supported on Windows.")
        exit(1)


def import_third_party():
    global requests, colorama

    try:
        import colorama
        colorama.init(autoreset=True)
    except ImportError:
        print("WARNING: There was an error importing colorama.")
        warn_virtual_environment()
        sys.exit(1)
    
    try:  # other third party requests here
        import requests
        
    except ImportError as e:
        missing_module = e.msg[17:-1]
        print(colorama.Fore.YELLOW + "Warning: unable to import required third-party library" + missing_module)
        exit(1)


def check_virtual_environment() -> bool:
    return sys.prefix != sys.base_prefix


def warn_virtual_environment() -> None:
    if not check_virtual_environment:
        print(colorama.Fore.YELLOW + "warning: not running in virtual environment")


def assert_git_installed() -> None:
    try:
        res = subprocess.run(["git", "-h"], capture_output=True)
        if res.returncode != 0:
            print("Something has gone terribly wrong and I am not sure how it would be possible to be here")
            exit(1)
    except FileNotFoundError:
        print("Error: could not access git. Ensure that git is available by running 'git -h'.")
        exit(1)


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
    # TODO: check windows, virtual environment, colorama, and other imports, and print warnings accordingly
    assert_is_windows()
    warn_virtual_environment()
    import_third_party()
    
    assert_git_installed()

    if not check_virtual_environment():
        print('warning: not running in virtual environment')

    # if check_update_available():
    #     pass

    python_versions = get_python_versions()


if __name__ == "__main__":
    main()
