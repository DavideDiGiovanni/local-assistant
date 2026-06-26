from dataclasses import dataclass, field
from typing import Any

from local_assistant.models.agent_result import AgentResult


@dataclass(frozen=True)
class OrchestratorResult:
    """
    Standard result returned by the orchestrator.

    The orchestrator routes requests to domain agents.
    It does not execute tools directly.
    """

    success: bool
    message: str
    domain: str
    operation: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    agent_result: AgentResult | None = None

    @classmethod
    def from_agent_result(
        cls,
        domain: str,
        agent_result: AgentResult,
    ) -> "OrchestratorResult":
        return cls(
            success=agent_result.success,
            message=agent_result.message,
            domain=domain,
            operation=agent_result.operation,
            data=agent_result.data,
            error=agent_result.error,
            agent_result=agent_result,
        )
