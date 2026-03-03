"""Custom exceptions for Plinth."""


class PedestalError(Exception):
    """Base exception for all Plinth errors."""

    def __init__(self, message: str, code: str = "GENERIC_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ProjectExistsError(PedestalError):
    """Raised when project directory already exists."""

    def __init__(self, project_name: str):
        super().__init__(
            message=f"Project '{project_name}' already exists", code="PROJECT_EXISTS"
        )


class NotAPedestalProjectError(PedestalError):
    """Raised when operation is run outside a Pedestal project."""

    def __init__(self, path: str = "."):
        super().__init__(
            message=f"No Pedestal project found at '{path}'", code="NOT_A_PLINTH_PROJECT"
        )


class ModuleAlreadyInstalledError(PedestalError):
    """Raised when trying to install an already installed module."""

    def __init__(self, module_name: str):
        super().__init__(
            message=f"Module '{module_name}' is already installed",
            code="MODULE_ALREADY_INSTALLED",
        )


class ModuleNotFoundError(PedestalError):
    """Raised when a module is not found."""

    def __init__(self, module_name: str):
        super().__init__(
            message=f"Module '{module_name}' not found", code="MODULE_NOT_FOUND"
        )


class InvalidConfigError(PedestalError):
    """Raised when configuration is invalid."""

    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"Invalid configuration: '{field}' = '{value}'",
            code="INVALID_CONFIG",
        )


class TemplateRenderError(PedestalError):
    """Raised when template rendering fails."""

    def __init__(self, template_name: str, reason: str):
        super().__init__(
            message=f"Failed to render template '{template_name}': {reason}",
            code="TEMPLATE_RENDER_ERROR",
        )


class CodeInjectionError(PedestalError):
    """Raised when code injection fails."""

    def __init__(self, target_file: str, reason: str):
        super().__init__(
            message=f"Failed to inject code into '{target_file}': {reason}",
            code="CODE_INJECTION_ERROR",
        )

