"""
This script is used to initialize the project. Developers that want to work on
this project need to run this script as first thing.

Please make sure to run this script with the local machine global Python 3
interpreter (run "python --version" to check).

This script will create a local virtual environment for python, every other
scripts should be run inside that environment.
"""

import os, shutil, subprocess, sys
from pathlib import Path

env_name = "env"


def cd(dir: str):
    os.chdir(dir)


def python(parameters: list[str]):
    subprocess.check_call(["python", "-m"] + parameters)


def python_env(parameters: list[str]):
    if sys.platform == "win32":
        subprocess.check_call([f"{env_name}/Scripts/python", "-m"] + parameters)
    else:
        subprocess.check_call([f"{env_name}/bin/python", "-m"] + parameters)


def requirements(file_path):
    result = []

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for row in file:
                result.append(row.strip())

    return result


# Move to script directory
cd(os.path.dirname(__file__))

# Make sure that pip is ready and updated
python(["ensurepip"])
python(["pip", "install", "--upgrade", "pip"])

# Setup the virtual environment
env_path = Path("env")
if env_path.exists() and not env_path.is_dir():
    shutil.rmtree(env_path)
if not env_path.exists():
    python(["venv", env_name])

# Make sure that pip is ready and updated in the virtual environment
python_env(["ensurepip"])
python_env(["pip", "install", "--upgrade", "pip"])

# Install the project requirements
python_env(
    ["pip", "install"]
    + requirements("requirements.txt")
    + requirements(f"requirements-{sys.platform}.txt")
)

# Install the project itself
python_env(["pip", "install", "-e", "."])
