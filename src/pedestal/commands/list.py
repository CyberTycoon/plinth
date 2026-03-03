"""List command implementation."""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from pedestal.config import pedestal_config
from pedestal.logger import logger
from pedestal.state import StateManager


def list_modules(
    project_path: Path,
    show_installed: bool,
    show_available: bool,
    console: Console,
) -> None:
    """List installed and/or available modules.

    Args:
        project_path: Path to project directory
        show_installed: Show only installed modules
        show_available: Show only available modules
        console: Rich console for output
    """
    project_path = Path(project_path).resolve()
    state_manager = StateManager(project_path)

    # Determine what to show
    show_both = not show_installed and not show_available

    if show_installed or show_both:
        if state_manager.exists():
            state = state_manager.load()

            if state.modules:
                table = Table(
                    title=f"Installed Modules in '{state.project_name}'",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Type", style="magenta")
                table.add_column("Version", style="green")
                table.add_column("Installed At", style="dim")

                for module in state.modules:
                    table.add_row(
                        module.name,
                        module.type,
                        module.version,
                        module.installed_at[:10],  # Just the date
                    )

                console.print(table)
            else:
                console.print("[dim]No modules installed yet.[/dim]")
        else:
            if show_installed:
                logger.warning("No Pedestal project found")

    if show_available or show_both:
        if show_both and state_manager.exists():
            console.print()  # Add spacing

        table = Table(
            title="Available Modules",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        for name, description in pedestal_config.AVAILABLE_MODULES.items():
            table.add_row(name, description)

        console.print(table)

