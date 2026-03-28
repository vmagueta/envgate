# envgate

[![PyPI version](https://img.shields.io/pypi/v/envgate)](https://pypi.org/project/envgate/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/envgate)](https://pypi.org/project/envgate/)

A minimal Python library to validate environment variables at startup. Zero dependencies.

## Why?

Instead of your app crashing at runtime because `DATABASE_URL` is missing,
envgate validates everything at startup and tells you exactly what's wrong — all at once.

## Installation

```bash
pip install envgate
```

## Quick Start

```python
from envgate import envgate

envgate({
    "DATABASE_URL": {"required": True},
    "REDIS_URL": {"required": True},
    "LOG_LEVEL": {"default": "INFO"},
    "PORT": {"type": int, "default": 8000},
    "DEBUG": {"type": bool, "default": False},
})
```

If `DATABASE_URL` and `REDIS_URL` are missing, you get:

```
envgate: 2 environment variable errors:
  - DATABASE_URL is required
  - REDIS_URL is required
```

## License

MIT
