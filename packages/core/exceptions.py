"""
Domain exception hierarchy for AI-GOS.

All exceptions include a machine-readable code for API error serialization.
HTTP status codes are assigned at the API layer (controllers), NOT in domain logic.
"""

from __future__ import annotations


class AIGOSException(Exception):
    """Base exception for all AI-GOS domain errors."""

    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, code: str | None = None) -> None:
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        super().__init__(self.message)

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


class NotFoundError(AIGOSException):
    """Resource does not exist."""

    code = "NOT_FOUND"
    message = "The requested resource was not found."


class ConflictError(AIGOSException):
    """Resource already exists or state conflict."""

    code = "CONFLICT"
    message = "A conflict occurred with the current state of the resource."


class AuthorizationError(AIGOSException):
    """Caller lacks permission for the requested action."""

    code = "FORBIDDEN"
    message = "You do not have permission to perform this action."


class AuthenticationError(AIGOSException):
    """Identity cannot be verified."""

    code = "UNAUTHORIZED"
    message = "Authentication is required."


class ValidationError(AIGOSException):
    """Input data failed validation."""

    code = "VALIDATION_ERROR"
    message = "The provided input is invalid."

    def __init__(self, message: str, fields: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.fields = fields or {}


class RateLimitError(AIGOSException):
    """Too many requests from this caller."""

    code = "RATE_LIMITED"
    message = "You have exceeded the rate limit. Please wait before retrying."


class TenantIsolationError(AIGOSException):
    """Cross-tenant data access detected — security violation."""

    code = "TENANT_ISOLATION_VIOLATION"
    message = "Cross-tenant access is not permitted."


class WorkflowError(AIGOSException):
    """Workflow execution error."""

    code = "WORKFLOW_ERROR"
    message = "A workflow execution error occurred."


class KnowledgeError(AIGOSException):
    """Knowledge layer processing error."""

    code = "KNOWLEDGE_ERROR"
    message = "A knowledge processing error occurred."


class AIProviderError(AIGOSException):
    """External AI provider returned an error."""

    code = "AI_PROVIDER_ERROR"
    message = "The AI provider returned an error."
