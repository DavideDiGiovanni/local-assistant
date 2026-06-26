import json
from typing import Any

from local_assistant.llm.base_provider import BaseLLMProvider
from local_assistant.models.command_proposal import (
    CommandProposal,
    CommandProposalResult,
)
from local_assistant.validation.command_proposal_validator import (
    CommandProposalValidator,
)


class CommandProposer:
    """
    Uses an LLM to propose a structured command.

    The LLM does not execute anything.

    It only proposes a JSON command that is then validated locally.
    The prompt template is loaded outside this class and injected.
    """

    REQUEST_PLACEHOLDER = "{{request}}"

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        prompt_template: str,
        validator: CommandProposalValidator | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.prompt_template = prompt_template
        self.validator = validator or CommandProposalValidator()

    def propose(self, request: str) -> CommandProposalResult:
        normalized_request = request.strip()

        if not normalized_request:
            return CommandProposalResult(
                success=False,
                message="Missing natural language request.",
                request=request,
                error="EMPTY_REQUEST",
            )

        prompt = self._build_prompt(normalized_request)
        raw_response = self.llm_provider.generate(prompt)

        try:
            payload = self._extract_json_object(raw_response)
        except ValueError as exc:
            return CommandProposalResult(
                success=False,
                message="LLM response did not contain a valid JSON object.",
                request=normalized_request,
                error="INVALID_JSON",
                raw_response=raw_response,
                data={
                    "details": str(exc),
                },
            )

        proposal = self._proposal_from_payload(payload)

        validation_error = self.validator.validate(proposal)

        if validation_error is not None:
            return CommandProposalResult(
                success=False,
                message="Command proposal failed validation.",
                request=normalized_request,
                proposal=proposal,
                error=validation_error,
                raw_response=raw_response,
            )

        proposal = self.validator.normalize_confirmation(proposal)

        return CommandProposalResult(
            success=True,
            message="Command proposal generated successfully.",
            request=normalized_request,
            proposal=proposal,
            raw_response=raw_response,
            data={
                "domain": proposal.domain,
                "operation": proposal.operation,
                "arguments": proposal.arguments,
                "requires_confirmation": proposal.requires_confirmation,
                "explanation": proposal.explanation,
            },
        )

    def _build_prompt(self, request: str) -> str:
        if self.REQUEST_PLACEHOLDER not in self.prompt_template:
            raise ValueError(
                f"Prompt template must contain {self.REQUEST_PLACEHOLDER} placeholder."
            )

        return self.prompt_template.replace(self.REQUEST_PLACEHOLDER, request)

    def _extract_json_object(self, raw_response: str) -> dict[str, Any]:
        start = raw_response.find("{")
        end = raw_response.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found.")

        json_text = raw_response[start : end + 1]

        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise ValueError(str(exc)) from exc

        if not isinstance(payload, dict):
            raise ValueError("JSON payload is not an object.")

        return payload

    def _proposal_from_payload(self, payload: dict[str, Any]) -> CommandProposal:
        domain = payload.get("domain", "")
        operation = payload.get("operation", "")
        arguments = payload.get("arguments", {})
        explanation = payload.get("explanation", "")
        requires_confirmation = payload.get("requires_confirmation", True)

        if not isinstance(arguments, dict):
            arguments = {}

        if not isinstance(requires_confirmation, bool):
            requires_confirmation = True

        return CommandProposal(
            domain=str(domain).strip().lower(),
            operation=str(operation).strip(),
            arguments=arguments,
            explanation=str(explanation).strip(),
            requires_confirmation=requires_confirmation,
        )
