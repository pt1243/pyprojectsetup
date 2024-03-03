import sys
import shutil
from collections.abc import Callable
from typing import Any
from pathlib import Path
import importlib.resources

from InquirerPy import inquirer
from InquirerPy.prompts import ListPrompt
from virtualenv.discovery.py_spec import PythonSpec
from virtualenv.discovery.windows import propose_interpreters


_templates = importlib.resources.files("pyprojectsetup.templates")

# p = _templates / "test_install.txt"
# print(p)
# print(p.exists())


def is_virtual_environment() -> bool:
    return sys.prefix != sys.base_prefix


def is_windows() -> bool:
    return sys.platform == "win32"


def is_git_installed() -> bool:
    return shutil.which("git") is not None


def list_selection(
    message: str,
    choices: list[str],
    long_instruction: str | None = None,
    filter_index: int | None = None,
    filter_func: Callable[[str], Any] | None = None,
) -> ListPrompt:
    kwargs = {
        "message": message,
        "choices": choices,
    }
    if long_instruction is not None:
        kwargs["long_instruction"] = long_instruction
    if filter_index is not None:
        if filter_func is not None:
            raise ValueError("cannot provide both filter index and filter function")
        if not 0 <= filter_index < len(choices):
            raise ValueError(f"invalid index {filter_index}, must be between 0 and {len(choices) - 1} inclusive")
        if len(set(choices)) != len(choices):
            raise ValueError("cannot filter list with duplicated choices")
        kwargs["filter"] = lambda res: True if res == choices[filter_index] else False
    if filter_func is not None:
        kwargs["filter"] = filter_func
    return inquirer.select(**kwargs)


def get_python_versions() -> dict[tuple[int, int], tuple[Path, int]]:
    found: dict[tuple[int, int], Path] = {}
    versions = ((3, 8), (3, 9), (3, 10), (3, 11), (3, 12))
    # TODO: filter anaconda, windows store versions
    for v in versions:
        interpreter = next(propose_interpreters(PythonSpec.from_string_spec(f"{v[0]}.{v[1]}-64"), None, None), None)
        if interpreter is not None:
            executable = Path(interpreter.executable)
            found[v] = (executable, 64)
        else:
            interpreter = next(propose_interpreters(PythonSpec.from_string_spec(f"{v[0]}.{v[1]}-32"), None, None), None)
            if interpreter is not None:
                executable = Path(interpreter.executable)
                found[v] = (executable, 32)
    return found


def is_on_path() -> bool:
    return shutil.which("pyprojectsetup") is not None

