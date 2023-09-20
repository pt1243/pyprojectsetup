import sys
import subprocess
import pathlib


def assert_is_windows() -> None:
    if sys.platform != "win32":
            print("Error: this tool is currently only supported on Windows.")
            exit(1)


def assert_git_installed() -> None:
    try:
        subprocess.run(["git", "-h"], capture_output=True)
    except FileNotFoundError:
        print("Error: could not access git. Ensure that git is available by running 'git -h'.")
        exit(1)


def get_python_versions() -> dict[tuple[int, int], pathlib.Path]:
    found: dict[tuple[int, int], pathlib.Path] = {}

    try:
        py_0p = subprocess.run(["py", "-0p"], capture_output=True, text=True)
        lines = py_0p.stdout.splitlines()
        for line in lines:
            line = line.strip()

            if line.startswith("*"):  # currently in a virtual environment
                executable_path = pathlib.Path(sys.base_exec_prefix) / "python.exe"
                if not pathlib.Path.exists(executable_path):  # this should never execute, but just in case
                    continue
                version_tuple = (sys.version_info[0], sys.version_info[1])  # our python version is the same as the base
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
        pass

    finally:
        from pprint import pprint
        pprint(found)


def main():
    assert_is_windows()
    assert_git_installed()

    python_versions = get_python_versions()


if __name__ == "__main__":
    main()
