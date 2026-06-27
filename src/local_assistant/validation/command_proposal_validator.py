from dataclasses import replace
from pathlib import PurePosixPath

from local_assistant.models.command_proposal import CommandProposal


class CommandProposalValidator:
    """
    Shared validator for CommandProposal objects.

    Validation is used both when the LLM proposes a command and when a proposal
    is executed.

    This keeps the rules centralized while preserving multiple validation gates.
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
        "list_folders": {
            "required": set(),
            "optional": {"relative_path"},
        },
        "create_folder": {
            "required": {"relative_path"},
            "optional": set(),
        },
        "delete_folder": {
            "required": {"relative_path"},
            "optional": set(),
        },
    }

    WRITE_OPERATIONS = {
        "append_note",
        "write_note",
        "create_folder",
        "delete_folder",
    }

    def validate(self, proposal: CommandProposal) -> str | None:
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

            if not isinstance(relative_path, str):
                return "INVALID_ARGUMENT_TYPE"

            if not self._is_safe_relative_path(relative_path):
                return "UNSAFE_RELATIVE_PATH"

        if "overwrite" in proposal.arguments:
            overwrite = proposal.arguments["overwrite"]

            if not isinstance(overwrite, bool):
                return "INVALID_OVERWRITE_ARGUMENT"

        return None

    def requires_confirmation(self, proposal: CommandProposal) -> bool:
        return proposal.operation in self.WRITE_OPERATIONS

    def normalize_confirmation(
        self,
        proposal: CommandProposal,
    ) -> CommandProposal:
        if self.requires_confirmation(proposal):
            return replace(proposal, requires_confirmation=True)

        return proposal

    def _is_safe_relative_path(self, relative_path: str) -> bool:
        path = PurePosixPath(relative_path)

        if path.is_absolute():
            return False

        if ".." in path.parts:
            return False

        return True
