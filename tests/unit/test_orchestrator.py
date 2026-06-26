from local_assistant.orchestrator.orchestrator import Orchestrator


def test_orchestrator_routes_write_note_to_vault_agent(tmp_path):
    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="vault",
        operation="write_note",
        relative_path="note.md",
        content="# Test\n\nContent.",
    )

    assert result.success is True
    assert result.domain == "vault"
    assert result.operation == "write_note"
    assert result.error is None
    assert result.agent_result is not None
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "# Test\n\nContent."


def test_orchestrator_routes_read_note_to_vault_agent(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n\nContent.", encoding="utf-8")

    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="vault",
        operation="read_note",
        relative_path="note.md",
    )

    assert result.success is True
    assert result.domain == "vault"
    assert result.operation == "read_note"
    assert result.data["content"] == "# Test\n\nContent."


def test_orchestrator_routes_search_notes_to_vault_agent(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("The Vault is searchable.", encoding="utf-8")

    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="vault",
        operation="search_notes",
        query="Vault",
    )

    assert result.success is True
    assert result.domain == "vault"
    assert result.operation == "search_notes"
    assert result.data["match_count"] == 1


def test_orchestrator_routes_append_note_to_vault_agent(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n", encoding="utf-8")

    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="vault",
        operation="append_note",
        relative_path="note.md",
        content="\nAppended.",
    )

    assert result.success is True
    assert result.domain == "vault"
    assert result.operation == "append_note"
    assert note.read_text(encoding="utf-8") == "# Test\n\nAppended."


def test_orchestrator_rejects_unsupported_domain(tmp_path):
    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="linux",
        operation="run_command",
        command="ls",
    )

    assert result.success is False
    assert result.domain == "linux"
    assert result.operation == "run_command"
    assert result.error == "UNSUPPORTED_DOMAIN"
    assert result.agent_result is None
    assert result.data["supported_domains"] == ["vault"]


def test_orchestrator_rejects_empty_domain(tmp_path):
    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="   ",
        operation="read_note",
        relative_path="note.md",
    )

    assert result.success is False
    assert result.error == "EMPTY_DOMAIN"
    assert result.agent_result is None


def test_orchestrator_preserves_agent_error(tmp_path):
    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="vault",
        operation="read_note",
        relative_path="missing.md",
    )

    assert result.success is False
    assert result.domain == "vault"
    assert result.operation == "read_note"
    assert result.error == "NOTE_NOT_FOUND"
    assert result.agent_result is not None
    assert result.agent_result.error == "NOTE_NOT_FOUND"


def test_orchestrator_preserves_unsupported_vault_operation(tmp_path):
    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="vault",
        operation="delete_note",
        relative_path="note.md",
    )

    assert result.success is False
    assert result.domain == "vault"
    assert result.operation == "delete_note"
    assert result.error == "UNSUPPORTED_OPERATION"
    assert result.agent_result is not None


def test_orchestrator_normalizes_domain_case(tmp_path):
    orchestrator = Orchestrator(tmp_path)

    result = orchestrator.execute(
        domain="Vault",
        operation="write_note",
        relative_path="note.md",
        content="# Test",
    )

    assert result.success is True
    assert result.domain == "vault"
    assert result.operation == "write_note"
