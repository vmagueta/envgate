# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).



## [0.6.0] - 2026-05-11

### Added
- `validator` option in `get_env` and `validate` schemas. Accepts a
  callable that receives the coerced value and signals failure by
  raising any exception. The exception's `str(exc)` becomes the error
  message, joined into the collective `ValidationError` alongside
  missing-variable and coercion errors.
- `InvalidEnvVarError` now carries an optional `reason` attribute
  (set when the error came from a validator) and adapts its message
  accordingly: `"Environment variable 'PORT' has invalid value '80':
  must be in [1024, 65535]"`.

### Behavior notes
- Validators run **after** type coercion, so they see the typed value
  (e.g. `int`, `list[int]`) rather than the raw string.
- Validators also run on `default` values — a default that violates
  the validator is a schema bug, surfaced eagerly instead of waiting
  for the variable to be absent in production.
- Validators are **not** invoked when the variable is optional, absent,
  and no default is provided (the function returns `None`).
- Coercion failures short-circuit before the validator runs.

## [0.5.0] - 2026-04-23

### Added
- New `list` type for comma-separated environment variables. Supports
  `list` (alias for `list[str]`), `list[str]`, `list[int]`, `list[float]`,
  and `list[bool]`.
- `sep` parameter on `get_env` (keyword-only, default `","`), usable
  within `validate` schemas. Only applies to list types — passing `sep`
  with a scalar type raises `ValueError`.
- When multiple items within a list fail coercion, all errors are
  collected and reported together in a single `InvalidEnvVarError`,
  consistent with the collective validation behavior from v0.3.
- List defaults are returned as copies, preventing mutations on
  returned values from leaking back into shared schemas.

## [0.4.1] - 2026-04-23

### Changed
- Docstring examples in `get_env` and `validate` are now illustrative
  (plain text, no `>>>` prompts). Their behavior remains covered by
  unit tests in `tests/`.
- CI now executes doctests for pure modules via `pytest --doctest-modules`.
  Previously, docstring examples could silently drift from the API.

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
