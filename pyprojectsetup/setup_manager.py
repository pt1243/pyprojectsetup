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
