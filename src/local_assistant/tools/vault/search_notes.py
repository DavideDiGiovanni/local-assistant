from pathlib import Path

from local_assistant.models.tool_result import ToolResult


class SearchNotes:
    """
    Tool that searches Markdown notes inside a configured Vault path.

    This tool performs one real operation:
    search text inside Markdown files.

    It does not know anything about LLMs, agents, memory or orchestration.
    """

    def __init__(self, vault_path: str | Path) -> None:
        self.vault_path = Path(vault_path).expanduser().resolve()

    def run(self, query: str) -> ToolResult:
        normalized_query = query.strip()

        if not normalized_query:
            return ToolResult(
                success=False,
                message="Missing search query.",
                error="EMPTY_QUERY",
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

        matches: list[dict[str, object]] = []
        query_lower = normalized_query.lower()

        for note_path in sorted(self.vault_path.rglob("*.md")):
            if not note_path.is_file():
                continue

            if not self._is_inside_vault(note_path.resolve()):
                continue

            try:
                content = note_path.read_text(encoding="utf-8")
            except OSError:
                continue

            for line_number, line in enumerate(content.splitlines(), start=1):
                if query_lower in line.lower():
                    matches.append(
                        {
                            "relative_path": str(note_path.relative_to(self.vault_path)),
                            "line_number": line_number,
                            "line": line,
                        }
                    )

        return ToolResult(
            success=True,
            message=f"Search completed. Found {len(matches)} match(es).",
            data={
                "query": normalized_query,
                "matches": matches,
                "match_count": len(matches),
            },
        )

    def _is_inside_vault(self, path: Path) -> bool:
        try:
            path.relative_to(self.vault_path)
            return True
        except ValueError:
            return False
