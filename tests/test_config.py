"""Tests for plinth configuration."""

import pytest

from pedestal.config import pedestalConfig, plinth_config, DatabaseDriver, AuthConfig


class TestPlinthConfig:
    """Test the PlinthConfig class."""

    def test_state_filename(self) -> None:
        """Test that state filename is correct."""
        assert plinth_config.STATE_FILENAME == ".plinth.json"

    def test_directory_constants(self) -> None:
        """Test directory constants."""
        assert plinth_config.SOURCE_DIR == "src"
        assert plinth_config.API_DIR == "api"
        assert plinth_config.CORE_DIR == "core"
        assert plinth_config.MODELS_DIR == "models"
        assert plinth_config.TESTS_DIR == "tests"

    def test_version(self) -> None:
        """Test version is set."""
        assert plinth_config.VERSION == "1.0.0"

    def test_database_drivers_exist(self) -> None:
        """Test that database drivers are configured."""
        assert "postgres" in plinth_config.DATABASE_DRIVERS
        assert "mysql" in plinth_config.DATABASE_DRIVERS
        assert "sqlite" in plinth_config.DATABASE_DRIVERS

    def test_postgres_driver(self) -> None:
        """Test PostgreSQL driver configuration."""
        driver = plinth_config.DATABASE_DRIVERS["postgres"]
        assert driver.name == "asyncpg"
        assert "asyncpg" in driver.package
        assert driver.url_prefix == "postgresql+asyncpg"

    def test_mysql_driver(self) -> None:
        """Test MySQL driver configuration."""
        driver = plinth_config.DATABASE_DRIVERS["mysql"]
        assert driver.name == "aiomysql"
        assert "aiomysql" in driver.package
        assert driver.url_prefix == "mysql+aiomysql"

    def test_sqlite_driver(self) -> None:
        """Test SQLite driver configuration."""
        driver = plinth_config.DATABASE_DRIVERS["sqlite"]
        assert driver.name == "aiosqlite"
        assert "aiosqlite" in driver.package
        assert driver.url_prefix == "sqlite+aiosqlite"

    def test_auth_types_exist(self) -> None:
        """Test that auth types are configured."""
        assert "jwt" in plinth_config.AUTH_TYPES
        assert "session" in plinth_config.AUTH_TYPES

    def test_jwt_auth(self) -> None:
        """Test JWT auth configuration."""
        auth = plinth_config.AUTH_TYPES["jwt"]
        assert auth.name == "jwt"
        assert "pyjwt" in auth.packages[0]
        assert "passlib" in auth.packages[1]

    def test_session_auth(self) -> None:
        """Test session auth configuration."""
        auth = plinth_config.AUTH_TYPES["session"]
        assert auth.name == "session"
        assert "itsdangerous" in auth.packages[0]
        assert "passlib" in auth.packages[1]

    def test_available_modules(self) -> None:
        """Test available modules are defined."""
        expected_modules = [
            "postgres",
            "mysql",
            "sqlite",
            "redis",
            "auth-jwt",
            "auth-session",
        ]
        for module in expected_modules:
            assert module in plinth_config.AVAILABLE_MODULES

    def test_base_dependencies(self) -> None:
        """Test base dependencies are configured."""
        deps = plinth_config.BASE_DEPENDENCIES
        assert any("fastapi" in dep for dep in deps)
        assert any("uvicorn" in dep for dep in deps)
        assert any("pydantic" in dep for dep in deps)

    def test_optional_dependencies(self) -> None:
        """Test optional dependencies are configured."""
        assert "redis" in plinth_config.REDIS_DEPENDENCY
        assert "sqlalchemy" in plinth_config.SQLALCHEMY_DEPENDENCY
        assert "alembic" in plinth_config.ALEMBIC_DEPENDENCY


class TestDatabaseDriver:
    """Test the DatabaseDriver dataclass."""

    def test_creation(self) -> None:
        """Test creating a DatabaseDriver."""
        driver = DatabaseDriver(
            name="testdriver",
            package="test-package>=1.0.0",
            url_prefix="test+driver",
        )
        assert driver.name == "testdriver"
        assert driver.package == "test-package>=1.0.0"
        assert driver.url_prefix == "test+driver"

    def test_frozen(self) -> None:
        """Test that DatabaseDriver is immutable."""
        driver = DatabaseDriver(
            name="testdriver",
            package="test-package>=1.0.0",
            url_prefix="test+driver",
        )
        with pytest.raises(AttributeError):
            driver.name = "newname"


class TestAuthConfig:
    """Test the AuthConfig dataclass."""

    def test_creation(self) -> None:
        """Test creating an AuthConfig."""
        auth = AuthConfig(
            name="testauth",
            packages=["package1", "package2"],
        )
        assert auth.name == "testauth"
        assert auth.packages == ["package1", "package2"]

    def test_frozen(self) -> None:
        """Test that AuthConfig is immutable."""
        auth = AuthConfig(
            name="testauth",
            packages=["package1"],
        )
        with pytest.raises(AttributeError):
            auth.name = "newname"
