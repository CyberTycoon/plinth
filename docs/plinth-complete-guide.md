# 🪨 pedestal: User Guide

> Create FastAPI projects in seconds, add features as you grow

---

## What is pedestal?

pedestal is a tool that creates FastAPI projects with the features you need. Instead of starting from scratch, tell pedestal what you want (database, authentication, etc.) and it sets everything up for you.

**The big idea:** Start simple, add features later without breaking your code.

---

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install pedestal
```

### Option 2: Install with uv (Faster)

```bash
uv tool install pedestal
```

> **Note:** The package is named `pedestal` on PyPI, but the command remains `Pedestal`.

### Verify Installation

```bash
pedestal --version
```

---

## Quick Start (30 Seconds)

### 1. Create Your First Project

```bash
pedestal --help
pedestal init my-first-app
cd my-first-app
uv run uvicorn src.main:app --reload
```

Open http://localhost:8000/docs - you have a working API!

---

## Common Use Cases

### "I need a database"

```bash
# SQLite (simplest, no setup)
pedestal init my-app --db sqlite

# PostgreSQL (production-ready)
pedestal init my-app --db postgres

# MySQL
pedestal init my-app --db mysql
```

### "I need user login"

```bash
# JWT tokens (for APIs)
pedestal init my-app --auth jwt

# Session cookies (for web apps)
pedestal init my-app --auth session

# With database
pedestal init my-app --db postgres --auth jwt
```

### "I need caching"

```bash
pedestal init my-app --redis
```

### "I need everything"

```bash
pedestal init my-app \
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
pedestal add redis

# Add authentication
pedestal add auth-jwt

# Add database
pedestal add postgres
```

**What happens:**

1. New files are created
2. Dependencies are installed
3. Routes are registered automatically
4. Configuration is updated

---

## Project Structure

After running `pedestal init`, you get:

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
└── .Pedestal.json         # pedestal state
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
pedestal list
```

### Check for problems

```bash
pedestal doctor
```

### Remove a feature

```bash
pedestal remove redis
```

---

## Examples by Use Case

### REST API with Database

```bash
pedestal init todo-api --db sqlite
```

Creates:

- SQLite database
- Health check endpoint
- Ready for CRUD endpoints

### User Authentication System

```bash
pedestal init user-service --db postgres --auth jwt
```

Creates:

- PostgreSQL database
- Login/register endpoints
- Password hashing
- Protected routes ready

### High-Performance API

```bash
pedestal init highperf-api \
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

### "pedestal command not found"

```bash
# Reinstall
pip install --force-reinstall Pedestal
```

### "No pedestal project found"

You're not in a pedestal project directory. Look for `.Pedestal.json` or run `pedestal init` first.

### "Module already installed"

You can't add the same module twice. Use `pedestal list` to see what's installed.

### Database connection errors

Check your `.env` file has the correct `DATABASE_URL`.

---

## Next Steps

1. **Create a project:** `pedestal init my-app --db sqlite`
2. **Add features:** `pedestal add redis`, `pedestal add auth-jwt`
3. **Start coding:** Add your endpoints in `src/api/v1/`
4. **Deploy:** Use the generated Dockerfile

---

## Commands Reference

| Command                      | Purpose                             |
| ---------------------------- | ----------------------------------- |
| `pedestal init <name>`     | Create new project                  |
| `pedestal add <module>`    | Add feature (redis, auth-jwt, etc.) |
| `pedestal remove <module>` | Remove feature                      |
| `pedestal list`            | Show installed/available modules    |
| `pedestal doctor`          | Check project health                |
| `pedestal --help`          | Show all options                    |

---

## Developer Documentation

Want to contribute or modify pedestal? See [developer-guide.md](developer-guide.md) for:

- Code architecture
- Adding new modules
- Development setup
- Internal APIs
