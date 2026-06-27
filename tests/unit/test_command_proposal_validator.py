from local_assistant.models.command_proposal import CommandProposal
from local_assistant.validation.command_proposal_validator import (
    CommandProposalValidator,
)


def test_validator_accepts_search_notes():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="search_notes",
        arguments={"query": "Salesforce"},
        explanation="Search notes.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) is None


def test_validator_accepts_read_note():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="read_note",
        arguments={"relative_path": "daily/today.md"},
        explanation="Read note.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) is None


def test_validator_rejects_unsupported_domain():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="linux",
        operation="run_command",
        arguments={"command": "ls"},
        explanation="Unsupported.",
        requires_confirmation=True,
    )

    assert validator.validate(proposal) == "UNSUPPORTED_DOMAIN"


def test_validator_rejects_unsupported_operation():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="delete_note",
        arguments={"relative_path": "note.md"},
        explanation="Unsupported.",
        requires_confirmation=True,
    )

    assert validator.validate(proposal) == "UNSUPPORTED_OPERATION"


def test_validator_rejects_missing_required_argument():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="read_note",
        arguments={},
        explanation="Missing path.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) == "MISSING_REQUIRED_ARGUMENT"


def test_validator_rejects_unknown_argument():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="search_notes",
        arguments={
            "query": "Salesforce",
            "extra": "invalid",
        },
        explanation="Search notes.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) == "UNKNOWN_ARGUMENT"


def test_validator_rejects_empty_argument():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="search_notes",
        arguments={"query": "   "},
        explanation="Empty query.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) == "EMPTY_ARGUMENT"


def test_validator_rejects_absolute_relative_path():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="read_note",
        arguments={"relative_path": "/home/user/secret.md"},
        explanation="Unsafe path.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) == "UNSAFE_RELATIVE_PATH"


def test_validator_rejects_parent_directory_relative_path():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="read_note",
        arguments={"relative_path": "../secret.md"},
        explanation="Unsafe path.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) == "UNSAFE_RELATIVE_PATH"


def test_validator_rejects_invalid_overwrite_argument():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="write_note",
        arguments={
            "relative_path": "note.md",
            "content": "# Test",
            "overwrite": "true",
        },
        explanation="Invalid overwrite.",
        requires_confirmation=True,
    )

    assert validator.validate(proposal) == "INVALID_OVERWRITE_ARGUMENT"


def test_validator_requires_confirmation_for_write_operations():
    validator = CommandProposalValidator()

    write_proposal = CommandProposal(
        domain="vault",
        operation="write_note",
        arguments={
            "relative_path": "note.md",
            "content": "# Test",
        },
        explanation="Write note.",
        requires_confirmation=False,
    )

    append_proposal = CommandProposal(
        domain="vault",
        operation="append_note",
        arguments={
            "relative_path": "note.md",
            "content": "Append",
        },
        explanation="Append note.",
        requires_confirmation=False,
    )

    assert validator.requires_confirmation(write_proposal) is True
    assert validator.requires_confirmation(append_proposal) is True


def test_validator_does_not_require_confirmation_for_read_operations():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="search_notes",
        arguments={"query": "Salesforce"},
        explanation="Search notes.",
        requires_confirmation=False,
    )

    assert validator.requires_confirmation(proposal) is False


def test_validator_normalizes_confirmation_for_write_operations():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="write_note",
        arguments={
            "relative_path": "note.md",
            "content": "# Test",
        },
        explanation="Write note.",
        requires_confirmation=False,
    )

    normalized = validator.normalize_confirmation(proposal)

    assert normalized.requires_confirmation is True


def test_validator_accepts_list_folders_without_arguments():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="list_folders",
        arguments={},
        explanation="List folders in the Vault root.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) is None


def test_validator_accepts_list_folders_with_relative_path():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="list_folders",
        arguments={"relative_path": "projects"},
        explanation="List folders in projects.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) is None


def test_validator_rejects_list_folders_unknown_argument():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="list_folders",
        arguments={"unknown": "value"},
        explanation="List folders.",
        requires_confirmation=False,
    )

    assert validator.validate(proposal) == "UNKNOWN_ARGUMENT"


def test_validator_does_not_require_confirmation_for_list_folders():
    validator = CommandProposalValidator()

    proposal = CommandProposal(
        domain="vault",
        operation="list_folders",
        arguments={},
        explanation="List folders.",
        requires_confirmation=False,
    )

    assert validator.requires_confirmation(proposal) is False
