"""Remove command implementation."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from pedestal.exceptions import (
    NotAPedestalProjectError,
    ModuleNotFoundError,
)
from pedestal.logger import logger
from pedestal.state import StateManager


def remove_module(
    module_name: str,
    project_path: Path,
    console: Console,
) -> None:
    """Remove a module from the project.

    Args:
        module_name: Name of module to remove
        project_path: Path to project directory
        console: Rich console for output

    Raises:
        NotAPedestalProjectError: If not in a Pedestal project
        ModuleNotFoundError: If module not installed
    """
    project_path = Path(project_path).resolve()

    # Verify this is a Pedestal project
    state_manager = StateManager(project_path)
    if not state_manager.exists():
        raise NotAPedestalProjectError(str(project_path))

    # Check if module is installed
    state = state_manager.load()
    if not state.has_module(module_name):
        raise ModuleNotFoundError(module_name)

    console.print(
        Panel.fit(
            f"[bold yellow]➖ Removing module:[/bold yellow] [red]{module_name}[/red]",
            border_style="yellow",
        )
    )

    # Remove from state
    state_manager.remove_module(module_name)
    logger.success(f"Removed module from state: {module_name}")

    console.print(
        f"\n[bold green]✅ Module '{module_name}' removed successfully![/bold green]\n"
    )

    logger.info("Note: Files and dependencies are not automatically removed.")
    logger.info("Please manually remove any unwanted code and update pyproject.toml.")

