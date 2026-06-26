import pytest

from local_assistant.llm.base_provider import BaseLLMProvider
from local_assistant.llm.command_proposer import CommandProposer

PROMPT_TEMPLATE = "User request:\n{{request}}"


class FakeLLMProvider(BaseLLMProvider):
    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response


def test_command_proposer_search_notes_success():
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

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("cerca Salesforce")

    assert result.success is True
    assert result.proposal is not None
    assert result.proposal.domain == "vault"
    assert result.proposal.operation == "search_notes"
    assert result.proposal.arguments == {"query": "Salesforce"}
    assert result.proposal.requires_confirmation is False


def test_command_proposer_read_note_success():
    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "read_note",
          "arguments": {
            "relative_path": "welcome.md"
          },
          "requires_confirmation": false,
          "explanation": "Read the requested note."
        }
        """
    )

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("leggi welcome.md")

    assert result.success is True
    assert result.proposal is not None
    assert result.proposal.operation == "read_note"
    assert result.proposal.arguments["relative_path"] == "welcome.md"


def test_command_proposer_forces_confirmation_for_write_operations():
    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "write_note",
          "arguments": {
            "relative_path": "ideas/test.md",
            "content": "# Test"
          },
          "requires_confirmation": false,
          "explanation": "Create a test note."
        }
        """
    )

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("crea una nota")

    assert result.success is True
    assert result.proposal is not None
    assert result.proposal.operation == "write_note"
    assert result.proposal.requires_confirmation is True


def test_command_proposer_rejects_invalid_json():
    llm = FakeLLMProvider("not json")

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("cerca Salesforce")

    assert result.success is False
    assert result.error == "INVALID_JSON"


def test_command_proposer_rejects_unsupported_domain():
    llm = FakeLLMProvider(
        """
        {
          "domain": "linux",
          "operation": "run_command",
          "arguments": {
            "command": "ls"
          },
          "requires_confirmation": true,
          "explanation": "Unsupported command."
        }
        """
    )

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("lista i file")

    assert result.success is False
    assert result.error == "UNSUPPORTED_DOMAIN"


def test_command_proposer_rejects_unsupported_operation():
    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "delete_note",
          "arguments": {
            "relative_path": "note.md"
          },
          "requires_confirmation": true,
          "explanation": "Delete note."
        }
        """
    )

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("elimina note.md")

    assert result.success is False
    assert result.error == "UNSUPPORTED_OPERATION"


def test_command_proposer_rejects_missing_required_argument():
    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "read_note",
          "arguments": {},
          "requires_confirmation": false,
          "explanation": "Read a note."
        }
        """
    )

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("leggi la nota")

    assert result.success is False
    assert result.error == "MISSING_REQUIRED_ARGUMENT"


def test_command_proposer_rejects_unsafe_relative_path():
    llm = FakeLLMProvider(
        """
        {
          "domain": "vault",
          "operation": "read_note",
          "arguments": {
            "relative_path": "../secret.md"
          },
          "requires_confirmation": false,
          "explanation": "Unsafe path."
        }
        """
    )

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("leggi file esterno")

    assert result.success is False
    assert result.error == "UNSAFE_RELATIVE_PATH"


def test_command_proposer_rejects_empty_request():
    llm = FakeLLMProvider("{}")

    proposer = CommandProposer(llm, prompt_template=PROMPT_TEMPLATE)
    result = proposer.propose("   ")

    assert result.success is False
    assert result.error == "EMPTY_REQUEST"


def test_command_proposer_requires_request_placeholder():
    llm = FakeLLMProvider("{}")

    proposer = CommandProposer(
        llm,
        prompt_template="Prompt without placeholder",
    )

    with pytest.raises(ValueError):
        proposer.propose("cerca Salesforce")
