from pathlib import Path

from local_assistant.models.tool_result import ToolResult


class AppendNote:
    """
    Tool that appends text to an existing Markdown note.

    This tool performs one real write operation:
    append content to a Markdown file.

    After writing, it verifies that the file content actually changed
    and that the appended content is present at the end of the note.
    """

    def __init__(self, vault_path: str | Path) -> None:
        self.vault_path = Path(vault_path).expanduser().resolve()

    def run(self, relative_path: str, content: str) -> ToolResult:
        if not relative_path:
            return ToolResult(
                success=False,
                message="Missing note path.",
                error="EMPTY_PATH",
            )

        if not content:
            return ToolResult(
                success=False,
                message="Missing content to append.",
                error="EMPTY_CONTENT",
            )

        if not self.vault_path.exists():
            return ToolResult(
                success=False,
                message="Vault path does not exist.",
                error="VAULT_NOT_FOUND",
                data={
                    "vault_path": str(self.vault_path),
                },
            )

        if not self.vault_path.is_dir():
            return ToolResult(
                success=False,
                message="Vault path is not a directory.",
                error="VAULT_NOT_DIRECTORY",
                data={
                    "vault_path": str(self.vault_path),
                },
            )

        note_path = (self.vault_path / relative_path).resolve()

        if not self._is_inside_vault(note_path):
            return ToolResult(
                success=False,
                message="Refusing to modify a file outside the Vault.",
                error="PATH_OUTSIDE_VAULT",
                data={
                    "requested_path": relative_path,
                },
            )

        if note_path.suffix.lower() != ".md":
            return ToolResult(
                success=False,
                message="Refusing to modify a non-Markdown file.",
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
            before_content = note_path.read_text(encoding="utf-8")
        except OSError as exc:
            return ToolResult(
                success=False,
                message="Failed to read note before append.",
                error="READ_ERROR",
                data={
                    "path": str(note_path),
                    "details": str(exc),
                },
            )

        appended_content = self._build_appended_content(before_content, content)

        try:
            note_path.write_text(before_content + appended_content, encoding="utf-8")
        except OSError as exc:
            return ToolResult(
                success=False,
                message="Failed to append content to note.",
                error="WRITE_ERROR",
                data={
                    "path": str(note_path),
                    "details": str(exc),
                },
            )

        try:
            after_content = note_path.read_text(encoding="utf-8")
        except OSError as exc:
            return ToolResult(
                success=False,
                message="Failed to verify appended note.",
                error="VERIFY_READ_ERROR",
                data={
                    "path": str(note_path),
                    "details": str(exc),
                },
            )

        expected_content = before_content + appended_content

        if after_content != expected_content:
            return ToolResult(
                success=False,
                message="Append verification failed.",
                error="VERIFY_FAILED",
                data={
                    "path": str(note_path),
                    "before_size_bytes": len(before_content.encode("utf-8")),
                    "after_size_bytes": len(after_content.encode("utf-8")),
                },
            )

        return ToolResult(
            success=True,
            message="Content appended and verified successfully.",
            data={
                "path": str(note_path),
                "relative_path": relative_path,
                "appended_content": appended_content,
                "before_size_bytes": len(before_content.encode("utf-8")),
                "after_size_bytes": len(after_content.encode("utf-8")),
            },
        )

    def _build_appended_content(self, before_content: str, content: str) -> str:
        """
        Make append behavior predictable.

        If the existing note is empty, append the content as-is.
        If the existing note does not end with a newline, insert one newline.
        If it already ends with a newline, append directly.
        """

        if not before_content:
            return content

        if before_content.endswith("\n"):
            return content

        return "\n" + content

    def _is_inside_vault(self, path: Path) -> bool:
        try:
            path.relative_to(self.vault_path)
            return True
        except ValueError:
            return False
