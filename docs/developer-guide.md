# plinth-cli Developer Guide

> Quick reference for internal developers working on the plinth-cli codebase

---

## Quick Start for Developers

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone <repo>
cd plinth

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run in development mode (no installation needed)
python -m plinth-cli --help

# OR install in editable mode for regular development
pip install -e .
plinth-cli --help
```

### What Each Command Does

#### `pip install -r requirements.txt`

Installs all required Python packages (typer, jinja2, pydantic, libcst, rich, etc.) into your current Python environment.

#### `python -m plinth-cli --help`

Runs plinth-cli as a Python module directly from source code. Useful for quick testing without installation. The `-m` flag tells Python to run the `plinth` package's `__main__.py` file.

#### `pip install -e .`

Installs plinth-cli in **editable (development) mode**:

- `-e` = Editable install (creates a link to source code)
- `.` = Current directory (where `pyproject.toml` is located)
- Changes to source code are immediately reflected without reinstalling
- Makes the `plinth` command available system-wide

#### `plinth-cli --help`

Displays all available CLI commands, their descriptions, and options. After editable install, you can use `plinth` directly instead of `python -m plinth`.

---

## Project Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI (cli.py)                        │
│                    Typer command routing                    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌────────────────┐    ┌──────────────┐
│   Commands   │    │    Core Libs   │    │   Templates  │
├──────────────┤    ├────────────────┤    ├──────────────┤
│ init.py      │    │ state.py         │    │ base/        │
│ add.py       │    │ config.py        │    │ └── *.j2     │
│ remove.py    │    │ injector.py      │    │              │
│ list.py      │    │ packages.py      │    │              │
│ doctor.py    │    │ logger.py        │    │              │
└──────────────┘    │ exceptions.py    │    └──────────────┘
                    └────────────────┘
```

---

## Core Concepts

### 1. The Registry Pattern

**What it is:** A list in `src/core/registry.py` that holds all API routers

**Why we use it:** Allows plinth-cli to inject new routes without touching `main.py`

```python
# This is the magic that makes 'plinth-cli add' work
ROUTERS: list[APIRouter] = []
```

**How injection works:**

1. LibCST parses `registry.py`
2. Finds the `ROUTERS` list
3. Appends new router import + reference
4. Writes back modified code

### 2. State Management

**What it is:** A JSON file (`.plinth.json`) tracking installed modules

**Why we use it:** Prevents duplicate installs and enables diagnostics

```python
# Reading state
state_manager = StateManager(project_path)
state = state_manager.load()  # Returns ProjectState dataclass

# Check if module exists
if state.has_module("redis"):
    raise ModuleAlreadyInstalledError("redis")
```

### 3. Module Configuration

**Where to add new modules:** [`src/plinth/commands/add.py`](src/plinth/commands/add.py:20)

```python
MODULE_CONFIG = {
    "redis": {
        "type": "cache",           # Category for list view
        "packages": ["redis[hiredis]>=5.0.0"],  # uv add these
        "files": [                 # Templates to render
            ("modules/redis/cache.py.j2", "src/core/cache.py"),
        ],
        "registry": {              # If it adds routes
            "import_path": "src.api.v1.auth",
            "router_name": "auth_router",
        },
    },
}
```

### 4. Error Handling

**Pattern:** All errors inherit from `PlinthError`

```python
# Raising errors
raise ProjectExistsError("my-app")

# Catching in CLI
try:
    init_project(config, console)
except PlinthError as e:
    console.print(f"[red]Error:[/red] {e.message}")
    raise typer.Exit(1)
```

---

## Available Modules Reference

### Built-in Modules

| Module           | Type     | What It Creates                                                |
| ---------------- | -------- | -------------------------------------------------------------- |
| **postgres**     | Database | `src/core/database.py` with asyncpg, SQLAlchemy, Alembic       |
| **mysql**        | Database | `src/core/database.py` with aiomysql, SQLAlchemy, Alembic      |
| **sqlite**       | Database | `src/core/database.py` with aiosqlite, file-based              |
| **redis**        | Cache    | `src/core/cache.py` with Redis connection pool                 |
| **auth-jwt**     | Auth     | `src/core/auth.py` + `src/api/v1/auth.py` with JWT tokens      |
| **auth-session** | Auth     | `src/core/auth.py` + `src/api/v1/auth.py` with cookie sessions |

### Using Modules

#### During Project Creation

```bash
# Database only
plinth-cli init my-app --db postgres

# Database + Auth
plinth-cli init my-app --db postgres --auth jwt

# Full stack
plinth-cli init my-app --db postgres --auth jwt --redis
```

#### Adding to Existing Projects

```bash
cd my-app

# Add database
plinth-cli add postgres

# Add auth
plinth-cli add auth-jwt

# Add cache
plinth-cli add redis
```

### Module Configuration

Each module is defined in `src/plinth/commands/add.py` in `MODULE_CONFIG`:

```python
"redis": {
    "type": "cache",
    "packages": ["redis[hiredis]>=5.0.0"],
    "files": [
        ("modules/redis/cache.py.j2", "src/core/cache.py"),
    ],
}
```

### Template Variables

When creating templates, these variables are available:

| Variable              | Description   | Example                            |
| --------------------- | ------------- | ---------------------------------- |
| `{{ project_name }}`  | Project name  | `my-app`                           |
| `{{ db_type }}`       | Database type | `postgres`, `mysql`, `sqlite`      |
| `{{ db_driver }}`     | Driver name   | `asyncpg`, `aiomysql`, `aiosqlite` |
| `{{ auth_type }}`     | Auth type     | `jwt`, `session`                   |
| `{{ use_redis }}`     | Redis enabled | `True`, `False`                    |
| `{{ async_enabled }}` | Async mode    | `True` for async drivers           |

---

## Adding a New Command

### Step 1: Create the command file

```python
# src/plinth/commands/mycommand.py
def my_command(
    project_path: Path,
    console: Console,
) -> None:
    """My new command."""
    state_manager = StateManager(project_path)

    if not state_manager.exists():
        raise NotAPlinthProjectError(str(project_path))

    # Your logic here
    console.print("Done!")
```

### Step 2: Wire up in CLI

```python
# src/plinth/cli.py
from plinth.commands.mycommand import my_command

@app.command()
def mycmd(
    path: Path = typer.Option(Path("."), "--path", "-p"),
) -> None:
    """My new command description."""
    try:
        my_command(path, console)
    except PlinthError as e:
        console.print(f"[red]Error:[/red] {e.message}")
        raise typer.Exit(1)
```

---

## Adding a New Module (e.g., "stripe")

### Step 1: Add to MODULE_CONFIG

```python
# src/plinth/commands/add.py
MODULE_CONFIG = {
    # ... existing modules ...

    "stripe": {
        "type": "payment",
        "packages": ["stripe>=7.0.0"],
        "files": [
            ("modules/stripe/core.py.j2", "src/core/stripe.py"),
            ("modules/stripe/routes.py.j2", "src/api/v1/stripe.py"),
        ],
        "registry": {
            "import_path": "src.api.v1.stripe",
            "router_name": "stripe_router",
        },
    },
}
```

### Step 2: Add to AVAILABLE_MODULES

```python
# src/plinth/config.py
AVAILABLE_MODULES = {
    # ... existing ...
    "stripe": "Stripe payment integration",
}
```

### Step 3: Create templates

```python
# src/plinth/templates/modules/stripe/core.py.j2
"""Stripe integration."""

import stripe
from src.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_payment_intent(amount: int, currency: str = "usd"):
    return stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
    )
```

```python
# src/plinth/templates/modules/stripe/routes.py.j2
"""Stripe API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/stripe", tags=["stripe"])

# Export for registry
stripe_router = router

@router.post("/payment-intent")
async def create_intent():
    ...
```

### Step 4: Add config template (optional)

Update [`src/plinth/templates/base/src/config.py.j2`](src/plinth/templates/base/src/config.py.j2:1) to include Stripe settings.

---

## CLI Commands for Development

### `python -m plinth-cli <command>`

Runs plinth-cli directly from source code without installation. Useful during development.

```bash
# Test init command
python -m plinth-cli init test-app --db sqlite

# Test add command
python -m plinth-cli add redis --path test-app

# Show help
python -m plinth-cli --help
```

### `plinth-cli <command>` (after `pip install -e .`)

Same commands, but available globally after editable install.

```bash
# Create project
plinth-cli init my-app

# Add features
plinth-cli add redis
plinth-cli add auth-jwt

# Check status
plinth-cli list
plinth-cli doctor
```

### Command Details

#### `init`

Creates a new FastAPI project. As a developer, you can test with different flags:

```bash
# Minimal
plinth-cli init test1

# With database
plinth-cli init test2 --db postgres

# Full feature
plinth-cli init test3 --db postgres --auth jwt --redis
```

#### `add`

Adds a module. Requires being inside a plinth-cli project:

```bash
cd my-app
plinth-cli add redis      # Adds Redis cache.py
plinth-cli add auth-jwt   # Adds auth with routes
```

#### `list`

Shows modules. Helpful to verify state:

```bash
plinth-cli list --installed   # What's in current project
plinth-cli list --available   # What can be added
```

#### `doctor`

Diagnoses issues. Use when things go wrong:

```bash
plinth-cli doctor  # Check .plinth.json, structure, modules
```

---

## Common Development Tasks

### Testing Changes

```bash
# Run without installing (quick test)
python -m plinth-cli init test-app --db sqlite

# After making changes, test with editable install
pip install -e .
plinth-cli init test-app --db postgres --auth jwt

# Debug logging
python -m plinth-cli init test-app --db sqlite -v
```

### Adding a New Dependency

1. Add to [`requirements.txt`](requirements.txt:1)
2. Add to [`pyproject.toml`](pyproject.toml:1) dependencies
3. Document why in this guide

### Modifying Templates

Templates are Jinja2. Common variables available:

- `{{ project_name }}` - Project name
- `{{ db_type }}` - Database type (postgres, mysql, sqlite)
- `{{ db_driver }}` - Driver name (asyncpg, aiomysql, etc.)
- `{{ auth_type }}` - Auth type (jwt, session)
- `{{ use_redis }}` - Boolean for Redis
- `{{ async_enabled }}` - Boolean for async

---

## File Reference

| File                                          | Purpose            | When to Edit           |
| --------------------------------------------- | ------------------ | ---------------------- |
| [`cli.py`](src/plinth/cli.py:1)               | Command routing    | Add/remove commands    |
| [`config.py`](src/plinth/config.py:1)         | Constants & config | Add modules/drivers    |
| [`state.py`](src/plinth/state.py:1)           | State dataclasses  | Change state format    |
| [`injector.py`](src/plinth/injector.py:1)     | LibCST injection   | Change injection logic |
| [`templates.py`](src/plinth/templates.py:1)   | Jinja2 rendering   | Change build process   |
| [`packages.py`](src/plinth/packages.py:1)     | uv wrapper         | Change package install |
| [`logger.py`](src/plinth/logger.py:1)         | Rich logging       | Change output format   |
| [`exceptions.py`](src/plinth/exceptions.py:1) | Error classes      | Add new error types    |

---

## Key Design Decisions

1. **Why dataclasses over Pydantic for state?**
   - Simpler, faster, no extra dependencies for core state

2. **Why LibCST instead of regex?**
   - Safe AST manipulation preserves formatting and prevents syntax errors

3. **Why separate injector.py from add.py?**
   - Code injection is complex - isolates LibCST logic from command logic

4. **Why the registry pattern?**
   - Allows modules to be added without modifying main.py (which users might have customized)

5. **Why uv over pip?**
   - Much faster, modern Python packaging standard

---

## Troubleshooting

### LibCST injection fails

```python
# Check the source file is valid Python
python -m py_compile src/core/registry.py

# Debug the transformer
from plinth.injector import RegistryTransformer
import libcst as cst

source = Path("registry.py").read_text()
module = cst.parse_module(source)
transformer = RegistryTransformer("src.api.v1.stripe", "stripe_router")
modified = module.visit(transformer)
print(modified.code)
```

### Template not found

```bash
# Check template paths are correct
python -c "from plinth.templates import TemplateRenderer; t = TemplateRenderer(); print(t.env.list_templates())"
```

### State corruption

```bash
# Delete and re-initialize state
rm .plinth.json
plinth-cli doctor  # Will detect issues
```

---

## Questions?

Check the complete guide: [`plinth-complete-guide.md`](plinth-complete-guide.md:1)
