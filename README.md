# envgate

[![CI](https://github.com/vmagueta/envgate/actions/workflows/ci.yml/badge.svg)](https://github.com/vmagueta/envgate/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/vmagueta/envgate/branch/main/graph/badge.svg)](https://codecov.io/gh/vmagueta/envgate)
[![PyPI version](https://img.shields.io/pypi/v/envgate)](https://pypi.org/project/envgate/)
[![Python](https://img.shields.io/pypi/pyversions/envgate)](https://pypi.org/project/envgate/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A minimal Python library to validate environment variables at startup. Zero dependencies.

## Why?

Instead of your app crashing at runtime because `DATABASE_URL` is missing,
envgate validates everything at startup and tells you exactly what's wrong.

## Installation

```bash
pip install envgate
```

## Quick Start

```python
from envgate import get_env, validate

# Get a single variable with type coercion
port = get_env("PORT", type="int", default=8000)
debug = get_env("DEBUG", type="bool", default=False)

# Explicitly mark a variable as required
api_key = get_env("API_KEY", required=True)

# Parse comma-separated lists (or use a custom separator)
hosts = get_env("ALLOWED_HOSTS", type="list")            # ["a", "b", "c"]
ports = get_env("PORTS", type="list[int]", sep=":")      # [8000, 8001]

# Or validate multiple variables at once
config = validate({
    "DATABASE_URL": {"type": "str"},
    "REDIS_URL": {"type": "str"},
    "PORT": {"type": "int", "default": 8000},
    "DEBUG": {"type": "bool", "default": False},
})
```

If `DATABASE_URL` and `REDIS_URL` are missing and `PORT` is invalid, you get all errors at once:

```
envgate.exceptions.ValidationError: Environment validation failed:
    - Environment variable 'DATABASE_URL' is not set.
    - Environment variable 'REDIS_URL' is not set.
    - Environment variable 'PORT' has invalid value 'abc' (expected int).
```

## Supported Types

| Type | Example values |
|------|---------------|
| `str` | Any string (default) |
| `int` | `"42"`, `"-7"`, `"0"` |
| `float` | `"3.14"`, `"42"`, `"-2.5"` |
| `bool` | `"true"`, `"1"`, `"yes"`, `"on"` / `"false"`, `"0"`, `"no"`, `"off"` |
| `list`, `list[str]`, `list[int]`, `list[float]`, `list[bool]` | Comma-separated values — e.g. `"a,b,c"` → `["a", "b", "c"]`. Pass `sep=":"` (or any character) to override the separator. |

## Contributing

Contributions are welcome! Check out the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
