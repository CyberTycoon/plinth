"""Doctor command implementation for diagnostics."""

from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from plinth.logger import logger
from plinth.state import StateManager


def check_file_exists(path: Path, description: str, issues: List[str]) -> bool:
    """Check if a file exists and record issue if not.

    Args:
        path: Path to check
        description: Description of the file
        issues: List to append issues to

    Returns:
        True if file exists, False otherwise
    """
    if not path.exists():
        issues.append(f"Missing {description}: {path}")
        return False
    return True


def check_directory_structure(project_path: Path, issues: List[str]) -> None:
    """Check the basic project directory structure.

    Args:
        project_path: Root project path
        issues: List to append issues to
    """
    required_dirs = [
        (project_path / "src", "source directory"),
        (project_path / "src" / "api", "API directory"),
        (project_path / "src" / "core", "core directory"),
    ]

    for dir_path, description in required_dirs:
        if not dir_path.exists():
            issues.append(f"Missing {description}: {dir_path}")


def check_module_consistency(
    project_path: Path,
    state_manager: StateManager,
    issues: List[str],
) -> None:
    """Check that installed modules have their files.

    Args:
        project_path: Root project path
        state_manager: State manager instance
        issues: List to append issues to
    """
    state = state_manager.load()

    # Check database modules
    for db in ["postgres", "mysql", "sqlite"]:
        if state.has_module(db):
            db_file = project_path / "src" / "core" / "database.py"
            if not db_file.exists():
                issues.append(f"Module '{db}' installed but database.py not found")

    # Check Redis module
    if state.has_module("redis"):
        cache_file = project_path / "src" / "core" / "cache.py"
        if not cache_file.exists():
            issues.append("Module 'redis' installed but cache.py not found")

    # Check auth modules
    for auth in ["auth-jwt", "auth-session"]:
        if state.has_module(auth):
            auth_file = project_path / "src" / "core" / "auth.py"
            if not auth_file.exists():
                issues.append(f"Module '{auth}' installed but auth.py not found")


def run_doctor(project_path: Path, console: Console) -> List[str]:
    """Run diagnostics on the project.

    Args:
        project_path: Path to project directory
        console: Rich console for output

    Returns:
        List of issues found
    """
    project_path = Path(project_path).resolve()
    issues: List[str] = []

    console.print(
        Panel.fit(
            "[bold cyan]🔍 Running diagnostics...[/bold cyan]",
            border_style="cyan",
        )
    )

    # Check if this is a Plinth project
    state_manager = StateManager(project_path)
    if not state_manager.exists():
        issues.append("No .plinth.json found - not a Plinth project")
    else:
        # Load project state
        try:
            state = state_manager.load()
            console.print(f"[dim]Project:[/dim] {state.project_name}")
        except Exception as e:
            issues.append(f"Failed to load .plinth.json: {e}")

        # Only run additional checks if state loaded successfully
        if not issues:
            # Check state consistency
            if state.project_name != project_path.name:
                issues.append(
                    f"Project name mismatch: {state.project_name} vs {project_path.name}"
                )

            # Check directory structure
            check_directory_structure(project_path, issues)

            # Check core files
            check_file_exists(project_path / "src" / "main.py", "main.py", issues)
            check_file_exists(
                project_path / "src" / "core" / "config.py", "config.py", issues
            )
            check_file_exists(
                project_path / "src" / "core" / "registry.py", "registry.py", issues
            )

            # Check module consistency
            check_module_consistency(project_path, state_manager, issues)

    # Display results
    console.print()
    if issues:
        table = Table(
            title="Issues Found",
            show_header=True,
            header_style="bold red",
        )
        table.add_column("#", style="dim")
        table.add_column("Issue", style="red")

        for i, issue in enumerate(issues, 1):
            table.add_row(str(i), issue)

        console.print(table)
        console.print(f"\n[bold red]✗ Found {len(issues)} issue(s)[/bold red]")
    else:
        console.print("[bold green]✓ All checks passed![/bold green]")

    return issues
