# Contributing to envgate

Thanks for your interest in contributing!

## Getting started

1. Fork and clone the repo
2. Install dependencies:

```bash
uv sync
```

3. Run tests:

```bash
uv run pytest
```

4. Run linter:

```bash
uv run ruff check .
```

## Guidelines

- Follow PEP 8
- Add type hints to all functions
- Write tests for new features
- Keep zero external dependencies — stdlib only

## Ideas for contribution

- URL/email type validation
- Decorator support for FastAPI/Django
- `.env` file loading
- Compare `.env` with `.env.example` (detect drift)
- Custom validators (regex, choices)
- Variable groups (e.g., "database", "cache", "auth")

## Pull requests

- Create a branch from `main`
- Keep PRs focused — one feature or fix per PR
- Fill out the PR template
