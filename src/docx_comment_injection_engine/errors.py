from __future__ import annotations

from typing import Iterable, List, Mapping


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, errors: Iterable[Mapping[str, object]]):
        self.errors: List[Mapping[str, object]] = list(errors)
        message = "Validation failed"
        super().__init__(message)

    def to_dict(self) -> dict:
        return {"message": str(self), "errors": self.errors}
