from local_assistant.tools.vault.search_notes import SearchNotes


def test_search_notes_finds_match(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n\nThe Vault is important.", encoding="utf-8")

    tool = SearchNotes(tmp_path)
    result = tool.run("Vault")

    assert result.success is True
    assert result.data["match_count"] == 1
    assert result.data["matches"][0]["relative_path"] == "note.md"
    assert result.data["matches"][0]["line_number"] == 3
    assert result.data["matches"][0]["line"] == "The Vault is important."


def test_search_notes_is_case_insensitive(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Markdown notes are searchable.", encoding="utf-8")

    tool = SearchNotes(tmp_path)
    result = tool.run("markdown")

    assert result.success is True
    assert result.data["match_count"] == 1


def test_search_notes_returns_zero_matches(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Nothing relevant here.", encoding="utf-8")

    tool = SearchNotes(tmp_path)
    result = tool.run("Vault")

    assert result.success is True
    assert result.data["match_count"] == 0
    assert result.data["matches"] == []


def test_search_notes_rejects_empty_query(tmp_path):
    tool = SearchNotes(tmp_path)
    result = tool.run("   ")

    assert result.success is False
    assert result.error == "EMPTY_QUERY"


def test_search_notes_searches_nested_markdown_files(tmp_path):
    folder = tmp_path / "nested"
    folder.mkdir()

    note = folder / "note.md"
    note.write_text("Nested note contains Vault.", encoding="utf-8")

    tool = SearchNotes(tmp_path)
    result = tool.run("Vault")

    assert result.success is True
    assert result.data["match_count"] == 1
    assert result.data["matches"][0]["relative_path"] == "nested/note.md"


def test_search_notes_ignores_non_markdown_files(tmp_path):
    note = tmp_path / "note.txt"
    note.write_text("Vault appears here but should be ignored.", encoding="utf-8")

    tool = SearchNotes(tmp_path)
    result = tool.run("Vault")

    assert result.success is True
    assert result.data["match_count"] == 0


def test_search_notes_missing_vault(tmp_path):
    missing_vault = tmp_path / "missing"

    tool = SearchNotes(missing_vault)
    result = tool.run("Vault")

    assert result.success is False
    assert result.error == "VAULT_NOT_FOUND"
