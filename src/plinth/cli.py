"""Main CLI entry point for Plinth."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from plinth import __version__
from plinth.commands.init import init_project
from plinth.commands.add import add_module
from plinth.commands.list import list_modules
from plinth.commands.remove import remove_module
from plinth.commands.doctor import run_doctor
from plinth.config import plinth_config
from plinth.exceptions import PlinthError
from plinth.logger import logger

# Create Typer app
app = typer.Typer(
    name="plinth",
    help="🪨 A high-performance CLI scaffolding tool for FastAPI",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Console for output - force unicode on Windows
console = Console(legacy_windows=False, force_terminal=True)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(
            f"[bold cyan]Plinth[/bold cyan] version [green]{__version__}[/green]"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Plinth: The rock-solid foundation for FastAPI applications."""
    pass


@app.command()
def init(
    name: str = typer.Argument(
        ...,
        help="Name of the project to create",
    ),
    db: Optional[str] = typer.Option(
        None,
        "--db",
        help=f"Database type: {', '.join(plinth_config.DATABASE_DRIVERS.keys())}",
        case_sensitive=False,
    ),
    driver: Optional[str] = typer.Option(
        None,
        "--driver",
        help="Database driver: asyncpg, psycopg, aiomysql, aiosqlite",
        case_sensitive=False,
    ),
    auth: Optional[str] = typer.Option(
        None,
        "--auth",
        help=f"Authentication type: {', '.join(plinth_config.AUTH_TYPES.keys())}",
        case_sensitive=False,
    ),
    redis: bool = typer.Option(
        False,
        "--redis",
        help="Include Redis caching",
    ),
    docker: bool = typer.Option(
        False,
        "--docker",
        help="Generate Dockerfile",
    ),
    linting: bool = typer.Option(
        True,
        "--linting/--no-linting",
        help="Include linting configs",
    ),
    skip_uv: bool = typer.Option(
        False,
        "--skip-uv",
        help="Skip uv dependency installation",
    ),
) -> None:
    """🚀 Initialize a new FastAPI project with Plinth."""
    try:
        config = {
            "project_name": name,
            "db_type": db,
            "db_driver": driver,
            "auth_type": auth,
            "use_redis": redis,
            "use_docker": docker,
            "use_linting": linting,
            "skip_uv": skip_uv,
        }
        init_project(config, console)
    except PlinthError as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def add(
    module: str = typer.Argument(
        ...,
        help="Module to add (e.g., redis, auth-jwt, postgres)",
    ),
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        help="Path to the project directory",
    ),
    skip_uv: bool = typer.Option(
        False,
        "--skip-uv",
        help="Skip uv dependency installation",
    ),
) -> None:
    """➕ Add a feature module to an existing project."""
    try:
        add_module(module, path, skip_uv, console)
    except PlinthError as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def remove(
    module: str = typer.Argument(
        ...,
        help="Module to remove",
    ),
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        help="Path to the project directory",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """➖ Remove a feature module from the project."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to remove '{module}'?")
        if not confirm:
            console.print("[yellow]Operation cancelled.[/yellow]")
            raise typer.Exit()

    try:
        remove_module(module, path, console)
    except PlinthError as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command(name="list")
def list_cmd(
    installed: bool = typer.Option(
        False,
        "--installed",
        "-i",
        help="Show only installed modules",
    ),
    available: bool = typer.Option(
        False,
        "--available",
        "-a",
        help="Show only available modules",
    ),
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        help="Path to the project directory",
    ),
) -> None:
    """📋 List installed and available modules."""
    try:
        list_modules(path, installed, available, console)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def doctor(
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        help="Path to the project directory",
    ),
) -> None:
    """🔍 Run diagnostics on the project."""
    try:
        issues = run_doctor(path, console)
        if issues:
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
