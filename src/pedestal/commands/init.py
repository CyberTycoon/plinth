"""Initialize command implementation."""

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from pedestal.config import pedestal_config
from pedestal.exceptions import (
    ProjectExistsError,
    InvalidConfigError,
)
from pedestal.logger import logger
from pedestal.packages import PackageManager
from pedestal.state import StateManager
from pedestal.templates import ProjectBuilder, TemplateRenderer


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize the configuration.

    Args:
        config: Raw configuration dictionary

    Returns:
        Validated and normalized configuration

    Raises:
        InvalidConfigError: If configuration is invalid
    """
    # Set defaults
    config.setdefault("project_name", "my-app")

    # Validate database type
    db_type = config.get("db_type")
    if db_type and db_type not in pedestal_config.DATABASE_DRIVERS:
        valid = list(pedestal_config.DATABASE_DRIVERS.keys())
        raise InvalidConfigError("db", f"'{db_type}' not in {valid}")

    # Set driver defaults based on database
    if db_type and not config.get("db_driver"):
        driver = pedestal_config.DATABASE_DRIVERS[db_type]
        config["db_driver"] = driver.name

    # Validate auth type
    auth_type = config.get("auth_type")
    if auth_type and auth_type not in pedestal_config.AUTH_TYPES:
        valid = list(pedestal_config.AUTH_TYPES.keys())
        raise InvalidConfigError("auth", f"'{auth_type}' not in {valid}")

    # Determine if async is enabled
    driver = config.get("db_driver", "")
    config["async_enabled"] = driver in ("asyncpg", "aiomysql", "aiosqlite")

    return config


def build_project_context(config: dict[str, Any]) -> dict[str, Any]:
    """Build the complete project context for templating.

    Args:
        config: Validated configuration

    Returns:
        Complete context dictionary
    """
    return {
        "project_name": config["project_name"],
        "version": "0.1.0",
        "db_type": config.get("db_type"),
        "db_driver": config.get("db_driver"),
        "auth_type": config.get("auth_type"),
        "async_enabled": config.get("async_enabled", False),
        "use_redis": config.get("use_redis", False),
        "use_docker": config.get("use_docker", False),
        "use_linting": config.get("use_linting", True),
    }


def register_modules(state_manager: StateManager, config: dict[str, Any]) -> None:
    """Register installed modules in state.

    Args:
        state_manager: State manager instance
        config: Configuration dictionary
    """
    if config.get("db_type"):
        state_manager.add_module(config["db_type"], "database")
        logger.info(f"Registered module: {config['db_type']}")

    if config.get("auth_type"):
        module_name = f"auth-{config['auth_type']}"
        state_manager.add_module(module_name, "auth")
        logger.info(f"Registered module: {module_name}")

    if config.get("use_redis"):
        state_manager.add_module("redis", "cache")
        logger.info("Registered module: redis")


def init_project(config: dict[str, Any], console: Console) -> None:
    """Initialize a new FastAPI project.

    Args:
        config: Configuration dictionary
        console: Rich console for output

    Raises:
        ProjectExistsError: If project directory already exists
        InvalidConfigError: If configuration is invalid
    """
    # Validate configuration
    config = validate_config(config)
    project_name = config["project_name"]
    project_path = Path(project_name).resolve()

    # Check if directory exists
    if project_path.exists():
        raise ProjectExistsError(project_name)

    console.print(
        Panel.fit(
            f"[bold cyan]🪨 Plinth[/bold cyan] - Creating project: [yellow]{project_name}[/yellow]",
            border_style="cyan",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scaffolding project...", total=None)

        # Create project directory
        project_path.mkdir(parents=True)
        logger.success(f"Created project directory: {project_path}")

        # Initialize state
        state_manager = StateManager(project_path)
        extra_config = {
            "db_type": config.get("db_type"),
            "db_driver": config.get("db_driver"),
            "auth_type": config.get("auth_type"),
            "async_enabled": config.get("async_enabled"),
            "docker_enabled": config.get("use_docker"),
            "redis_enabled": config.get("use_redis"),
        }
        state_manager.init(project_name, extra_config)

        # Build project
        context = build_project_context(config)
        renderer = TemplateRenderer()
        builder = ProjectBuilder(renderer, console)
        builder.build(project_path, context)

        # Register modules in state
        register_modules(state_manager, config)

        progress.update(task, completed=True)

    # Install dependencies
    package_manager = PackageManager(project_path, config.get("skip_uv", False))
    package_manager.install_dependencies()

    # Display next steps
    console.print("\n[bold green]✅ Project created successfully![/bold green]\n")

    next_steps = f"""[bold]Next Steps:[/bold]
    cd {project_name}
    uv run uvicorn src.main:app --reload
    
[dim]# Or using your preferred method:[/dim]
    python -m uvicorn src.main:app --reload
    """

    console.print(Panel(next_steps, title="🚀 Get Started", border_style="green"))

