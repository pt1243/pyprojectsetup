# pyprojectsetup
Setup tools to initialize a Python project template.

```
if exist pyprojectsetup\ (rmdir pyprojectsetup /s /q) && mkdir pyprojectsetup && cd pyprojectsetup && py -m venv .venv && .venv\scripts\activate && py -m pip install -q --upgrade pip && py -m pip install -q git+https://github.com/pt1243/pyprojectsetup.git && initial-setup && deactivate && cd ..
```