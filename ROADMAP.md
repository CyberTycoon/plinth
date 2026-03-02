# 🗺️ Plinth-CLI Roadmap

> This roadmap outlines our vision for Plinth-CLI through 2027 and beyond. We are committed to long-term maintenance and continuous improvement.

**Legend:**

- ✅ **Implemented** — Available now
- 🚧 **In Progress** — Actively being developed
- 📋 **Planned** — Committed for this quarter
- 💡 **Proposed** — Under consideration, may change based on community feedback

---

## Current Status

Plinth-CLI is actively maintained and production-ready at v1.0.2. We follow semantic versioning and maintain backward compatibility within major versions.

### ✅ Implemented Features

- **Core Commands:** `init`, `add`, `list`, `remove`, `doctor`
- **Database Modules:** PostgreSQL, MySQL, SQLite with SQLAlchemy 2.0
- **Authentication:** JWT and session-based auth
- **Caching:** Redis integration
- **Code Injection:** AST-aware modifications via LibCST
- **State Management:** `.plinth.json` for tracking project configuration

---

## 2026 Milestones

### Q1 2026: Stability & Core Extensions

**Focus:** Hardening existing features and expanding the module catalog

- [ ] 📋 **Testing Module** — `plinth add pytest` for test scaffolding with fixtures
- [ ] 📋 **Docker Module** — Enhanced Docker Compose with PostgreSQL/Redis services
- [ ] 📋 **Linting Module** — `plinth add ruff` for code formatting and linting
- [ ] 📋 **MongoDB Module** — NoSQL database support via Motor
- [ ] 📋 **Doctor Enhancements** — Better diagnostics for missing dependencies

### Q2 2026: Developer Experience

**Focus:** Making Plinth-CLI more powerful for existing FastAPI projects

- [ ] 📋 **Project Templates** — `plinth init --template microservice` for different architectures
- [ ] 📋 **Alembic Integration** — `plinth add migrations` with auto-generated revision support
- [ ] 📋 **Celery Module** — Background task queues with Redis/RabbitMQ
- [ ] 📋 **Environment Sync** — `plinth sync` to reconcile .env with pyproject.toml
- [ ] 📋 **Upgrade Command** — `plinth upgrade` to update modules to latest versions

### Q3 2026: Ecosystem Growth

**Focus:** Community modules and integrations

- [ ] 💡 **Module Registry** — Public index for community-contributed modules
- [ ] 💡 **Webhook Module** — Stripe, GitHub webhook handlers
- [ ] 💡 **Email Module** — FastMail, SendGrid integration templates
- [ ] 💡 **GraphQL Module** — Strawberry GraphQL scaffolding
- [ ] 💡 **OpenAPI Enhancements** — Better documentation generation

### Q4 2026: Enterprise & Scale

**Focus:** Supporting larger teams and deployments

- [ ] 💡 **Configuration Profiles** — Save and share project templates
- [ ] 💡 **CI/CD Templates** — GitHub Actions, GitLab CI scaffolding
- [ ] 💡 **Monitoring Module** — Prometheus metrics endpoints
- [ ] 💡 **Structured Logging** — JSON logging with correlation IDs
- [ ] 💡 **Health Checks** — Advanced health check endpoints with dependency status

---

## 2027 Milestones

### Q1 2027: Platform Foundations

**Focus:** Building infrastructure for broader adoption

- [ ] 💡 **Plugin System** — Third-party module loading
- [ ] 💡 **Private Registries** — Self-hosted module hosting
- [ ] 💡 **Team Features** — Shared templates within organizations
- [ ] 💡 **VS Code Extension** — IDE integration for module management

### Q2 2027+ : Long-Term Vision

**Focus:** Expanding beyond core functionality

- [ ] 💡 **Framework Expansion** — Experimental Django/Flask scaffolding
- [ ] 💡 **Cloud Integrations** — AWS CDK, Azure Bicep templates
- [ ] 💡 **Kubernetes Support** — Helm chart generation
- [ ] 💡 **AI-Assisted Scaffolding** — Intelligent module recommendations

---

## How to Contribute

We welcome contributions! To propose a new module or feature:

1. Open a [GitHub Discussion](https://github.com/cybertycoon/plinth/discussions)
2. Submit a [GitHub Issue](https://github.com/cybertycoon/plinth/issues)

### Contributing New Modules

Modules are Jinja2 templates in `src/plinth/templates/`. See existing modules for patterns:

- [`src/plinth/templates/base/`](src/plinth/templates/base/) — Base project template
- Add module metadata to [`plinth_config.AVAILABLE_MODULES`](src/plinth/config.py:72)

---

## Version Support Policy

| Version | Status             | Support Until      |
| ------- | ------------------ | ------------------ |
| 1.x     | Active Development | Q4 2027            |
| 0.x     | End of Life        | Already deprecated |

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for detailed release notes.

---

_Last updated: March 2026_

_This roadmap is a living document. Priorities may shift based on community feedback and maintainer capacity. Features marked with 💡 are aspirational and subject to change._
