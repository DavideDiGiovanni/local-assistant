from pathlib import Path

from local_assistant.models.tool_result import ToolResult


class ListFolders:

    def __init__(self, vault_path: Path) -> None:
        self.vault_path = vault_path.resolve()

    def run(self, relative_path: str = ".") -> ToolResult:
        if relative_path is None:
            relative_path = "."

        relative_path = relative_path.strip()

        if not relative_path:
            relative_path = "."

        target_path = (self.vault_path / relative_path).resolve()

        if not self._is_inside_vault(target_path):
            return ToolResult(
                success=False,
                message="Path is outside the Vault.",
                error="PATH_OUTSIDE_VAULT",
            )

        if not target_path.exists():
            return ToolResult(
                success=False,
                message="Folder does not exist.",
                error="FOLDER_NOT_FOUND",
            )

        if not target_path.is_dir():
            return ToolResult(
                success=False,
                message="Path is not a folder.",
                error="NOT_A_FOLDER",
            )

        folders = sorted(
            [
                {
                    "name": child.name,
                    "relative_path": str(child.relative_to(self.vault_path)),
                }
                for child in target_path.iterdir()
                if child.is_dir()
            ],
            key=lambda item: item["relative_path"].lower(),
        )

        return ToolResult(
            success=True,
            message=f"Found {len(folders)} folder(s).",
            data={
                "relative_path": str(target_path.relative_to(self.vault_path)),
                "folders": folders,
            },
        )

    def _is_inside_vault(self, path: Path) -> bool:
        return path == self.vault_path or self.vault_path in path.parents
