"""Add command implementation for adding modules to projects."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from pedestal.config import pedestal_config
from pedestal.exceptions import (
    NotAPedestalProjectError,
    ModuleAlreadyInstalledError,
    ModuleNotFoundError,
)
from pedestal.injector import CodeInjector
from pedestal.logger import logger
from pedestal.packages import PackageManager
from pedestal.state import StateManager
from pedestal.templates import TemplateRenderer


# Module configuration
MODULE_CONFIG = {
    "redis": {
        "type": "cache",
        "packages": [pedestal_config.REDIS_DEPENDENCY],
        "files": [
            ("modules/redis/cache.py.j2", "src/core/cache.py"),
        ],
    },
    "auth-jwt": {
        "type": "auth",
        "packages": pedestal_config.AUTH_TYPES["jwt"].packages,
        "files": [
            ("modules/auth/jwt/core.py.j2", "src/core/auth.py"),
            ("modules/auth/jwt/routes.py.j2", "src/api/v1/auth.py"),
        ],
        "registry": {
            "import_path": "src.api.v1.auth",
            "router_name": "auth_router",
        },
    },
    "auth-session": {
        "type": "auth",
        "packages": pedestal_config.AUTH_TYPES["session"].packages,
        "files": [
            ("modules/auth/session/core.py.j2", "src/core/auth.py"),
            ("modules/auth/session/routes.py.j2", "src/api/v1/auth.py"),
        ],
        "registry": {
            "import_path": "src.api.v1.auth",
            "router_name": "auth_router",
        },
    },
    "postgres": {
        "type": "database",
        "packages": [
            pedestal_config.SQLALCHEMY_DEPENDENCY,
            pedestal_config.DATABASE_DRIVERS["postgres"].package,
            pedestal_config.ALEMBIC_DEPENDENCY,
        ],
        "files": [
            ("modules/database/postgres.py.j2", "src/core/database.py"),
        ],
    },
    "mysql": {
        "type": "database",
        "packages": [
            pedestal_config.SQLALCHEMY_DEPENDENCY,
            pedestal_config.DATABASE_DRIVERS["mysql"].package,
            pedestal_config.ALEMBIC_DEPENDENCY,
        ],
        "files": [
            ("modules/database/mysql.py.j2", "src/core/database.py"),
        ],
    },
    "sqlite": {
        "type": "database",
        "packages": [
            pedestal_config.SQLALCHEMY_DEPENDENCY,
            pedestal_config.DATABASE_DRIVERS["sqlite"].package,
            pedestal_config.ALEMBIC_DEPENDENCY,
        ],
        "files": [
            ("modules/database/sqlite.py.j2", "src/core/database.py"),
        ],
    },
}


def get_module_config(module_name: str) -> dict:
    """Get configuration for a module.

    Args:
        module_name: Name of the module

    Returns:
        Module configuration dictionary

    Raises:
        ModuleNotFoundError: If module doesn't exist
    """
    if module_name not in MODULE_CONFIG:
        available = list(MODULE_CONFIG.keys())
        raise ModuleNotFoundError(f"{module_name} (available: {available})")
    return MODULE_CONFIG[module_name]


def render_module_files(
    renderer: TemplateRenderer,
    project_path: Path,
    module_config: dict,
    context: dict,
) -> None:
    """Render all files for a module.

    Args:
        renderer: Template renderer instance
        project_path: Root project path
        module_config: Module configuration
        context: Template context
    """
    for template_name, output_relative in module_config.get("files", []):
        output_path = project_path / output_relative
        try:
            renderer.render_to_file(template_name, output_path, context)
        except Exception as e:
            logger.warning(f"Could not render {template_name}: {e}")


def update_registry(
    project_path: Path,
    module_config: dict,
) -> None:
    """Update registry.py with new router if needed.

    Args:
        project_path: Root project path
        module_config: Module configuration
    """
    registry_info = module_config.get("registry")
    if not registry_info:
        return

    registry_path = project_path / "src" / "core" / "registry.py"
    if not registry_path.exists():
        logger.warning("Registry file not found, skipping router injection")
        return

    CodeInjector.inject_router(
        registry_path,
        registry_info["import_path"],
        registry_info["router_name"],
    )


def add_module(
    module_name: str,
    project_path: Path,
    skip_uv: bool,
    console: Console,
) -> None:
    """Add a module to an existing project.

    Args:
        module_name: Name of module to add
        project_path: Path to project directory
        skip_uv: Whether to skip uv operations
        console: Rich console for output

    Raises:
        NotAPedestalProjectError: If not in a Pedestal project
        ModuleAlreadyInstalledError: If module already installed
        ModuleNotFoundError: If module doesn't exist
    """
    project_path = Path(project_path).resolve()

    # Verify this is a Pedestal project
    state_manager = StateManager(project_path)
    if not state_manager.exists():
        raise NotAPedestalProjectError(str(project_path))

    # Get module configuration
    module_config = get_module_config(module_name)

    # Check if already installed
    state = state_manager.load()
    if state.has_module(module_name):
        raise ModuleAlreadyInstalledError(module_name)

    console.print(
        Panel.fit(
            f"[bold cyan]➕ Adding module:[/bold cyan] [yellow]{module_name}[/yellow]",
            border_style="cyan",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Installing {module_name}...", total=None)

        # Load project config for context
        project_state = state_manager.load()
        context = {
            "project_name": project_state.project_name,
            **project_state.config,
        }

        # Render module files
        renderer = TemplateRenderer()
        render_module_files(renderer, project_path, module_config, context)

        # Update registry if needed
        update_registry(project_path, module_config)

        # Register module in state
        state_manager.add_module(
            module_name,
            module_config["type"],
        )

        progress.update(task, completed=True)

    # Install dependencies
    package_manager = PackageManager(project_path, skip_uv)
    for package in module_config.get("packages", []):
        package_manager.add_package(package)

    console.print(
        f"\n[bold green]✅ Module '{module_name}' added successfully![/bold green]\n"
    )

