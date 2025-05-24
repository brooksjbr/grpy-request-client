import logging
import os
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Access variables
VENV_PATH = os.getenv("PYTHON_VENV_PATH")


def check_file_exists(file_path_str: str) -> bool:
    """
    Check if a file or directory exists at the given path.

    Args:
        file_path_str: String representation of the file path to check

    Returns:
        Boolean indicating whether the path exists (True) or not (False)
    """
    file_path = Path(file_path_str)
    return file_path.exists()


def run_command(command, timeout=300):
    """Execute shell command with timeout"""
    try:
        with subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as process:
            stdout, stderr = process.communicate(timeout=timeout)

            if process.returncode != 0:
                logger.error(f"Command error: {stderr}")
                raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)

            if stderr:
                logger.error(f"Command error: {stderr}")
            elif stdout != "":
                logger.info(f"Command output: {stdout}")

            return process
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout} seconds")
        raise


def set_path():
    cwd_name = Path.cwd().name

    if VENV_PATH:
        venv_path = Path(f"{VENV_PATH}/{cwd_name}")
    else:
        raise RuntimeError("No virtual env path available")

    return venv_path


def init_venv(venv_path: Path, deps_group: str = "dev"):
    # Create the virtual environment
    run_command(f"python3 -m venv --clear {venv_path}")

    # Install dependencies with specified group
    run_command(f'{venv_path}/bin/pip install -e ".[{deps_group}]"')

    # Print activation instructions instead of trying to activate
    logger.info(f"\nVirtual environment created at: {venv_path}")
    logger.info("To activate the virtual environment, run:")
    logger.info(f"  source {venv_path}/bin/activate")


def create_readme(project_dir: Path):
    """
    Create a basic README.md file in the project directory.

    Args:
        project_dir: Path to the project directory
    """
    readme_path = project_dir / "README.md"
    project_name = project_dir.name

    with open(readme_path, "w") as f:
        f.write(f"# {project_name}\n\n")
        f.write("## Description\n\n")
        f.write("Add your project description here.\n\n")
        f.write("## Installation\n\n")
        f.write("\n")
        f.write("pip install -e .\n")
        f.write("\n\n")
        f.write("## Usage\n\n")
        f.write("Add usage examples here.\n")

    logger.info(f"Created README.md file at {readme_path}")


def main():
    # Check for pyproject.toml in the current working directory
    # If we're in the scripts directory, we need to check the parent directory
    current_dir = Path.cwd()
    script_dir = Path(__file__).parent

    # If the current directory is the scripts directory, look in the parent directory
    if current_dir.samefile(script_dir):
        project_dir = current_dir.parent
    else:
        project_dir = current_dir

    pyproject_path = project_dir / "pyproject.toml"

    if not check_file_exists(str(pyproject_path)):
        raise RuntimeError(
            "pyproject.toml file is missing. Cannot proceed with virtual environment setup."
        )

    # Check for README.md in the project directory
    readme_path = project_dir / "README.md"
    if not check_file_exists(str(readme_path)):
        logger.info("README.md not found. Creating a basic README.md file.")
        create_readme(project_dir)
    else:
        logger.info("README.md found in the project directory.")

    # If pyproject.toml exists, continue with the setup
    venv_path = set_path()
    init_venv(venv_path)

    return


if __name__ == "__main__":
    sys.exit(main())
