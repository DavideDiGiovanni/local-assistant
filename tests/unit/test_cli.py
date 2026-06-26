from local_assistant.cli import run_cli


def test_cli_read_note(tmp_path, capsys):
    note = tmp_path / "note.md"
    note.write_text("# Test\n\nContent.", encoding="utf-8")

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "read-note",
            "note.md",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert "# Test" in captured.out
    assert "Content." in captured.out


def test_cli_search_notes(tmp_path, capsys):
    note = tmp_path / "note.md"
    note.write_text("The Vault is searchable.", encoding="utf-8")

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "search-notes",
            "Vault",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert "matches: 1" in captured.out
    assert "note.md:1: The Vault is searchable." in captured.out


def test_cli_write_note(tmp_path, capsys):
    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "write-note",
            "note.md",
            "# Test",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "# Test"


def test_cli_write_note_refuses_overwrite_by_default(tmp_path, capsys):
    note = tmp_path / "note.md"
    note.write_text("Original", encoding="utf-8")

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "write-note",
            "note.md",
            "New content",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "success: False" in captured.out
    assert "NOTE_ALREADY_EXISTS" in captured.out
    assert note.read_text(encoding="utf-8") == "Original"


def test_cli_write_note_overwrites_when_allowed(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Original", encoding="utf-8")

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "write-note",
            "note.md",
            "New content",
            "--overwrite",
        ]
    )

    assert exit_code == 0
    assert note.read_text(encoding="utf-8") == "New content"


def test_cli_append_note(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n", encoding="utf-8")

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "append-note",
            "note.md",
            "\nAppended.",
        ]
    )

    assert exit_code == 0
    assert note.read_text(encoding="utf-8") == "# Test\n\nAppended."


def test_cli_write_note_from_content_file(tmp_path):
    content_file = tmp_path / "content.md"
    content_file.write_text("# From file", encoding="utf-8")

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "write-note",
            "note.md",
            "--content-file",
            str(content_file),
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "# From file"


def test_cli_returns_error_for_missing_note(tmp_path, capsys):
    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "read-note",
            "missing.md",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "success: False" in captured.out
    assert "NOTE_NOT_FOUND" in captured.out


def test_cli_json_output(tmp_path, capsys):
    note = tmp_path / "note.md"
    note.write_text("# Test", encoding="utf-8")

    exit_code = run_cli(
        [
            "--json",
            "--vault-path",
            str(tmp_path),
            "read-note",
            "note.md",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"success": true' in captured.out
    assert '"operation": "read_note"' in captured.out
    assert '"content": "# Test"' in captured.out


def test_cli_without_command_returns_error(capsys):
    exit_code = run_cli([])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Structured CLI for the Local Assistant." in captured.out


def test_cli_propose_command(monkeypatch, capsys):
    from local_assistant.llm.base_provider import BaseLLMProvider

    class FakeLLMProvider(BaseLLMProvider):
        def generate(self, prompt: str) -> str:
            return """
            {
              "domain": "vault",
              "operation": "search_notes",
              "arguments": {
                "query": "Salesforce"
              },
              "requires_confirmation": false,
              "explanation": "Search notes for Salesforce."
            }
            """

    def fake_build_llm_provider(settings):
        return FakeLLMProvider()

    monkeypatch.setattr(
        "local_assistant.cli.build_llm_provider",
        fake_build_llm_provider,
    )

    from local_assistant.cli import run_cli

    exit_code = run_cli(["propose", "cerca Salesforce"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert "operation: search_notes" in captured.out
    assert "Salesforce" in captured.out
