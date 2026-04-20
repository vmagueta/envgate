# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.4.0] - 2026-04-20

### Added
- Explicit `required` flag in `get_env` and `validate` schemas,
  with tri-state semantics: `True` (must be set), `False` (optional,
  returns `None` if absent), or `None` (default — inferred from `default`).
- `get_env` now raises `ValueError` when `required=True` is combined
  with a `default` value (contradictory schema).
- `required=False` without a `default` now returns `None` instead of
  raising `MissingEnvVarError`.

### Changed
- Schema validation for the `required`/`default` contradiction happens
  eagerly at the top of `get_env`, before consulting `os.environ`, so
  schema bugs surface even when the variable is set.

## [0.3.0] - 2026-04-01

### Added
- `ValidationError` exception that collects all individual errors
- `validate()` now reports all missing/invalid variables at once instead of stopping at the first failure

## [0.2.0] - 2026-03-30

### Added
- Initial project setup
- `pyproject.toml` with metadata and PyPI configuration
- README with badges and usage example
- PR template, CONTRIBUTING guide
- Core library: `get_env` and `validate` functions
- Custom exceptions: `EnvGateError`, `MissingEnvVarError`, `InvalidEnvVarError`
- Type coercion: `str`, `int`, `float`, `bool`
- Unit tests (56 tests) and doctests (10 tests)
- CI workflow: ruff format, ruff check, pytest, coverage
- CD workflow: automatic publish to PyPI on release
- README badges: CI status, coverage, PyPI version, Python versions
