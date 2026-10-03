"""Explicit exceptions with stable, machine-readable error codes."""


class GoldScopeError(Exception):
    """Base class. `code` is stable and safe to expose; `message` never holds secrets."""

    code = "goldscope_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConfigError(GoldScopeError):
    """Configuration is missing or invalid for the requested use case."""

    code = "config_error"


class NotImplementedYetError(GoldScopeError):
    """A planned command whose backlog task has not been implemented."""

    code = "not_implemented"


class DataConflictError(GoldScopeError):
    """A business key already exists with different content (needs a new revision_key)."""

    code = "data_conflict"
