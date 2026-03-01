# 🪨 Plinth

> Stop building the "basement" of your FastAPI project.

## The Problem

Every new FastAPI project starts with the same 2-hour slog:

- Wiring up SQLAlchemy with async drivers
- Setting up config management
- Creating folder structures that won't become a mess
- Adding auth... then rewriting it when you change your mind

**Boilerplate burnout is real.**

## The Solution

Plinth scaffolds production-ready FastAPI projects in **2 seconds**, then lets you add features incrementally without breaking your code.

```bash
# Start with exactly what you need
plinth init my-api --db postgres --auth jwt

# Change your mind later? No problem.
plinth add redis
plinth add auth-session
```

## Why Plinth?

| Without Plinth                                | With Plinth                                    |
| --------------------------------------------- | ---------------------------------------------- |
| Copy-paste boilerplate from old projects      | Generate clean, consistent structure instantly |
| Fear of adding features mid-project           | Add/remove modules anytime safely              |
| Hope your code injection doesn't break things | AST-aware code modifications (LibCST)          |
| Spend hours on setup                          | Spend hours on **features**                    |

## Installation

### From PyPI

```bash
pip install plinth-cli
```

### Install with uv (Faster)

```bash
uv tool install plinth-cli
```

### From Source

```bash
git clone https://github.com/cybertycoon/plinth.git
cd plinth
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Create a Basic Project

```bash
plinth init my-app
cd my-app
uv run uvicorn src.main:app --reload
```

### Create with Database & Auth

```bash
plinth init my-api --db postgres --auth jwt --redis
```

### Add Features Later

```bash
cd my-api

# Add Redis caching
plinth add redis

# Add JWT authentication
plinth add auth-jwt
```

## Commands

### `plinth init <name>` — Create New Project

Scaffold a new FastAPI project with your chosen features.

```bash
# Basic project
plinth init my-app

# With database and auth
plinth init my-api --db postgres --auth jwt

# Full stack
plinth init my-service --db postgres --redis --auth jwt
```

**Options:**

- `--db postgres|mysql|sqlite` — Add database support
- `--redis` — Add Redis caching
- `--auth jwt|session` — Add authentication

### `plinth add <module>` — Add Features Later

Add modules to an existing project without breaking your code.

```bash
cd my-api

# Add Redis for caching
plinth add redis

# Add JWT authentication
plinth add auth-jwt

# Add database (if not added during init)
plinth add postgres
```

### `plinth remove <module>` — Remove Features

Cleanly remove a module and its code.

```bash
plinth remove redis
plinth remove auth-jwt
```

### `plinth list` — See What's Available

Shows installed modules and available modules you can add.

```bash
plinth list
```

### `plinth doctor` — Check Project Health

Diagnoses issues with your Plinth project.

```bash
plinth doctor
```

## Available Modules

- **postgres/mysql/sqlite** - Database with async drivers
- **redis** - Caching & sessions
- **auth-jwt** - JWT authentication
- **auth-session** - Session-based auth

## How It Works

Plinth doesn't just copy files—it **understands** your Python code using AST manipulation. When you run `plinth add redis`, it:

1. Injects Redis connection code into your main app
2. Updates `.env` with Redis URL
3. Adds dependencies to `pyproject.toml`
4. Registers routes without touching your custom code

Your project stays clean, typed, and maintainable.

## Project Structure

```
my-app/
├── .plinth.json          # Tracks installed modules
├── pyproject.toml        # Dependencies
├── src/
│   ├── main.py          # FastAPI entry
│   ├── core/
│   │   ├── config.py    # Pydantic settings
│   │   └── registry.py  # Auto-router registration
│   └── api/
│       └── v1/
└── tests/
```

## Documentation

- [Complete User Guide](docs/plinth-complete-guide.md)
- [Developer Guide](docs/developer-guide.md)

## License

MIT License
