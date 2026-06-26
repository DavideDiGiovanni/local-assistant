from local_assistant.tools.vault.write_note import WriteNote


def test_write_note_creates_new_note(tmp_path):
    tool = WriteNote(tmp_path)

    result = tool.run("note.md", "# Test\n\nContent.")

    note = tmp_path / "note.md"

    assert result.success is True
    assert result.message == "Note written and verified successfully."
    assert note.exists()
    assert note.read_text(encoding="utf-8") == "# Test\n\nContent."
    assert result.data["relative_path"] == "note.md"
    assert result.data["created"] is True
    assert result.data["overwritten"] is False


def test_write_note_creates_nested_directories(tmp_path):
    tool = WriteNote(tmp_path)

    result = tool.run("folder/subfolder/note.md", "# Nested note")

    note = tmp_path / "folder" / "subfolder" / "note.md"

    assert result.success is True
    assert note.exists()
    assert note.read_text(encoding="utf-8") == "# Nested note"


def test_write_note_refuses_to_overwrite_by_default(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Original content", encoding="utf-8")

    tool = WriteNote(tmp_path)
    result = tool.run("note.md", "New content")

    assert result.success is False
    assert result.error == "NOTE_ALREADY_EXISTS"
    assert note.read_text(encoding="utf-8") == "Original content"


def test_write_note_overwrites_when_explicitly_allowed(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Original content", encoding="utf-8")

    tool = WriteNote(tmp_path)
    result = tool.run("note.md", "New content", overwrite=True)

    assert result.success is True
    assert note.read_text(encoding="utf-8") == "New content"
    assert result.data["created"] is False
    assert result.data["overwritten"] is True


def test_write_note_rejects_empty_path(tmp_path):
    tool = WriteNote(tmp_path)

    result = tool.run("", "# Content")

    assert result.success is False
    assert result.error == "EMPTY_PATH"


def test_write_note_rejects_empty_content(tmp_path):
    tool = WriteNote(tmp_path)

    result = tool.run("note.md", "   ")

    assert result.success is False
    assert result.error == "EMPTY_CONTENT"


def test_write_note_rejects_path_outside_vault(tmp_path):
    tool = WriteNote(tmp_path)

    result = tool.run("../outside.md", "# Content")

    assert result.success is False
    assert result.error == "PATH_OUTSIDE_VAULT"


def test_write_note_rejects_non_markdown_file(tmp_path):
    tool = WriteNote(tmp_path)

    result = tool.run("note.txt", "Content")

    assert result.success is False
    assert result.error == "NOT_MARKDOWN"


def test_write_note_missing_vault(tmp_path):
    missing_vault = tmp_path / "missing"

    tool = WriteNote(missing_vault)
    result = tool.run("note.md", "# Content")

    assert result.success is False
    assert result.error == "VAULT_NOT_FOUND"


def test_write_note_rejects_vault_path_that_is_not_directory(tmp_path):
    fake_vault = tmp_path / "vault.md"
    fake_vault.write_text("Not a directory", encoding="utf-8")

    tool = WriteNote(fake_vault)
    result = tool.run("note.md", "# Content")

    assert result.success is False
    assert result.error == "VAULT_NOT_DIRECTORY"
