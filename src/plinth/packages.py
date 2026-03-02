"""Package management utilities for Plinth."""

import subprocess
from pathlib import Path

from plinth.logger import logger


class PackageManager:
    """Handles package installation using uv."""

    def __init__(self, project_path: Path, skip_uv: bool = False):
        self.project_path = Path(project_path)
        self.skip_uv = skip_uv

    def install_dependencies(self) -> bool:
        """Install project dependencies using uv sync.

        Returns:
            True if successful, False otherwise
        """
        if self.skip_uv:
            logger.info("Skipping uv sync (--skip-uv flag)")
            return True

        try:
            logger.info("Installing dependencies with uv...")
            subprocess.run(
                ["uv", "sync"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.success("Dependencies installed successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(f"uv sync failed: {e.stderr}")
            logger.info("You can run 'uv sync' manually later")
            return False

        except FileNotFoundError:
            logger.warning("uv not found. Please install dependencies manually.")
            return False

    def add_package(self, package: str) -> bool:
        """Add a package to the project.

        Args:
            package: Package specification (e.g., "redis>=5.0.0")

        Returns:
            True if successful, False otherwise
        """
        if self.skip_uv:
            logger.info(f"Skipping uv add {package} (--skip-uv flag)")
            return True

        try:
            logger.info(f"Adding package: {package}")
            subprocess.run(
                ["uv", "add", package],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.success(f"Added {package}")
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to add {package}: {e.stderr}")
            return False

        except FileNotFoundError:
            logger.warning(f"uv not found. Add '{package}' manually to pyproject.toml")
            return False

    def add_packages(self, packages: list[str]) -> bool:
        """Add multiple packages to the project.

        Args:
            packages: List of package specifications

        Returns:
            True if all packages were added successfully
        """
        if not packages:
            return True

        success = True
        for package in packages:
            if not self.add_package(package):
                success = False

        return success
