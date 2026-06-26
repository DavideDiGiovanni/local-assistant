from pathlib import Path

from local_assistant.models.tool_result import ToolResult


class ReadNote:
    """
    Tool that reads a Markdown note from a configured Vault path.

    This tool performs one real operation:
    read the content of a Markdown file.

    It does not know anything about LLMs, agents, memory or orchestration.
    """

    def __init__(self, vault_path: str | Path) -> None:
        self.vault_path = Path(vault_path).expanduser().resolve()

    def run(self, relative_path: str) -> ToolResult:
        if not relative_path:
            return ToolResult(
                success=False,
                message="Missing note path.",
                error="EMPTY_PATH",
            )

        note_path = (self.vault_path / relative_path).resolve()

        if not self._is_inside_vault(note_path):
            return ToolResult(
                success=False,
                message="Refusing to read a file outside the Vault.",
                error="PATH_OUTSIDE_VAULT",
                data={
                    "requested_path": relative_path,
                },
            )

        if note_path.suffix.lower() != ".md":
            return ToolResult(
                success=False,
                message="Refusing to read a non-Markdown file.",
                error="NOT_MARKDOWN",
                data={
                    "path": str(note_path),
                },
            )

        if not note_path.exists():
            return ToolResult(
                success=False,
                message="Note does not exist.",
                error="NOTE_NOT_FOUND",
                data={
                    "path": str(note_path),
                },
            )

        if not note_path.is_file():
            return ToolResult(
                success=False,
                message="Path is not a file.",
                error="NOT_A_FILE",
                data={
                    "path": str(note_path),
                },
            )

        try:
            content = note_path.read_text(encoding="utf-8")
        except OSError as exc:
            return ToolResult(
                success=False,
                message="Failed to read note.",
                error="READ_ERROR",
                data={
                    "path": str(note_path),
                    "details": str(exc),
                },
            )

        return ToolResult(
            success=True,
            message="Note read successfully.",
            data={
                "path": str(note_path),
                "relative_path": relative_path,
                "content": content,
                "size_bytes": note_path.stat().st_size,
            },
        )

    def _is_inside_vault(self, path: Path) -> bool:
        try:
            path.relative_to(self.vault_path)
            return True
        except ValueError:
            return False
