from local_assistant.agents.vault_agent import VaultAgent


def test_vault_agent_write_note(tmp_path):
    agent = VaultAgent(tmp_path)

    result = agent.execute(
        "write_note",
        relative_path="note.md",
        content="# Test\n\nContent.",
    )

    assert result.success is True
    assert result.operation == "write_note"
    assert result.error is None
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "# Test\n\nContent."


def test_vault_agent_read_note(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n\nContent.", encoding="utf-8")

    agent = VaultAgent(tmp_path)

    result = agent.execute(
        "read_note",
        relative_path="note.md",
    )

    assert result.success is True
    assert result.operation == "read_note"
    assert result.data["content"] == "# Test\n\nContent."


def test_vault_agent_search_notes(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("The Vault is searchable.", encoding="utf-8")

    agent = VaultAgent(tmp_path)

    result = agent.execute(
        "search_notes",
        query="Vault",
    )

    assert result.success is True
    assert result.operation == "search_notes"
    assert result.data["match_count"] == 1


def test_vault_agent_append_note(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n", encoding="utf-8")

    agent = VaultAgent(tmp_path)

    result = agent.execute(
        "append_note",
        relative_path="note.md",
        content="\nAppended.",
    )

    assert result.success is True
    assert result.operation == "append_note"
    assert note.read_text(encoding="utf-8") == "# Test\n\nAppended."


def test_vault_agent_rejects_unsupported_operation(tmp_path):
    agent = VaultAgent(tmp_path)

    result = agent.execute("delete_note", relative_path="note.md")

    assert result.success is False
    assert result.operation == "delete_note"
    assert result.error == "UNSUPPORTED_OPERATION"
    assert "delete_note" not in result.data["supported_operations"]


def test_vault_agent_reports_missing_argument(tmp_path):
    agent = VaultAgent(tmp_path)

    result = agent.execute("read_note")

    assert result.success is False
    assert result.operation == "read_note"
    assert result.error == "MISSING_ARGUMENT"
    assert result.data["missing_argument"] == "relative_path"


def test_vault_agent_preserves_tool_error(tmp_path):
    agent = VaultAgent(tmp_path)

    result = agent.execute(
        "read_note",
        relative_path="missing.md",
    )

    assert result.success is False
    assert result.operation == "read_note"
    assert result.error == "NOTE_NOT_FOUND"
    assert result.tool_result is not None
    assert result.tool_result.error == "NOTE_NOT_FOUND"


def test_vault_agent_does_not_overwrite_by_default(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Original", encoding="utf-8")

    agent = VaultAgent(tmp_path)

    result = agent.execute(
        "write_note",
        relative_path="note.md",
        content="New content",
    )

    assert result.success is False
    assert result.error == "NOTE_ALREADY_EXISTS"
    assert note.read_text(encoding="utf-8") == "Original"


def test_vault_agent_overwrites_when_explicitly_allowed(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Original", encoding="utf-8")

    agent = VaultAgent(tmp_path)

    result = agent.execute(
        "write_note",
        relative_path="note.md",
        content="New content",
        overwrite=True,
    )

    assert result.success is True
    assert result.data["overwritten"] is True
    assert note.read_text(encoding="utf-8") == "New content"


def test_vault_agent_list_folders(tmp_path):
    (tmp_path / "projects").mkdir()
    (tmp_path / "daily").mkdir()

    agent = VaultAgent(tmp_path)

    result = agent.execute("list_folders")

    assert result.success is True
    assert result.operation == "list_folders"
    assert len(result.data["folders"]) == 2


def test_vault_agent_list_folders_with_relative_path(tmp_path):
    (tmp_path / "projects" / "alpha").mkdir(parents=True)

    agent = VaultAgent(tmp_path)

    result = agent.execute("list_folders", relative_path="projects")

    assert result.success is True
    assert result.operation == "list_folders"
    assert result.data["folders"] == [
        {"name": "alpha", "relative_path": "projects/alpha"},
    ]


def test_vault_agent_creates_folder(tmp_path):
    agent = VaultAgent(tmp_path)

    result = agent.execute("create_folder", relative_path="projects")

    assert result.success is True
    assert result.operation == "create_folder"
    assert (tmp_path / "projects").is_dir()


def test_vault_agent_create_folder_reports_missing_argument(tmp_path):
    agent = VaultAgent(tmp_path)

    result = agent.execute("create_folder")

    assert result.success is False
    assert result.operation == "create_folder"
    assert result.error == "MISSING_ARGUMENT"
    assert result.data["missing_argument"] == "relative_path"


def test_vault_agent_deletes_folder(tmp_path):
    (tmp_path / "projects").mkdir()
    agent = VaultAgent(tmp_path)

    result = agent.execute("delete_folder", relative_path="projects")

    assert result.success is True
    assert result.operation == "delete_folder"
    assert not (tmp_path / "projects").exists()


def test_vault_agent_delete_folder_reports_missing_argument(tmp_path):
    agent = VaultAgent(tmp_path)

    result = agent.execute("delete_folder")

    assert result.success is False
    assert result.operation == "delete_folder"
    assert result.error == "MISSING_ARGUMENT"
    assert result.data["missing_argument"] == "relative_path"
