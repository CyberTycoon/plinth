"""State management for Pedestal projects."""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pedestal.config import pedestal_config
from pedestal.exceptions import (
    NotAPedestalProjectError,
    ModuleAlreadyInstalledError,
)


@dataclass
class ModuleInfo:
    """Information about an installed module."""

    name: str
    type: str
    version: str
    installed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModuleInfo":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ProjectState:
    """Project state stored in .pedestal.json."""

    version: str
    project_name: str
    created_at: str
    modules: list[ModuleInfo] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)

    def has_module(self, name: str) -> bool:
        """Check if a module is already installed."""
        return any(m.name == name for m in self.modules)

    def get_module(self, name: str) -> Optional[ModuleInfo]:
        """Get a module by name."""
        for module in self.modules:
            if module.name == name:
                return module
        return None

    def add_module(self, module: ModuleInfo) -> None:
        """Add a module to the project."""
        if self.has_module(module.name):
            raise ModuleAlreadyInstalledError(module.name)
        self.modules.append(module)

    def remove_module(self, name: str) -> bool:
        """Remove a module from the project."""
        for i, module in enumerate(self.modules):
            if module.name == name:
                self.modules.pop(i)
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "project_name": self.project_name,
            "created_at": self.created_at,
            "modules": [m.to_dict() for m in self.modules],
            "config": self.config,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectState":
        """Create from dictionary."""
        modules = [ModuleInfo.from_dict(m) for m in data.get("modules", [])]
        return cls(
            version=data.get("version", pedestal_config.VERSION),
            project_name=data["project_name"],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            modules=modules,
            config=data.get("config", {}),
        )


class StateManager:
    """Manages the .pedestal.json state file."""

    def __init__(self, project_path: Path | str):
        self.project_path = Path(project_path).resolve()
        self.state_file = self.project_path / pedestal_config.STATE_FILENAME

    def exists(self) -> bool:
        """Check if state file exists."""
        return self.state_file.exists()

    def load(self) -> ProjectState:
        """Load project state from file.

        Raises:
            NotAPedestalProjectError: If state file doesn't exist
        """
        if not self.exists():
            raise NotAPedestalProjectError(str(self.project_path))

        try:
            data = json.loads(self.state_file.read_text())
            return ProjectState.from_dict(data)
        except json.JSONDecodeError as e:
            raise NotAPedestalProjectError(
                f"Corrupted state file at {self.project_path}"
            ) from e

    def save(self, state: ProjectState) -> None:
        """Save project state to file."""
        self.state_file.write_text(json.dumps(state.to_dict(), indent=2) + "\n")

    def init(
        self,
        project_name: str,
        extra_config: Optional[dict[str, Any]] = None,
    ) -> ProjectState:
        """Initialize a new project state."""
        state = ProjectState(
            version=pedestal_config.VERSION,
            project_name=project_name,
            created_at=datetime.utcnow().isoformat(),
            config=extra_config or {},
        )
        self.save(state)
        return state

    def add_module(
        self,
        name: str,
        module_type: str,
        version: str = "1.0.0",
    ) -> None:
        """Add a module to the project state."""
        state = self.load()
        module = ModuleInfo(
            name=name,
            type=module_type,
            version=version,
        )
        state.add_module(module)
        self.save(state)

    def remove_module(self, name: str) -> bool:
        """Remove a module from the project state."""
        state = self.load()
        removed = state.remove_module(name)
        if removed:
            self.save(state)
        return removed

