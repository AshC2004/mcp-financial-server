"""Custom error classes for the MCP Financial Server."""


class ToolError(Exception):
    """Base error for tool execution failures."""

    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ValidationError(ToolError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__("VALIDATION_ERROR", message, details)


class DatabaseError(ToolError):
    """Raised when a database operation fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__("DATABASE_ERROR", message, details)


class NotFoundError(ToolError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__("NOT_FOUND", message, details)
