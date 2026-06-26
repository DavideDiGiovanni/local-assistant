from pathlib import Path
from typing import Any

from local_assistant.agents.vault_agent import VaultAgent
from local_assistant.models.orchestrator_result import OrchestratorResult


class Orchestrator:
    """
    Minimal orchestrator.

    The orchestrator decides which domain agent should receive a request.

    Current supported domain:

    - vault

    It does not parse natural language.
    It does not call tools directly.
    It does not know implementation details of the Vault tools.
    """

    SUPPORTED_DOMAINS = {
        "vault",
    }

    def __init__(self, vault_path: str | Path) -> None:
        self._vault_agent = VaultAgent(vault_path)

    def execute(
        self,
        domain: str,
        operation: str,
        **kwargs: Any,
    ) -> OrchestratorResult:
        normalized_domain = domain.strip().lower()

        if not normalized_domain:
            return OrchestratorResult(
                success=False,
                message="Missing domain.",
                domain=domain,
                operation=operation,
                error="EMPTY_DOMAIN",
            )

        if normalized_domain not in self.SUPPORTED_DOMAINS:
            return OrchestratorResult(
                success=False,
                message="Unsupported domain.",
                domain=normalized_domain,
                operation=operation,
                error="UNSUPPORTED_DOMAIN",
                data={
                    "supported_domains": sorted(self.SUPPORTED_DOMAINS),
                },
            )

        if normalized_domain == "vault":
            agent_result = self._vault_agent.execute(operation, **kwargs)
            return OrchestratorResult.from_agent_result(
                domain=normalized_domain,
                agent_result=agent_result,
            )

        return OrchestratorResult(
            success=False,
            message="Domain could not be routed.",
            domain=normalized_domain,
            operation=operation,
            error="ROUTING_ERROR",
        )
