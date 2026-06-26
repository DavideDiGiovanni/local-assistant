import json
from dataclasses import replace
from pathlib import PurePosixPath
from typing import Any

from local_assistant.llm.base_provider import BaseLLMProvider
from local_assistant.models.command_proposal import (
    CommandProposal,
    CommandProposalResult,
)


class CommandProposer:
    """
    Uses an LLM to propose a structured command.

    The LLM does not execute anything.

    It only proposes a JSON command that is then validated locally.
    """

    ALLOWED_OPERATIONS: dict[str, dict[str, set[str]]] = {
        "read_note": {
            "required": {"relative_path"},
            "optional": set(),
        },
        "search_notes": {
            "required": {"query"},
            "optional": set(),
        },
        "append_note": {
            "required": {"relative_path", "content"},
            "optional": set(),
        },
        "write_note": {
            "required": {"relative_path", "content"},
            "optional": {"overwrite"},
        },
    }

    WRITE_OPERATIONS = {
        "append_note",
        "write_note",
    }

    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        self.llm_provider = llm_provider

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

        validation_error = self._validate_proposal(proposal)

        if validation_error is not None:
            return CommandProposalResult(
                success=False,
                message="Command proposal failed validation.",
                request=normalized_request,
                proposal=proposal,
                error=validation_error,
                raw_response=raw_response,
            )

        proposal = self._normalize_confirmation(proposal)

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
        return f"""You are a command proposal engine for a local assistant.

You do not execute commands. You only translate a natural language request into one structured JSON object.

The assistant currently supports only the "vault" domain.

Allowed operations:

1. read_note
Required arguments:
- relative_path

2. search_notes
Required arguments:
- query

3. append_note
Required arguments:
- relative_path
- content

4. write_note
Required arguments:
- relative_path
- content
Optional arguments:
- overwrite

Rules:
- Return JSON only.
- Do not use Markdown.
- Do not add explanations outside the JSON object.
- Do not invent unsupported domains.
- Do not invent unsupported operations.
- Use relative paths only.
- Never use absolute paths.
- Never use paths containing "..".
- For write operations, set requires_confirmation to true.
- For read_note and search_notes, requires_confirmation may be false.
- If the request is unsupported, return domain "unsupported" and operation "unsupported".

JSON schema:

{{
  "domain": "vault",
  "operation": "search_notes",
  "arguments": {{
    "query": "example"
  }},
  "requires_confirmation": false,
  "explanation": "Short explanation of the proposed command."
}}

User request:

{request}"""

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

    def _validate_proposal(self, proposal: CommandProposal) -> str | None:
        if proposal.domain != "vault":
            return "UNSUPPORTED_DOMAIN"

        if proposal.operation not in self.ALLOWED_OPERATIONS:
            return "UNSUPPORTED_OPERATION"

        operation_spec = self.ALLOWED_OPERATIONS[proposal.operation]
        required_args = operation_spec["required"]
        optional_args = operation_spec["optional"]
        allowed_args = required_args | optional_args

        received_args = set(proposal.arguments.keys())

        missing_args = required_args - received_args
        if missing_args:
            return "MISSING_REQUIRED_ARGUMENT"

        unknown_args = received_args - allowed_args
        if unknown_args:
            return "UNKNOWN_ARGUMENT"

        for arg_name in required_args:
            value = proposal.arguments.get(arg_name)

            if not isinstance(value, str):
                return "INVALID_ARGUMENT_TYPE"

            if not value.strip():
                return "EMPTY_ARGUMENT"

        if "relative_path" in proposal.arguments:
            relative_path = proposal.arguments["relative_path"]

            if not self._is_safe_relative_path(relative_path):
                return "UNSAFE_RELATIVE_PATH"

        if "overwrite" in proposal.arguments:
            overwrite = proposal.arguments["overwrite"]

            if not isinstance(overwrite, bool):
                return "INVALID_OVERWRITE_ARGUMENT"

        return None

    def _normalize_confirmation(
        self,
        proposal: CommandProposal,
    ) -> CommandProposal:
        if proposal.operation in self.WRITE_OPERATIONS:
            return replace(proposal, requires_confirmation=True)

        return proposal

    def _is_safe_relative_path(self, relative_path: str) -> bool:
        path = PurePosixPath(relative_path)

        if path.is_absolute():
            return False

        if ".." in path.parts:
            return False

        return True
