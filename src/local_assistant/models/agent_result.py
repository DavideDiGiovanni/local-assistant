from dataclasses import dataclass, field
from typing import Any

from local_assistant.models.tool_result import ToolResult


@dataclass(frozen=True)
class AgentResult:
    """
    Standard result returned by agents.

    Agents do not perform low-level operations directly.
    They coordinate tools and expose a domain-level result.
    """

    success: bool
    message: str
    operation: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    tool_result: ToolResult | None = None

    @classmethod
    def from_tool_result(
        cls,
        operation: str,
        tool_result: ToolResult,
    ) -> "AgentResult":
        return cls(
            success=tool_result.success,
            message=tool_result.message,
            operation=operation,
            data=tool_result.data,
            error=tool_result.error,
            tool_result=tool_result,
        )
