# pedestal Developer Guide

> Quick reference for internal developers working on the pedestal codebase

---

## Quick Start for Developers

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone <repo>
cd Pedestal

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run in development mode (no installation needed)
python -m pedestal --help

# OR install in editable mode for regular development
pip install -e .
pedestal --help
```

### What Each Command Does

#### `pip install -r requirements.txt`

Installs all required Python packages (typer, jinja2, pydantic, libcst, rich, etc.) into your current Python environment.

#### `python -m pedestal --help`

Runs pedestal as a Python module directly from source code. Useful for quick testing without installation. The `-m` flag tells Python to run the `Pedestal` package's `__main__.py` file.

#### `pip install -e .`

Installs pedestal in **editable (development) mode**:

- `-e` = Editable install (creates a link to source code)
- `.` = Current directory (where `pyproject.toml` is located)
- Changes to source code are immediately reflected without reinstalling
- Makes the `Pedestal` command available system-wide

#### `pedestal --help`

Displays all available CLI commands, their descriptions, and options. After editable install, you can use `Pedestal` directly instead of `python -m Pedestal`.

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

**Why we use it:** Allows pedestal to inject new routes without touching `main.py`

```python
# This is the magic that makes 'pedestal add' work
ROUTERS: list[APIRouter] = []
```

**How injection works:**

1. LibCST parses `registry.py`
2. Finds the `ROUTERS` list
3. Appends new router import + reference
4. Writes back modified code

### 2. State Management

**What it is:** A JSON file (`.Pedestal.json`) tracking installed modules

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

**Where to add new modules:** [`src/Pedestal/commands/add.py`](src/Pedestal/commands/add.py:20)

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

**Pattern:** All errors inherit from `PedestalError`

```python
# Raising errors
raise ProjectExistsError("my-app")

# Catching in CLI
try:
    init_project(config, console)
except PedestalError as e:
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
pedestal init my-app --db postgres

# Database + Auth
pedestal init my-app --db postgres --auth jwt

# Full stack
pedestal init my-app --db postgres --auth jwt --redis
```

#### Adding to Existing Projects

```bash
cd my-app

# Add database
pedestal add postgres

# Add auth
pedestal add auth-jwt

# Add cache
pedestal add redis
```

### Module Configuration

Each module is defined in `src/Pedestal/commands/add.py` in `MODULE_CONFIG`:

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
# src/Pedestal/commands/mycommand.py
def my_command(
    project_path: Path,
    console: Console,
) -> None:
    """My new command."""
    state_manager = StateManager(project_path)

    if not state_manager.exists():
        raise NotAPedestalProjectError(str(project_path))

    # Your logic here
    console.print("Done!")
```

### Step 2: Wire up in CLI

```python
# src/Pedestal/cli.py
from Pedestal.commands.mycommand import my_command

@app.command()
def mycmd(
    path: Path = typer.Option(Path("."), "--path", "-p"),
) -> None:
    """My new command description."""
    try:
        my_command(path, console)
    except PedestalError as e:
        console.print(f"[red]Error:[/red] {e.message}")
        raise typer.Exit(1)
```

---

## Adding a New Module (e.g., "stripe")

### Step 1: Add to MODULE_CONFIG

```python
# src/Pedestal/commands/add.py
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
# src/Pedestal/config.py
AVAILABLE_MODULES = {
    # ... existing ...
    "stripe": "Stripe payment integration",
}
```

### Step 3: Create templates

```python
# src/Pedestal/templates/modules/stripe/core.py.j2
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
# src/Pedestal/templates/modules/stripe/routes.py.j2
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

Update [`src/Pedestal/templates/base/src/config.py.j2`](src/Pedestal/templates/base/src/config.py.j2:1) to include Stripe settings.

---

## CLI Commands for Development

### `python -m pedestal <command>`

Runs pedestal directly from source code without installation. Useful during development.

```bash
# Test init command
python -m pedestal init test-app --db sqlite

# Test add command
python -m pedestal add redis --path test-app

# Show help
python -m pedestal --help
```

### `pedestal <command>` (after `pip install -e .`)

Same commands, but available globally after editable install.

```bash
# Create project
pedestal init my-app

# Add features
pedestal add redis
pedestal add auth-jwt

# Check status
pedestal list
pedestal doctor
```

### Command Details

#### `init`

Creates a new FastAPI project. As a developer, you can test with different flags:

```bash
# Minimal
pedestal init test1

# With database
pedestal init test2 --db postgres

# Full feature
pedestal init test3 --db postgres --auth jwt --redis
```

#### `add`

Adds a module. Requires being inside a pedestal project:

```bash
cd my-app
pedestal add redis      # Adds Redis cache.py
pedestal add auth-jwt   # Adds auth with routes
```

#### `list`

Shows modules. Helpful to verify state:

```bash
pedestal list --installed   # What's in current project
pedestal list --available   # What can be added
```

#### `doctor`

Diagnoses issues. Use when things go wrong:

```bash
pedestal doctor  # Check .Pedestal.json, structure, modules
```

---

## Common Development Tasks

### Testing Changes

```bash
# Run without installing (quick test)
python -m pedestal init test-app --db sqlite

# After making changes, test with editable install
pip install -e .
pedestal init test-app --db postgres --auth jwt

# Debug logging
python -m pedestal init test-app --db sqlite -v
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
| [`cli.py`](src/Pedestal/cli.py:1)               | Command routing    | Add/remove commands    |
| [`config.py`](src/Pedestal/config.py:1)         | Constants & config | Add modules/drivers    |
| [`state.py`](src/Pedestal/state.py:1)           | State dataclasses  | Change state format    |
| [`injector.py`](src/Pedestal/injector.py:1)     | LibCST injection   | Change injection logic |
| [`templates.py`](src/Pedestal/templates.py:1)   | Jinja2 rendering   | Change build process   |
| [`packages.py`](src/Pedestal/packages.py:1)     | uv wrapper         | Change package install |
| [`logger.py`](src/Pedestal/logger.py:1)         | Rich logging       | Change output format   |
| [`exceptions.py`](src/Pedestal/exceptions.py:1) | Error classes      | Add new error types    |

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
from Pedestal.injector import RegistryTransformer
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
python -c "from Pedestal.templates import TemplateRenderer; t = TemplateRenderer(); print(t.env.list_templates())"
```

### State corruption

```bash
# Delete and re-initialize state
rm .Pedestal.json
pedestal doctor  # Will detect issues
```

---

## Questions?

Check the complete guide: [`Pedestal-complete-guide.md`](Pedestal-complete-guide.md:1)
