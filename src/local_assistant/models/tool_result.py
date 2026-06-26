from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    """
    Standard result returned by tools.

    A tool must report whether it succeeded, what happened,
    and any structured data produced by the operation.
    """

    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
