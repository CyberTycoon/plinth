"""Template rendering system for Plinth."""

from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape
from rich.console import Console

from plinth.exceptions import TemplateRenderError
from plinth.logger import logger


class TemplateRenderer:
    """Renders Jinja2 templates for project scaffolding."""

    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir:
            loader = FileSystemLoader(str(templates_dir))
        else:
            loader = PackageLoader("plinth", "templates")

        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of the template file
            context: Dictionary of variables for template rendering

        Returns:
            Rendered template as string

        Raises:
            TemplateRenderError: If template cannot be rendered
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise TemplateRenderError(template_name, str(e)) from e

    def render_to_file(
        self,
        template_name: str,
        output_path: Path,
        context: dict[str, Any],
    ) -> None:
        """Render a template and write it to a file.

        Args:
            template_name: Name of the template file
            output_path: Path where rendered file should be written
            context: Dictionary of variables for template rendering
        """
        content = self.render(template_name, context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Created: {output_path}")


class ProjectBuilder:
    """Builds FastAPI projects from templates."""

    def __init__(self, renderer: TemplateRenderer, console: Console):
        self.renderer = renderer
        self.console = console

    def build(self, project_path: Path, config: dict[str, Any]) -> None:
        """Build a complete project.

        Args:
            project_path: Root directory for the project
            config: Build configuration dictionary
        """
        self._create_directories(project_path)
        self._render_base_files(project_path, config)

        if config.get("db_type"):
            self._render_database_files(project_path, config)

        if config.get("auth_type"):
            self._render_auth_files(project_path, config)

        if config.get("use_redis"):
            self._render_redis_files(project_path, config)

    def _create_directories(self, project_path: Path) -> None:
        """Create the standard project directory structure."""
        dirs = [
            project_path / "src" / "api" / "v1",
            project_path / "src" / "models",
            project_path / "src" / "core",
            project_path / "tests",
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path.relative_to(project_path)}")

    def _render_base_files(self, project_path: Path, config: dict[str, Any]) -> None:
        """Render base project files."""
        files = [
            ("base/pyproject.toml.j2", project_path / "pyproject.toml"),
            ("base/README.md.j2", project_path / "README.md"),
            ("base/.env.example", project_path / ".env.example"),
            ("base/.gitignore", project_path / ".gitignore"),
            ("base/src/__init__.py", project_path / "src" / "__init__.py"),
            ("base/src/main.py.j2", project_path / "src" / "main.py"),
            ("base/src/core/config.py.j2", project_path / "src" / "core" / "config.py"),
            (
                "base/src/core/registry.py",
                project_path / "src" / "core" / "registry.py",
            ),
            (
                "base/src/core/__init__.py",
                project_path / "src" / "core" / "__init__.py",
            ),
            ("base/src/api/__init__.py", project_path / "src" / "api" / "__init__.py"),
            (
                "base/src/api/v1/__init__.py",
                project_path / "src" / "api" / "v1" / "__init__.py",
            ),
            (
                "base/src/api/v1/health.py",
                project_path / "src" / "api" / "v1" / "health.py",
            ),
            (
                "base/src/models/__init__.py",
                project_path / "src" / "models" / "__init__.py",
            ),
            ("base/tests/__init__.py", project_path / "tests" / "__init__.py"),
        ]

        for template_name, output_path in files:
            try:
                self.renderer.render_to_file(template_name, output_path, config)
            except TemplateRenderError as e:
                logger.warning(f"Could not render {template_name}: {e}")

    def _render_database_files(
        self, project_path: Path, config: dict[str, Any]
    ) -> None:
        """Render database-specific files."""
        db_type = config.get("db_type")
        if not db_type:
            return

        template_map = {
            "postgres": "base/src/core/database.py.j2",
            "mysql": "base/src/core/database.py.j2",
            "sqlite": "base/src/core/database.py.j2",
        }

        template_name = template_map.get(db_type)
        if template_name:
            output_path = project_path / "src" / "core" / "database.py"
            self.renderer.render_to_file(template_name, output_path, config)

    def _render_auth_files(self, project_path: Path, config: dict[str, Any]) -> None:
        """Render authentication-specific files."""
        auth_type = config.get("auth_type")
        if not auth_type:
            return

        # Render auth core
        self.renderer.render_to_file(
            "base/src/core/auth.py.j2",
            project_path / "src" / "core" / "auth.py",
            config,
        )

        # Render auth routes
        self.renderer.render_to_file(
            f"base/src/api/v1/auth_{auth_type}.py.j2",
            project_path / "src" / "api" / "v1" / "auth.py",
            config,
        )

    def _render_redis_files(self, project_path: Path, config: dict[str, Any]) -> None:
        """Render Redis-specific files."""
        self.renderer.render_to_file(
            "base/src/core/cache.py.j2",
            project_path / "src" / "core" / "cache.py",
            config,
        )
