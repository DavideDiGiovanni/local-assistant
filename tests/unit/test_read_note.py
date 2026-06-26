from local_assistant.tools.vault.read_note import ReadNote


def test_read_note_success(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n\nHello.", encoding="utf-8")

    tool = ReadNote(tmp_path)
    result = tool.run("note.md")

    assert result.success is True
    assert result.message == "Note read successfully."
    assert result.data["content"] == "# Test\n\nHello."
    assert result.data["relative_path"] == "note.md"


def test_read_note_missing_file(tmp_path):
    tool = ReadNote(tmp_path)
    result = tool.run("missing.md")

    assert result.success is False
    assert result.error == "NOTE_NOT_FOUND"


def test_read_note_rejects_empty_path(tmp_path):
    tool = ReadNote(tmp_path)
    result = tool.run("")

    assert result.success is False
    assert result.error == "EMPTY_PATH"


def test_read_note_rejects_path_outside_vault(tmp_path):
    outside = tmp_path.parent / "outside.md"
    outside.write_text("Secret", encoding="utf-8")

    tool = ReadNote(tmp_path)
    result = tool.run("../outside.md")

    assert result.success is False
    assert result.error == "PATH_OUTSIDE_VAULT"


def test_read_note_rejects_non_markdown_file(tmp_path):
    text_file = tmp_path / "note.txt"
    text_file.write_text("Not markdown", encoding="utf-8")

    tool = ReadNote(tmp_path)
    result = tool.run("note.txt")

    assert result.success is False
    assert result.error == "NOT_MARKDOWN"
