from shutil import copy
from pathlib import Path
from importlib.resources import files

import virtualenv


class Setup:
    def __init__(
        self,
        root: Path,
        project_name: str,
        target_executable: Path,
        test_versions: list[tuple[int, int]],
        github: bool,
        gitlab: bool,
        pre_commit: bool,
        dependencies: list[str],
    ) -> None:
        self.root = root
        self.project_name = project_name
        self.target_executable = target_executable
        self.test_versions = test_versions
        self.github = github
        self.gitlab = gitlab
        self.pre_commit = pre_commit
        self.dependencies = dependencies
        self.template_files = files("pyprojectsetup.templates")

    def create_virtual_environment(self):
        virtualenv.cli_run((".venv", "-q", "-p", str(self.target_executable)))

    def copy_templates(self):
        pass


# $TOX_ALL_TEST_ENVS$ -> py{38,39,310,311,312}
# $PROJECT_NAME$ -> sample_project
# $PYPROJECT_TOML_DEPENDENCIES$ -> [\n    "numpy",\n    "scipy"\n] or []
# $AUTHOR_NAME$ -> Jeremy Smith
# $AUTHOR_EMAIL$ -> ...
# $PROJECT_BADGES$ ->
"""
[![Tests](https://github.com/pt1243/sample-project/actions/workflows/test.yml/badge.svg)](https://github.com/pt1243/sample-project/actions/workflows/test.yml)
[![Lint](https://github.com/pt1243/sample-project/actions/workflows/lint.yml/badge.svg)](https://github.com/pt1243/sample-project/actions/workflows/lint.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
"""
# $GITLAB_MATRIX_ENTRIES$ ->
"""
      - TOX_TEST_ENV: py38
        PYTHON_VERSION: "3.8"
      - TOX_TEST_ENV: py39
        PYTHON_VERSION: "3.9"
      - TOX_TEST_ENV: py310
        PYTHON_VERSION: "3.10"
      - TOX_TEST_ENV: py311
        PYTHON_VERSION: "3.11"
      - TOX_TEST_ENV: py312
        PYTHON_VERSION: "3.12"
"""