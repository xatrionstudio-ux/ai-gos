"""
Result monad — explicit error handling without exceptions in application layer.

Application services return Result[T, E] instead of raising exceptions.
This makes error paths visible in function signatures and eliminates
surprise exception propagation across domain boundaries.

Usage:
    result = await user_service.register(command)
    match result:
        case Ok(user):
            return UserResponse.model_validate(user)
        case Err(error):
            raise HTTPException(...)
"""

from __future__ import annotations

from typing import Callable, Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E", bound=Exception)
U = TypeVar("U")


class Ok(Generic[T]):
    """Successful result."""

    __slots__ = ("value",)

    def __init__(self, value: T) -> None:
        self.value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def map(self, fn: Callable[[T], U]) -> "Ok[U]":
        return Ok(fn(self.value))

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


class Err(Generic[E]):
    """Failed result."""

    __slots__ = ("error",)

    def __init__(self, error: E) -> None:
        self.error = error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:  # type: ignore[type-var]
        raise self.error

    def map(self, fn: Callable) -> "Err[E]":
        return self

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


# Type alias
Result = Union[Ok[T], Err[E]]
