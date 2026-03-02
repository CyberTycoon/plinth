# 🪨 Plinth: User Guide

> Create FastAPI projects in seconds, add features as you grow

---

## What is Plinth?

Plinth is a tool that creates FastAPI projects with the features you need. Instead of starting from scratch, tell Plinth what you want (database, authentication, etc.) and it sets everything up for you.

**The big idea:** Start simple, add features later without breaking your code.

---

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install plinth-cli
```

### Option 2: Install with uv (Faster)

```bash
uv tool install plinth-cli
```

> **Note:** The package is named `plinth-cli` on PyPI, but the command remains `plinth`.

### Verify Installation

```bash
plinth --version
```

---

## Quick Start (30 Seconds)

### 1. Create Your First Project

```bash
plinth --help
plinth init my-first-app
cd my-first-app
uv run uvicorn src.main:app --reload
```

Open http://localhost:8000/docs - you have a working API!

---

## Common Use Cases

### "I need a database"

```bash
# SQLite (simplest, no setup)
plinth init my-app --db sqlite

# PostgreSQL (production-ready)
plinth init my-app --db postgres

# MySQL
plinth init my-app --db mysql
```

### "I need user login"

```bash
# JWT tokens (for APIs)
plinth init my-app --auth jwt

# Session cookies (for web apps)
plinth init my-app --auth session

# With database
plinth init my-app --db postgres --auth jwt
```

### "I need caching"

```bash
plinth init my-app --redis
```

### "I need everything"

```bash
plinth init my-app \
  --db postgres \
  --auth jwt \
  --redis \
  --docker
```

---

## All Available Features

| Feature          | Flag             | What You Get                           |
| ---------------- | ---------------- | -------------------------------------- |
| **SQLite**       | `--db sqlite`    | Simple file database, no server needed |
| **PostgreSQL**   | `--db postgres`  | Production database with asyncpg       |
| **MySQL**        | `--db mysql`     | MySQL database with aiomysql           |
| **JWT Auth**     | `--auth jwt`     | Token-based login system               |
| **Session Auth** | `--auth session` | Cookie-based login system              |
| **Redis**        | `--redis`        | Caching and fast data storage          |
| **Docker**       | `--docker`       | Container setup files                  |
| **Linting**      | `--linting`      | Code quality tools (default: on)       |

---

## Adding Features Later

Started simple but need more? No problem!

```bash
cd my-app

# Add Redis caching
plinth add redis

# Add authentication
plinth add auth-jwt

# Add database
plinth add postgres
```

**What happens:**

1. New files are created
2. Dependencies are installed
3. Routes are registered automatically
4. Configuration is updated

---

## Project Structure

After running `plinth init`, you get:

```
my-app/
├── src/
│   ├── __init__.py      # Package initializer
│   ├── main.py          # API entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py    # Application settings
│   │   ├── database.py  # Database connection (if DB selected)
│   │   └── registry.py  # Route registration
│   └── models/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── pyproject.toml       # Dependencies
├── README.md            # Project readme
└── .plinth.json         # Plinth state
```

**Your code goes in:**

- `src/api/v1/` - Add your API endpoints
- `src/models/` - Add your database models
- `src/core/` - Core utilities

---

## Environment Configuration

Copy the example file and edit:

```bash
cp .env.example .env
```

### Common Settings

**Database**

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/my-app
```

**JWT Auth**

```env
SECRET_KEY=change-this-to-a-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Redis**

```env
REDIS_URL=redis://localhost:6379/0
```

---

## Managing Your Project

### See what's installed

```bash
plinth list
```

### Check for problems

```bash
plinth doctor
```

### Remove a feature

```bash
plinth remove redis
```

---

## Examples by Use Case

### REST API with Database

```bash
plinth init todo-api --db sqlite
```

Creates:

- SQLite database
- Health check endpoint
- Ready for CRUD endpoints

### User Authentication System

```bash
plinth init user-service --db postgres --auth jwt
```

Creates:

- PostgreSQL database
- Login/register endpoints
- Password hashing
- Protected routes ready

### High-Performance API

```bash
plinth init highperf-api \
  --db postgres \
  --redis \
  --docker
```

Creates:

- PostgreSQL for data
- Redis for caching
- Docker for deployment

---

## Troubleshooting

### "plinth command not found"

```bash
# Reinstall
pip install --force-reinstall plinth
```

### "No Plinth project found"

You're not in a Plinth project directory. Look for `.plinth.json` or run `plinth init` first.

### "Module already installed"

You can't add the same module twice. Use `plinth list` to see what's installed.

### Database connection errors

Check your `.env` file has the correct `DATABASE_URL`.

---

## Next Steps

1. **Create a project:** `plinth init my-app --db sqlite`
2. **Add features:** `plinth add redis`, `plinth add auth-jwt`
3. **Start coding:** Add your endpoints in `src/api/v1/`
4. **Deploy:** Use the generated Dockerfile

---

## Commands Reference

| Command                  | Purpose                             |
| ------------------------ | ----------------------------------- |
| `plinth init <name>`     | Create new project                  |
| `plinth add <module>`    | Add feature (redis, auth-jwt, etc.) |
| `plinth remove <module>` | Remove feature                      |
| `plinth list`            | Show installed/available modules    |
| `plinth doctor`          | Check project health                |
| `plinth --help`          | Show all options                    |

---

## Developer Documentation

Want to contribute or modify Plinth? See [developer-guide.md](developer-guide.md) for:

- Code architecture
- Adding new modules
- Development setup
- Internal APIs
