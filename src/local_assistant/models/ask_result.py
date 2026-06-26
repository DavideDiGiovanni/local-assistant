from dataclasses import dataclass, field
from typing import Any

from local_assistant.models.command_proposal import CommandProposal
from local_assistant.models.command_proposal import CommandProposalResult
from local_assistant.models.orchestrator_result import OrchestratorResult


@dataclass(frozen=True)
class AskResult:
    """
    Result returned by the controlled ask flow.

    The ask flow combines:

    - natural language request;
    - LLM command proposal;
    - local validation;
    - controlled execution through the orchestrator.
    """

    success: bool
    message: str
    request: str
    proposal: CommandProposal | None = None
    proposal_result: CommandProposalResult | None = None
    execution_result: OrchestratorResult | None = None
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
