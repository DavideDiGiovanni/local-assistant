from pathlib import Path
from typing import Any

from local_assistant.models.agent_result import AgentResult
from local_assistant.tools.vault.append_note import AppendNote
from local_assistant.tools.vault.list_folders import ListFolders
from local_assistant.tools.vault.read_note import ReadNote
from local_assistant.tools.vault.search_notes import SearchNotes
from local_assistant.tools.vault.write_note import WriteNote


class VaultAgent:
    """
    Minimal domain agent for Markdown Vault operations.

    This agent owns the Vault domain.

    It does not parse natural language.
    It does not talk to an LLM.
    It does not know about orchestration.
    It only dispatches explicit Vault operations to the correct Vault tool.
    """

    SUPPORTED_OPERATIONS = {
        "read_note",
        "search_notes",
        "append_note",
        "write_note",
        "list_folders",
    }

    def __init__(self, vault_path: str | Path) -> None:
        self.vault_path = Path(vault_path).expanduser().resolve()

        self._read_note = ReadNote(self.vault_path)
        self._search_notes = SearchNotes(self.vault_path)
        self._append_note = AppendNote(self.vault_path)
        self._write_note = WriteNote(self.vault_path)
        self._list_folders = ListFolders(self.vault_path)

    def execute(self, operation: str, **kwargs: Any) -> AgentResult:
        """
        Execute an explicit Vault operation.

        Supported operations:

        - read_note(relative_path)
        - search_notes(query)
        - append_note(relative_path, content)
        - write_note(relative_path, content, overwrite=False)
        - list_folders(relative_path=".")
        """

        if operation not in self.SUPPORTED_OPERATIONS:
            return AgentResult(
                success=False,
                message="Unsupported Vault operation.",
                operation=operation,
                error="UNSUPPORTED_OPERATION",
                data={
                    "supported_operations": sorted(self.SUPPORTED_OPERATIONS),
                },
            )

        try:
            if operation == "read_note":
                return self.read_note(
                    relative_path=kwargs["relative_path"],
                )

            if operation == "search_notes":
                return self.search_notes(
                    query=kwargs["query"],
                )

            if operation == "append_note":
                return self.append_note(
                    relative_path=kwargs["relative_path"],
                    content=kwargs["content"],
                )

            if operation == "write_note":
                return self.write_note(
                    relative_path=kwargs["relative_path"],
                    content=kwargs["content"],
                    overwrite=kwargs.get("overwrite", False),
                )

            if operation == "list_folders":
                return self.list_folders(
                    relative_path=kwargs.get("relative_path", "."),
                )

        except KeyError as exc:
            return AgentResult(
                success=False,
                message="Missing required operation argument.",
                operation=operation,
                error="MISSING_ARGUMENT",
                data={
                    "missing_argument": str(exc).strip("'"),
                },
            )

        return AgentResult(
            success=False,
            message="Vault operation could not be executed.",
            operation=operation,
            error="EXECUTION_ERROR",
        )

    def read_note(self, relative_path: str) -> AgentResult:
        tool_result = self._read_note.run(relative_path)
        return AgentResult.from_tool_result(
            operation="read_note",
            tool_result=tool_result,
        )

    def search_notes(self, query: str) -> AgentResult:
        tool_result = self._search_notes.run(query)
        return AgentResult.from_tool_result(
            operation="search_notes",
            tool_result=tool_result,
        )

    def append_note(self, relative_path: str, content: str) -> AgentResult:
        tool_result = self._append_note.run(relative_path, content)
        return AgentResult.from_tool_result(
            operation="append_note",
            tool_result=tool_result,
        )

    def write_note(
        self,
        relative_path: str,
        content: str,
        overwrite: bool = False,
    ) -> AgentResult:
        tool_result = self._write_note.run(
            relative_path=relative_path,
            content=content,
            overwrite=overwrite,
        )
        return AgentResult.from_tool_result(
            operation="write_note",
            tool_result=tool_result,
        )

    def list_folders(self, relative_path: str = ".") -> AgentResult:
        tool_result = self._list_folders.run(relative_path=relative_path)
        return AgentResult.from_tool_result(
            operation="list_folders",
            tool_result=tool_result,
        )
