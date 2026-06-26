from pathlib import Path

from local_assistant.models.tool_result import ToolResult


class WriteNote:
    """
    Tool that writes a Markdown note inside a configured Vault path.

    This tool performs one real write operation:
    create or overwrite a Markdown file.

    By default, it refuses to overwrite existing files.
    Overwrite must be requested explicitly.

    After writing, it verifies that the file exists and that its content
    exactly matches the requested content.
    """

    def __init__(self, vault_path: str | Path) -> None:
        self.vault_path = Path(vault_path).expanduser().resolve()

    def run(
        self,
        relative_path: str,
        content: str,
        overwrite: bool = False,
    ) -> ToolResult:
        if not relative_path:
            return ToolResult(
                success=False,
                message="Missing note path.",
                error="EMPTY_PATH",
            )

        if not content.strip():
            return ToolResult(
                success=False,
                message="Missing content to write.",
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
                message="Refusing to write a file outside the Vault.",
                error="PATH_OUTSIDE_VAULT",
                data={
                    "requested_path": relative_path,
                },
            )

        if note_path.suffix.lower() != ".md":
            return ToolResult(
                success=False,
                message="Refusing to write a non-Markdown file.",
                error="NOT_MARKDOWN",
                data={
                    "path": str(note_path),
                },
            )

        note_already_exists = note_path.exists()

        if note_already_exists and not note_path.is_file():
            return ToolResult(
                success=False,
                message="Path exists but is not a file.",
                error="NOT_A_FILE",
                data={
                    "path": str(note_path),
                },
            )

        if note_already_exists and not overwrite:
            return ToolResult(
                success=False,
                message="Note already exists. Refusing to overwrite without explicit permission.",
                error="NOTE_ALREADY_EXISTS",
                data={
                    "path": str(note_path),
                    "relative_path": relative_path,
                },
            )

        try:
            note_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return ToolResult(
                success=False,
                message="Failed to create note directory.",
                error="DIRECTORY_CREATE_ERROR",
                data={
                    "path": str(note_path.parent),
                    "details": str(exc),
                },
            )

        try:
            note_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            return ToolResult(
                success=False,
                message="Failed to write note.",
                error="WRITE_ERROR",
                data={
                    "path": str(note_path),
                    "details": str(exc),
                },
            )

        try:
            written_content = note_path.read_text(encoding="utf-8")
        except OSError as exc:
            return ToolResult(
                success=False,
                message="Failed to verify written note.",
                error="VERIFY_READ_ERROR",
                data={
                    "path": str(note_path),
                    "details": str(exc),
                },
            )

        if written_content != content:
            return ToolResult(
                success=False,
                message="Write verification failed.",
                error="VERIFY_FAILED",
                data={
                    "path": str(note_path),
                    "expected_size_bytes": len(content.encode("utf-8")),
                    "actual_size_bytes": len(written_content.encode("utf-8")),
                },
            )

        return ToolResult(
            success=True,
            message="Note written and verified successfully.",
            data={
                "path": str(note_path),
                "relative_path": relative_path,
                "created": not note_already_exists,
                "overwritten": note_already_exists and overwrite,
                "size_bytes": note_path.stat().st_size,
            },
        )

    def _is_inside_vault(self, path: Path) -> bool:
        try:
            path.relative_to(self.vault_path)
            return True
        except ValueError:
            return False
