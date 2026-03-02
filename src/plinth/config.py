"""Configuration and constants for Plinth."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseDriver:
    """Database driver configuration."""

    name: str
    package: str
    url_prefix: str


@dataclass(frozen=True)
class AuthConfig:
    """Authentication configuration."""

    name: str
    packages: list[str]


class PlinthConfig:
    """Global configuration for Plinth."""

    # State file
    STATE_FILENAME = ".plinth.json"

    # Directories
    SOURCE_DIR = "src"
    API_DIR = "api"
    CORE_DIR = "core"
    MODELS_DIR = "models"
    TESTS_DIR = "tests"

    # Version
    VERSION = "1.0.0"

    # Database drivers
    DATABASE_DRIVERS = {
        "postgres": DatabaseDriver(
            name="asyncpg",
            package="asyncpg>=0.29.0",
            url_prefix="postgresql+asyncpg",
        ),
        "mysql": DatabaseDriver(
            name="aiomysql",
            package="aiomysql>=0.2.0",
            url_prefix="mysql+aiomysql",
        ),
        "sqlite": DatabaseDriver(
            name="aiosqlite",
            package="aiosqlite>=0.20.0",
            url_prefix="sqlite+aiosqlite",
        ),
    }

    # Authentication types
    AUTH_TYPES = {
        "jwt": AuthConfig(
            name="jwt",
            packages=["pyjwt>=2.8.0", "passlib[bcrypt]>=1.7.4"],
        ),
        "session": AuthConfig(
            name="session",
            packages=["itsdangerous>=2.1.0", "passlib[bcrypt]>=1.7.4"],
        ),
    }

    # Available modules
    AVAILABLE_MODULES = {
        "postgres": "PostgreSQL database with asyncpg driver",
        "mysql": "MySQL database with aiomysql driver",
        "sqlite": "SQLite database with aiosqlite driver",
        "redis": "Redis caching and session storage",
        "auth-jwt": "JWT-based authentication",
        "auth-session": "Session-based authentication",
    }

    # Base dependencies
    BASE_DEPENDENCIES = [
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.29.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
    ]

    # Optional dependencies
    REDIS_DEPENDENCY = "redis[hiredis]>=5.0.0"
    SQLALCHEMY_DEPENDENCY = "sqlalchemy>=2.0.0"
    ALEMBIC_DEPENDENCY = "alembic>=1.13.0"


# Global config instance
plinth_config = PlinthConfig()
