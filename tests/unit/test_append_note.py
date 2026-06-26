from local_assistant.tools.vault.append_note import AppendNote


def test_append_note_success(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n", encoding="utf-8")

    tool = AppendNote(tmp_path)
    result = tool.run("note.md", "\nAppended content.")

    assert result.success is True
    assert result.message == "Content appended and verified successfully."
    assert note.read_text(encoding="utf-8") == "# Test\n\nAppended content."
    assert result.data["relative_path"] == "note.md"


def test_append_note_adds_newline_when_missing(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test", encoding="utf-8")

    tool = AppendNote(tmp_path)
    result = tool.run("note.md", "Appended content.")

    assert result.success is True
    assert note.read_text(encoding="utf-8") == "# Test\nAppended content."


def test_append_note_does_not_add_newline_to_empty_file(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("", encoding="utf-8")

    tool = AppendNote(tmp_path)
    result = tool.run("note.md", "Appended content.")

    assert result.success is True
    assert note.read_text(encoding="utf-8") == "Appended content."


def test_append_note_rejects_empty_path(tmp_path):
    tool = AppendNote(tmp_path)
    result = tool.run("", "Content")

    assert result.success is False
    assert result.error == "EMPTY_PATH"


def test_append_note_rejects_empty_content(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test", encoding="utf-8")

    tool = AppendNote(tmp_path)
    result = tool.run("note.md", "")

    assert result.success is False
    assert result.error == "EMPTY_CONTENT"


def test_append_note_rejects_missing_note(tmp_path):
    tool = AppendNote(tmp_path)
    result = tool.run("missing.md", "Content")

    assert result.success is False
    assert result.error == "NOTE_NOT_FOUND"


def test_append_note_rejects_path_outside_vault(tmp_path):
    outside = tmp_path.parent / "outside.md"
    outside.write_text("Secret", encoding="utf-8")

    tool = AppendNote(tmp_path)
    result = tool.run("../outside.md", "Content")

    assert result.success is False
    assert result.error == "PATH_OUTSIDE_VAULT"


def test_append_note_rejects_non_markdown_file(tmp_path):
    text_file = tmp_path / "note.txt"
    text_file.write_text("Text", encoding="utf-8")

    tool = AppendNote(tmp_path)
    result = tool.run("note.txt", "Content")

    assert result.success is False
    assert result.error == "NOT_MARKDOWN"


def test_append_note_missing_vault(tmp_path):
    missing_vault = tmp_path / "missing"

    tool = AppendNote(missing_vault)
    result = tool.run("note.md", "Content")

    assert result.success is False
    assert result.error == "VAULT_NOT_FOUND"
