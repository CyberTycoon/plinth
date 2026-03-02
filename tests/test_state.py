"""Tests for plinth state management."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from plinth.state import ModuleInfo, ProjectState, StateManager
from plinth.config import plinth_config
from plinth.exceptions import NotAPlinthProjectError, ModuleAlreadyInstalledError


class TestModuleInfo:
    """Test the ModuleInfo dataclass."""

    def test_creation(self) -> None:
        """Test creating a ModuleInfo instance."""
        now = datetime.now().isoformat()
        module = ModuleInfo(
            name="postgres",
            type="database",
            version="1.0.0",
            installed_at=now,
        )
        assert module.name == "postgres"
        assert module.type == "database"
        assert module.version == "1.0.0"
        assert module.installed_at == now

    def test_to_dict(self) -> None:
        """Test converting ModuleInfo to dict."""
        now = datetime.now().isoformat()
        module = ModuleInfo(
            name="postgres",
            type="database",
            version="1.0.0",
            installed_at=now,
        )
        data = module.to_dict()
        assert data["name"] == "postgres"
        assert data["type"] == "database"
        assert data["version"] == "1.0.0"
        assert data["installed_at"] == now

    def test_from_dict(self) -> None:
        """Test creating ModuleInfo from dict."""
        now = datetime.now().isoformat()
        data = {
            "name": "redis",
            "type": "cache",
            "version": "1.0.0",
            "installed_at": now,
        }
        module = ModuleInfo.from_dict(data)
        assert module.name == "redis"
        assert module.type == "cache"
        assert module.version == "1.0.0"

    def test_default_installed_at(self) -> None:
        """Test that installed_at has a default value."""
        module = ModuleInfo(
            name="test",
            type="test",
            version="1.0.0",
        )
        assert module.installed_at is not None


class TestProjectState:
    """Test the ProjectState dataclass."""

    def test_creation(self) -> None:
        """Test creating a ProjectState instance."""
        state = ProjectState(
            version="1.0.0",
            project_name="test-api",
            created_at=datetime.now().isoformat(),
        )
        assert state.project_name == "test-api"
        assert state.version == "1.0.0"
        assert state.modules == []
        assert state.config == {}

    def test_has_module(self) -> None:
        """Test checking if a module exists."""
        state = ProjectState(
            version="1.0.0",
            project_name="test-api",
            created_at=datetime.now().isoformat(),
        )
        assert state.has_module("postgres") is False

        state.modules.append(
            ModuleInfo(name="postgres", type="database", version="1.0.0")
        )
        assert state.has_module("postgres") is True

    def test_get_module(self) -> None:
        """Test getting a module by name."""
        state = ProjectState(
            version="1.0.0",
            project_name="test-api",
            created_at=datetime.now().isoformat(),
        )
        assert state.get_module("postgres") is None

        state.modules.append(
            ModuleInfo(name="postgres", type="database", version="1.0.0")
        )
        module = state.get_module("postgres")
        assert module is not None
        assert module.name == "postgres"

    def test_add_module(self) -> None:
        """Test adding a module."""
        state = ProjectState(
            version="1.0.0",
            project_name="test-api",
            created_at=datetime.now().isoformat(),
        )
        module = ModuleInfo(name="redis", type="cache", version="1.0.0")
        state.add_module(module)
        assert len(state.modules) == 1
        assert state.has_module("redis")

    def test_add_duplicate_module_raises(self) -> None:
        """Test that adding a duplicate module raises an error."""
        state = ProjectState(
            version="1.0.0",
            project_name="test-api",
            created_at=datetime.now().isoformat(),
        )
        module = ModuleInfo(name="redis", type="cache", version="1.0.0")
        state.add_module(module)

        with pytest.raises(ModuleAlreadyInstalledError):
            state.add_module(module)

    def test_remove_module(self) -> None:
        """Test removing a module."""
        state = ProjectState(
            version="1.0.0",
            project_name="test-api",
            created_at=datetime.now().isoformat(),
        )
        state.modules.append(
            ModuleInfo(name="postgres", type="database", version="1.0.0")
        )

        removed = state.remove_module("postgres")
        assert removed is True
        assert len(state.modules) == 0

        not_removed = state.remove_module("nonexistent")
        assert not_removed is False

    def test_to_dict(self) -> None:
        """Test converting ProjectState to dict."""
        now = datetime.now().isoformat()
        state = ProjectState(
            version="1.0.0",
            project_name="test-api",
            created_at=now,
        )
        data = state.to_dict()
        assert data["project_name"] == "test-api"
        assert data["version"] == "1.0.0"
        assert data["created_at"] == now
        assert data["modules"] == []
        assert data["config"] == {}

    def test_from_dict(self) -> None:
        """Test creating ProjectState from dict."""
        now = datetime.now().isoformat()
        data = {
            "project_name": "test-api",
            "version": "1.0.0",
            "created_at": now,
            "modules": [
                {
                    "name": "postgres",
                    "type": "database",
                    "version": "1.0.0",
                    "installed_at": now,
                }
            ],
            "config": {},
        }
        state = ProjectState.from_dict(data)
        assert state.project_name == "test-api"
        assert len(state.modules) == 1
        assert state.modules[0].name == "postgres"


class TestStateManager:
    """Test the StateManager class."""

    def test_init(self) -> None:
        """Test StateManager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            assert manager.project_path == Path(tmpdir)
            assert manager.state_file == Path(tmpdir) / ".plinth.json"

    def test_exists_no_file(self) -> None:
        """Test exists() returns False when no state file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            assert manager.exists() is False

    def test_exists_with_file(self) -> None:
        """Test exists() returns True when state file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            # Create the state file
            manager.state_file.write_text("{}")
            assert manager.exists() is True

    def test_init_state(self) -> None:
        """Test initializing a new state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            state = manager.init("my-api")
            assert state.project_name == "my-api"
            assert state.version == plinth_config.VERSION
            assert len(state.modules) == 0
            assert manager.exists() is True

    def test_load_raises_when_no_state(self) -> None:
        """Test load() raises when no state file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            with pytest.raises(NotAPlinthProjectError):
                manager.load()

    def test_save_and_load(self) -> None:
        """Test saving and loading state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            state = manager.init("my-api")
            manager.save(state)

            loaded = manager.load()
            assert loaded.project_name == "my-api"
            assert loaded.version == plinth_config.VERSION

    def test_add_module(self) -> None:
        """Test adding a module to state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            manager.init("my-api")

            manager.add_module("postgres", "database", "1.0.0")
            loaded = manager.load()
            assert len(loaded.modules) == 1
            assert loaded.modules[0].name == "postgres"
            assert loaded.modules[0].type == "database"

    def test_remove_module(self) -> None:
        """Test removing a module from state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            manager.init("my-api")
            manager.add_module("redis", "cache", "1.0.0")

            removed = manager.remove_module("redis")
            assert removed is True

            loaded = manager.load()
            assert len(loaded.modules) == 0

            # Removing non-existent returns False
            not_removed = manager.remove_module("nonexistent")
            assert not_removed is False

    def test_load_corrupted_file(self) -> None:
        """Test loading a corrupted state file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(Path(tmpdir))
            manager.state_file.write_text("not valid json")

            with pytest.raises(NotAPlinthProjectError):
                manager.load()
