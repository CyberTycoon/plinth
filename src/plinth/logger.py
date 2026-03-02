"""Logging utilities for Plinth."""

import logging
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

# Global console instance
console = Console()


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging with Rich formatting.

    Args:
        verbose: Enable debug logging if True

    Returns:
        Configured logger instance
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
            )
        ],
    )

    return logging.getLogger("plinth")


class PlinthLogger:
    """Structured logging for Plinth operations."""

    def __init__(self, name: str = "plinth"):
        self._logger = logging.getLogger(name)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._logger.error(message, extra=kwargs)

    def success(self, message: str) -> None:
        """Log success message with emoji."""
        console.print(f"[bold green]✓[/bold green] {message}")

    def failure(self, message: str) -> None:
        """Log failure message with emoji."""
        console.print(f"[bold red]✗[/bold red] {message}")


# Global logger instance
logger = PlinthLogger()
