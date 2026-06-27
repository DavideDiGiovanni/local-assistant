from local_assistant.actions.controlled_ask import ControlledAsk
from local_assistant.llm.base_provider import BaseLLMProvider
from local_assistant.orchestrator.orchestrator import Orchestrator

PROMPT_TEMPLATE = "User request:\n{{request}}"


class FakeLLMProvider(BaseLLMProvider):
    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response


def test_controlled_ask_executes_search_notes(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Salesforce project note.", encoding="utf-8")

    llm = FakeLLMProvider(
        """
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
    )

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("cerca Salesforce")

    assert result.success is True
    assert result.proposal is not None
    assert result.proposal.operation == "search_notes"
    assert result.execution_result is not None
    assert result.execution_result.data["match_count"] == 1


def test_controlled_ask_executes_read_note(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test", encoding="utf-8")

    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "read_note",
          "arguments": {
            "relative_path": "note.md"
          },
          "requires_confirmation": false,
          "explanation": "Read note."
        }
        """
    )

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("leggi note.md")

    assert result.success is True
    assert result.proposal is not None
    assert result.proposal.operation == "read_note"
    assert result.execution_result is not None
    assert result.execution_result.data["content"] == "# Test"


def test_controlled_ask_requires_confirmation_for_write(tmp_path):
    llm = FakeLLMProvider(
        """
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
    )

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("crea note.md")

    assert result.success is False
    assert result.error == "CONFIRMATION_REQUIRED"
    assert result.proposal is not None
    assert result.proposal.requires_confirmation is True
    assert result.execution_result is None
    assert not (tmp_path / "note.md").exists()


def test_controlled_ask_writes_when_confirmed(tmp_path):
    llm = FakeLLMProvider(
        """
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
    )

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("crea note.md", confirm=True)

    assert result.success is True
    assert result.execution_result is not None
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "# Test"


def test_controlled_ask_requires_confirmation_for_append(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n", encoding="utf-8")

    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "append_note",
          "arguments": {
            "relative_path": "note.md",
            "content": "\\nAppend"
          },
          "requires_confirmation": false,
          "explanation": "Append note."
        }
        """
    )

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("aggiungi contenuto")

    assert result.success is False
    assert result.error == "CONFIRMATION_REQUIRED"
    assert note.read_text(encoding="utf-8") == "# Test\n"


def test_controlled_ask_appends_when_confirmed(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Test\n", encoding="utf-8")

    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "append_note",
          "arguments": {
            "relative_path": "note.md",
            "content": "\\nAppend"
          },
          "requires_confirmation": false,
          "explanation": "Append note."
        }
        """
    )

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("aggiungi contenuto", confirm=True)

    assert result.success is True
    assert note.read_text(encoding="utf-8") == "# Test\n\nAppend"


def test_controlled_ask_returns_proposal_error(tmp_path):
    llm = FakeLLMProvider("not json")

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("cerca Salesforce")

    assert result.success is False
    assert result.error == "INVALID_JSON"
    assert result.execution_result is None


def test_controlled_ask_requires_confirmation_for_delete_folder(tmp_path):
    (tmp_path / "projects").mkdir()

    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "delete_folder",
          "arguments": {
            "relative_path": "projects"
          },
          "requires_confirmation": false,
          "explanation": "Delete projects folder."
        }
        """
    )

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("elimina cartella projects")

    assert result.success is False
    assert result.error == "CONFIRMATION_REQUIRED"
    assert result.proposal is not None
    assert result.proposal.requires_confirmation is True
    assert result.execution_result is None
    assert (tmp_path / "projects").is_dir()


def test_controlled_ask_deletes_folder_when_confirmed(tmp_path):
    (tmp_path / "projects").mkdir()

    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "delete_folder",
          "arguments": {
            "relative_path": "projects"
          },
          "requires_confirmation": false,
          "explanation": "Delete projects folder."
        }
        """
    )

    action = ControlledAsk(
        llm_provider=llm,
        prompt_template=PROMPT_TEMPLATE,
        orchestrator=Orchestrator(tmp_path),
    )

    result = action.run("elimina cartella projects", confirm=True)

    assert result.success is True
    assert result.execution_result is not None
    assert not (tmp_path / "projects").exists()
