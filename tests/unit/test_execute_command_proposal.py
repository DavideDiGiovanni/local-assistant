import json

from local_assistant.actions.execute_command_proposal import ExecuteCommandProposal
from local_assistant.models.command_proposal import CommandProposal
from local_assistant.orchestrator.orchestrator import Orchestrator


def test_execute_command_proposal_read_note(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test", encoding="utf-8")

    orchestrator = Orchestrator(tmp_path)
    executor = ExecuteCommandProposal(orchestrator)

    proposal = CommandProposal(
        domain="vault",
        operation="read_note",
        arguments={"relative_path": "note.md"},
        explanation="Read note.",
        requires_confirmation=False,
    )

    result = executor.execute(proposal)

    assert result.success is True
    assert result.operation == "read_note"
    assert result.data["content"] == "# Test"


def test_execute_command_proposal_search_notes(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Salesforce project note.", encoding="utf-8")

    orchestrator = Orchestrator(tmp_path)
    executor = ExecuteCommandProposal(orchestrator)

    proposal = CommandProposal(
        domain="vault",
        operation="search_notes",
        arguments={"query": "Salesforce"},
        explanation="Search notes.",
        requires_confirmation=False,
    )

    result = executor.execute(proposal)

    assert result.success is True
    assert result.operation == "search_notes"
    assert result.data["match_count"] == 1


def test_execute_command_proposal_requires_confirmation_for_write(tmp_path):
    orchestrator = Orchestrator(tmp_path)
    executor = ExecuteCommandProposal(orchestrator)

    proposal = CommandProposal(
        domain="vault",
        operation="write_note",
        arguments={
            "relative_path": "note.md",
            "content": "# Test",
        },
        explanation="Write note.",
        requires_confirmation=True,
    )

    result = executor.execute(proposal)

    assert result.success is False
    assert result.error == "CONFIRMATION_REQUIRED"
    assert not (tmp_path / "note.md").exists()


def test_execute_command_proposal_writes_when_confirmed(tmp_path):
    orchestrator = Orchestrator(tmp_path)
    executor = ExecuteCommandProposal(orchestrator)

    proposal = CommandProposal(
        domain="vault",
        operation="write_note",
        arguments={
            "relative_path": "note.md",
            "content": "# Test",
        },
        explanation="Write note.",
        requires_confirmation=True,
    )

    result = executor.execute(proposal, confirm=True)

    assert result.success is True
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "# Test"


def test_execute_command_proposal_appends_when_confirmed(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n", encoding="utf-8")

    orchestrator = Orchestrator(tmp_path)
    executor = ExecuteCommandProposal(orchestrator)

    proposal = CommandProposal(
        domain="vault",
        operation="append_note",
        arguments={
            "relative_path": "note.md",
            "content": "\nAppended.",
        },
        explanation="Append note.",
        requires_confirmation=True,
    )

    result = executor.execute(proposal, confirm=True)

    assert result.success is True
    assert note.read_text(encoding="utf-8") == "# Test\n\nAppended."


def test_execute_command_proposal_rejects_unsafe_path(tmp_path):
    orchestrator = Orchestrator(tmp_path)
    executor = ExecuteCommandProposal(orchestrator)

    proposal = CommandProposal(
        domain="vault",
        operation="read_note",
        arguments={"relative_path": "../secret.md"},
        explanation="Unsafe read.",
        requires_confirmation=False,
    )

    result = executor.execute(proposal)

    assert result.success is False
    assert result.error == "UNSAFE_RELATIVE_PATH"


def test_execute_command_proposal_reads_full_proposal_result_json(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test", encoding="utf-8")

    proposal_file = tmp_path / "proposal.json"
    proposal_file.write_text(
        json.dumps(
            {
                "success": True,
                "message": "Command proposal generated successfully.",
                "request": "leggi note.md",
                "proposal": {
                    "domain": "vault",
                    "operation": "read_note",
                    "arguments": {
                        "relative_path": "note.md",
                    },
                    "explanation": "Read note.",
                    "requires_confirmation": False,
                },
                "data": {},
                "error": None,
                "raw_response": "{}",
            }
        ),
        encoding="utf-8",
    )

    orchestrator = Orchestrator(tmp_path)
    executor = ExecuteCommandProposal(orchestrator)

    result = executor.execute_from_file(proposal_file)

    assert result.success is True
    assert result.operation == "read_note"
    assert result.data["content"] == "# Test"


def test_execute_command_proposal_rejects_invalid_json_file(tmp_path):
    proposal_file = tmp_path / "proposal.json"
    proposal_file.write_text("not json", encoding="utf-8")

    orchestrator = Orchestrator(tmp_path)
    executor = ExecuteCommandProposal(orchestrator)

    result = executor.execute_from_file(proposal_file)

    assert result.success is False
    assert result.error == "INVALID_PROPOSAL_JSON"
