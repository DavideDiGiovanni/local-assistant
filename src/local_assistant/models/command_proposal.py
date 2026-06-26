from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CommandProposal:
    """
    Structured command proposed by an LLM.

    This is not execution.

    The proposal must be validated before it can be displayed or executed.
    """

    domain: str
    operation: str
    arguments: dict[str, Any]
    explanation: str
    requires_confirmation: bool = True


@dataclass(frozen=True)
class CommandProposalResult:
    """
    Result returned by the command proposal layer.
    """

    success: bool
    message: str
    request: str
    proposal: CommandProposal | None = None
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    raw_response: str | None = None
