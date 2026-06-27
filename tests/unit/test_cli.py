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

    def fake_load_prompt(settings):
        return "User request:\n{{request}}"

    monkeypatch.setattr(
        "local_assistant.cli.build_llm_provider",
        fake_build_llm_provider,
    )
    monkeypatch.setattr(
        "local_assistant.cli.load_command_proposal_prompt",
        fake_load_prompt,
    )

    from local_assistant.cli import run_cli

    exit_code = run_cli(["propose", "cerca Salesforce"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert "operation: search_notes" in captured.out
    assert "Salesforce" in captured.out


def test_cli_execute_proposal_read_note(tmp_path, capsys):
    import json

    note = tmp_path / "note.md"
    note.write_text("# Test", encoding="utf-8")

    proposal_file = tmp_path / "proposal.json"
    proposal_file.write_text(
        json.dumps(
            {
                "domain": "vault",
                "operation": "read_note",
                "arguments": {
                    "relative_path": "note.md",
                },
                "explanation": "Read note.",
                "requires_confirmation": False,
            }
        ),
        encoding="utf-8",
    )

    from local_assistant.cli import run_cli

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "execute-proposal",
            str(proposal_file),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert "# Test" in captured.out


def test_cli_execute_proposal_write_requires_confirmation(tmp_path, capsys):
    import json

    proposal_file = tmp_path / "proposal.json"
    proposal_file.write_text(
        json.dumps(
            {
                "domain": "vault",
                "operation": "write_note",
                "arguments": {
                    "relative_path": "note.md",
                    "content": "# Test",
                },
                "explanation": "Write note.",
                "requires_confirmation": True,
            }
        ),
        encoding="utf-8",
    )

    from local_assistant.cli import run_cli

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "execute-proposal",
            str(proposal_file),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "CONFIRMATION_REQUIRED" in captured.out
    assert not (tmp_path / "note.md").exists()


def test_cli_execute_proposal_write_with_confirmation(tmp_path):
    import json

    proposal_file = tmp_path / "proposal.json"
    proposal_file.write_text(
        json.dumps(
            {
                "domain": "vault",
                "operation": "write_note",
                "arguments": {
                    "relative_path": "note.md",
                    "content": "# Test",
                },
                "explanation": "Write note.",
                "requires_confirmation": True,
            }
        ),
        encoding="utf-8",
    )

    from local_assistant.cli import run_cli

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "execute-proposal",
            str(proposal_file),
            "--confirm",
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "# Test"


def test_cli_ask_executes_search_notes(monkeypatch, tmp_path, capsys):
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

    def fake_load_prompt(settings):
        return "User request:\n{{request}}"

    monkeypatch.setattr(
        "local_assistant.cli.build_llm_provider",
        fake_build_llm_provider,
    )
    monkeypatch.setattr(
        "local_assistant.cli.load_command_proposal_prompt",
        fake_load_prompt,
    )

    note = tmp_path / "note.md"
    note.write_text("Salesforce project note.", encoding="utf-8")

    from local_assistant.cli import run_cli

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "ask",
            "cerca Salesforce",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert "operation: search_notes" in captured.out
    assert "matches: 1" in captured.out


def test_cli_ask_write_requires_confirmation(monkeypatch, tmp_path, capsys):
    from local_assistant.llm.base_provider import BaseLLMProvider

    class FakeLLMProvider(BaseLLMProvider):
        def generate(self, prompt: str) -> str:
            return """
            {
              "domain": "vault",
              "operation": "write_note",
              "arguments": {
                "relative_path": "note.md",
                "content": "# Test"
              },
              "requires_confirmation": false,
              "explanation": "Write note."
            }
            """

    def fake_build_llm_provider(settings):
        return FakeLLMProvider()

    def fake_load_prompt(settings):
        return "User request:\n{{request}}"

    monkeypatch.setattr(
        "local_assistant.cli.build_llm_provider",
        fake_build_llm_provider,
    )
    monkeypatch.setattr(
        "local_assistant.cli.load_command_proposal_prompt",
        fake_load_prompt,
    )

    from local_assistant.cli import run_cli

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "ask",
            "crea note.md",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "CONFIRMATION_REQUIRED" in captured.out
    assert not (tmp_path / "note.md").exists()


def test_cli_ask_write_with_confirmation(monkeypatch, tmp_path):
    from local_assistant.llm.base_provider import BaseLLMProvider

    class FakeLLMProvider(BaseLLMProvider):
        def generate(self, prompt: str) -> str:
            return """
            {
              "domain": "vault",
              "operation": "write_note",
              "arguments": {
                "relative_path": "note.md",
                "content": "# Test"
              },
              "requires_confirmation": false,
              "explanation": "Write note."
            }
            """

    def fake_build_llm_provider(settings):
        return FakeLLMProvider()

    def fake_load_prompt(settings):
        return "User request:\n{{request}}"

    monkeypatch.setattr(
        "local_assistant.cli.build_llm_provider",
        fake_build_llm_provider,
    )
    monkeypatch.setattr(
        "local_assistant.cli.load_command_proposal_prompt",
        fake_load_prompt,
    )

    from local_assistant.cli import run_cli

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "ask",
            "crea note.md",
            "--confirm",
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "# Test"


def test_cli_list_folders(tmp_path, capsys):
    (tmp_path / "projects").mkdir()
    (tmp_path / "daily").mkdir()
    (tmp_path / "note.md").write_text("# Note", encoding="utf-8")

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "list-folders",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert "folders: 2" in captured.out
    assert "projects" in captured.out
    assert "daily" in captured.out


def test_cli_list_folders_nested(tmp_path, capsys):
    (tmp_path / "projects" / "alpha").mkdir(parents=True)
    (tmp_path / "projects" / "beta").mkdir(parents=True)

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "list-folders",
            "projects",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert "folders: 2" in captured.out
    assert "projects/alpha" in captured.out
    assert "projects/beta" in captured.out


def test_cli_list_folders_missing(tmp_path, capsys):
    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "list-folders",
            "nonexistent",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "success: False" in captured.out
    assert "FOLDER_NOT_FOUND" in captured.out


def test_cli_create_folder(tmp_path, capsys):
    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "create-folder",
            "projects",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert (tmp_path / "projects").is_dir()


def test_cli_create_folder_already_exists(tmp_path, capsys):
    (tmp_path / "projects").mkdir()

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "create-folder",
            "projects",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "success: False" in captured.out
    assert "FOLDER_ALREADY_EXISTS" in captured.out


def test_cli_delete_folder(tmp_path, capsys):
    (tmp_path / "projects").mkdir()

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "delete-folder",
            "projects",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "success: True" in captured.out
    assert not (tmp_path / "projects").exists()


def test_cli_delete_folder_non_empty(tmp_path, capsys):
    (tmp_path / "projects").mkdir()
    (tmp_path / "projects" / "note.md").write_text("# Note", encoding="utf-8")

    exit_code = run_cli(
        [
            "--vault-path",
            str(tmp_path),
            "delete-folder",
            "projects",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "success: False" in captured.out
    assert "FOLDER_NOT_EMPTY" in captured.out
    assert (tmp_path / "projects").is_dir()
    assert (tmp_path / "projects" / "note.md").exists()
