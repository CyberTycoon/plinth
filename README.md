# 🪨 Plinth-CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Stop building the "basement" of your FastAPI project.

## The Problem

Every new FastAPI project starts with the same 2-hour slog:

- Wiring up SQLAlchemy with async drivers
- Setting up config management
- Creating folder structures that won't become a mess
- Adding auth... then rewriting it when you change your mind

**Boilerplate burnout is real.**

## The Solution

Plinth-CLI scaffolds production-ready FastAPI projects in **2 seconds**, then lets you add features incrementally without breaking your code.

```bash
# Start with exactly what you need
plinth-cli init my-api --db postgres --auth jwt

# Change your mind later? No problem.
plinth-cli add redis
plinth-cli add auth-session
```

## Why Plinth-CLI?

| Without Plinth-CLI                            | With Plinth-CLI                                |
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
cd plinth-cli
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Create a Basic Project

```bash
plinth-cli init my-app
cd my-app
uv run uvicorn src.main:app --reload
```

### Create with Database & Auth

```bash
plinth-cli init my-api --db postgres --auth jwt --redis
```

### Add Features Later

```bash
cd my-api

# Add Redis caching
plinth-cli add redis

# Add JWT authentication
plinth-cli add auth-jwt
```

## Commands

### `plinth-cli init <name>` — Create New Project

Scaffold a new FastAPI project with your chosen features.

```bash
# Basic project
plinth-cli init my-app

# With database and auth
plinth-cli init my-api --db postgres --auth jwt

# Full stack
plinth-cli init my-service --db postgres --redis --auth jwt
```

**Options:**

- `--db postgres|mysql|sqlite` — Add database support
- `--redis` — Add Redis caching
- `--auth jwt|session` — Add authentication

### `plinth-cli add <module>` — Add Features Later

Add modules to an existing project without breaking your code.

```bash
cd my-api

# Add Redis for caching
plinth-cli add redis

# Add JWT authentication
plinth-cli add auth-jwt

# Add database (if not added during init)
plinth-cli add postgres
```

### `plinth-cli remove <module>` — Remove Features

Cleanly remove a module and its code.

```bash
plinth-cli remove redis
plinth-cli remove auth-jwt
```

### `plinth-cli list` — See What's Available

Shows installed modules and available modules you can add.

```bash
plinth-cli list
```

### `plinth-cli doctor` — Check Project Health

Diagnoses issues with your Plinth-CLI project.

```bash
plinth-cli doctor
```

## Available Modules

- **postgres/mysql/sqlite** - Database with async drivers
- **redis** - Caching & sessions
- **auth-jwt** - JWT authentication
- **auth-session** - Session-based auth

## How It Works

Plinth-CLI doesn't just copy files—it **understands** your Python code using AST manipulation. When you run `plinth-cli add redis`, it:

1. Injects Redis connection code into your main app
2. Updates `.env` with Redis URL
3. Adds dependencies to `pyproject.toml`
4. Registers routes without touching your custom code

Your project stays clean, typed, and maintainable.

## Project Structure

```
my-app/
├── src/
│   ├── __init__.py       # Package initializer
│   ├── main.py           # FastAPI entry
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py     # Pydantic settings
│   │   ├── database.py   # Database connection (if DB selected)
│   │   └── registry.py   # Auto-router registration
│   └── models/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── .plinth.json         # Tracks installed modules
├── pyproject.toml       # Dependencies
└── README.md            # Project readme
```

## Documentation

- [Complete User Guide](https://github.com/CyberTycoon/plinth/blob/main/docs/plinth-complete-guide.md)
- [Developer Guide](https://github.com/CyberTycoon/plinth/blob/main/docs/developer-guide.md)
- [Roadmap](https://github.com/CyberTycoon/plinth/blob/main/ROADMAP.md)

## License

MIT License
