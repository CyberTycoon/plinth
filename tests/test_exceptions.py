"""Tests for plinth exceptions."""

import pytest

from plinth.exceptions import (
    PlinthError,
    ProjectExistsError,
    NotAPlinthProjectError,
    ModuleAlreadyInstalledError,
    ModuleNotFoundError,
    InvalidConfigError,
    TemplateRenderError,
    CodeInjectionError,
)


class TestPlinthError:
    """Test the base PlinthError class."""

    def test_is_exception(self) -> None:
        """Test that PlinthError is an Exception subclass."""
        assert issubclass(PlinthError, Exception)

    def test_can_be_raised(self) -> None:
        """Test that PlinthError can be raised and caught."""
        with pytest.raises(PlinthError):
            raise PlinthError("test error")

    def test_message(self) -> None:
        """Test that error message is preserved."""
        try:
            raise PlinthError("custom message")
        except PlinthError as e:
            assert str(e) == "custom message"

    def test_code_attribute(self) -> None:
        """Test that error code is stored."""
        err = PlinthError("message", code="CUSTOM_CODE")
        assert err.code == "CUSTOM_CODE"

    def test_default_code(self) -> None:
        """Test that default code is GENERIC_ERROR."""
        err = PlinthError("message")
        assert err.code == "GENERIC_ERROR"


class TestProjectExistsError:
    """Test ProjectExistsError."""

    def test_is_plinth_error(self) -> None:
        """Test that it's a PlinthError subclass."""
        assert issubclass(ProjectExistsError, PlinthError)

    def test_message_contains_project_name(self) -> None:
        """Test error message contains the project name."""
        err = ProjectExistsError("my-project")
        assert "my-project" in str(err)
        assert "already exists" in str(err)

    def test_code(self) -> None:
        """Test error code."""
        err = ProjectExistsError("test")
        assert err.code == "PROJECT_EXISTS"


class TestNotAPlinthProjectError:
    """Test NotAPlinthProjectError."""

    def test_is_plinth_error(self) -> None:
        """Test that it's a PlinthError subclass."""
        assert issubclass(NotAPlinthProjectError, PlinthError)

    def test_default_path(self) -> None:
        """Test default path is '.'"""
        err = NotAPlinthProjectError()
        assert "." in str(err)

    def test_custom_path(self) -> None:
        """Test custom path in error message."""
        err = NotAPlinthProjectError("/path/to/project")
        assert "/path/to/project" in str(err)
        assert "found" in str(err)

    def test_code(self) -> None:
        """Test error code."""
        err = NotAPlinthProjectError()
        assert err.code == "NOT_A_PLINTH_PROJECT"


class TestModuleAlreadyInstalledError:
    """Test ModuleAlreadyInstalledError."""

    def test_is_plinth_error(self) -> None:
        """Test that it's a PlinthError subclass."""
        assert issubclass(ModuleAlreadyInstalledError, PlinthError)

    def test_message_contains_module_name(self) -> None:
        """Test that error message contains the module name."""
        err = ModuleAlreadyInstalledError("postgres")
        assert "postgres" in str(err)
        assert "already installed" in str(err)

    def test_code(self) -> None:
        """Test error code."""
        err = ModuleAlreadyInstalledError("test")
        assert err.code == "MODULE_ALREADY_INSTALLED"


class TestModuleNotFoundError:
    """Test ModuleNotFoundError."""

    def test_is_plinth_error(self) -> None:
        """Test that it's a PlinthError subclass."""
        assert issubclass(ModuleNotFoundError, PlinthError)

    def test_message_contains_module_name(self) -> None:
        """Test that error message contains the module name."""
        err = ModuleNotFoundError("redis")
        assert "redis" in str(err)
        assert "not found" in str(err)

    def test_code(self) -> None:
        """Test error code."""
        err = ModuleNotFoundError("test")
        assert err.code == "MODULE_NOT_FOUND"


class TestInvalidConfigError:
    """Test InvalidConfigError."""

    def test_is_plinth_error(self) -> None:
        """Test that it's a PlinthError subclass."""
        assert issubclass(InvalidConfigError, PlinthError)

    def test_message_contains_field_and_value(self) -> None:
        """Test that error message contains field and value."""
        err = InvalidConfigError("database", "invalid")
        assert "database" in str(err)
        assert "invalid" in str(err)
        assert "Invalid configuration" in str(err)

    def test_code(self) -> None:
        """Test error code."""
        err = InvalidConfigError("field", "value")
        assert err.code == "INVALID_CONFIG"


class TestTemplateRenderError:
    """Test TemplateRenderError."""

    def test_is_plinth_error(self) -> None:
        """Test that it's a PlinthError subclass."""
        assert issubclass(TemplateRenderError, PlinthError)

    def test_message_contains_template_and_reason(self) -> None:
        """Test that error message contains template name and reason."""
        err = TemplateRenderError("base", "missing variable")
        assert "base" in str(err)
        assert "missing variable" in str(err)
        assert "Failed to render" in str(err)

    def test_code(self) -> None:
        """Test error code."""
        err = TemplateRenderError("test", "reason")
        assert err.code == "TEMPLATE_RENDER_ERROR"


class TestCodeInjectionError:
    """Test CodeInjectionError."""

    def test_is_plinth_error(self) -> None:
        """Test that it's a PlinthError subclass."""
        assert issubclass(CodeInjectionError, PlinthError)

    def test_message_contains_file_and_reason(self) -> None:
        """Test that error message contains target file and reason."""
        err = CodeInjectionError("main.py", "syntax error")
        assert "main.py" in str(err)
        assert "syntax error" in str(err)
        assert "inject code" in str(err)

    def test_code(self) -> None:
        """Test error code."""
        err = CodeInjectionError("test.py", "error")
        assert err.code == "CODE_INJECTION_ERROR"


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_all_inherit_from_plinth_error(self) -> None:
        """Test all exceptions inherit from PlinthError."""
        exceptions = [
            ProjectExistsError,
            NotAPlinthProjectError,
            ModuleAlreadyInstalledError,
            ModuleNotFoundError,
            InvalidConfigError,
            TemplateRenderError,
            CodeInjectionError,
        ]
        for exc_class in exceptions:
            assert issubclass(
                exc_class, PlinthError
            ), f"{exc_class} should inherit from PlinthError"
