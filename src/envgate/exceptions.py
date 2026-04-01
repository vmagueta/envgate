"""Custom exceptions for envgate.

All exceptions inherit from :class:`EnvGateError`, making it easy to
catch any envgate-related error with a single except clause.
"""


class EnvGateError(Exception):
    """Base exception for all envgate errors.

    Catch this to handle any error raised by envgate.

    Examples:
        >>> try:
        ...     raise EnvGateError("something went wrong")
        ... except EnvGateError as e:
        ...     str(e)
        'something went wrong'
    """


class MissingEnvVarError(EnvGateError):
    """Raised when a required environment variable is not set.

    Attributes:
        var_name: The name of the missing environment variable.

    Examples:
        >>> error = MissingEnvVarError("DATABASE_URL")
        >>> str(error)
        "Environment variable 'DATABASE_URL' is not set."
        >>> error.var_name
        'DATABASE_URL'
    """

    def __init__(self, var_name: str) -> None:
        self.var_name = var_name
        super().__init__(f"Environment variable '{var_name}' is not set.")


class InvalidEnvVarError(EnvGateError):
    """Raised when an environment variable has an invalid value.

    Attributes:
        var_name: The name of the environment variable.
        value: The invalid value that was found.
        expected_type: The type that was expected.

    Examples:
        >>> error = InvalidEnvVarError("PORT", "abc", "int")
        >>> str(error)
        "Environment variable 'PORT' has invalid value 'abc' (expected int)."
        >>> error.var_name
        'PORT'
    """

    def __init__(self, var_name: str, value: str, expected_type: str) -> None:
        self.var_name = var_name
        self.value = value
        self.expected_type = expected_type
        super().__init__(
            f"Environment variable '{var_name}' has invalid value "
            f"'{value}' (expected {expected_type})."
        )


class ValidationError(EnvGateError):
    """Raised when multiple environment variables fail validation.

    Collects all individual errors so the user can fix everything
    in a single pass instead of playing whack-a-mole.

    Attributes:
        errors: A list of individual :class:`MissingEnvVarError` and/or
            :class:`InvalidEnvVarError` instances.

    Examples:
        >>> errors = [
        ...     MissingEnvVarError("DATABASE_URL"),
        ...     InvalidEnvVarError("PORT", "abc", "int")
        ... ]
        >>> exc = ValidationError(errors)
        >>> len(exc.errors)
        2
        >>> print(exc)
        Environment validation failed:
            - Environment variable 'DATABASE_URL' is not set.
            - Environment variable 'PORT' has invalid value 'abc' (expected int).
    """

    def __init__(self, errors: list[EnvGateError]) -> None:
        self.errors = errors
        details = "\n".join(f"    - {e}" for e in errors)
        super().__init__(f"Environment validation failed:\n{details}")
