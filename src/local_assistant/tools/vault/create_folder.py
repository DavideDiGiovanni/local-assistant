from pathlib import Path

from local_assistant.models.tool_result import ToolResult


class CreateFolder:

    def __init__(self, vault_path: Path) -> None:
        self.vault_path = vault_path.resolve()

    def run(self, relative_path: str) -> ToolResult:
        if relative_path is None:
            return ToolResult(
                success=False,
                message="Folder path is required.",
                error="EMPTY_FOLDER_PATH",
            )

        relative_path = relative_path.strip()

        if not relative_path or relative_path == ".":
            return ToolResult(
                success=False,
                message="Folder path is required.",
                error="EMPTY_FOLDER_PATH",
            )

        target_path = (self.vault_path / relative_path).resolve()

        if not self._is_inside_vault(target_path):
            return ToolResult(
                success=False,
                message="Path is outside the Vault.",
                error="PATH_OUTSIDE_VAULT",
            )

        if target_path.exists() and target_path.is_dir():
            return ToolResult(
                success=False,
                message="Folder already exists.",
                error="FOLDER_ALREADY_EXISTS",
            )

        if target_path.exists() and not target_path.is_dir():
            return ToolResult(
                success=False,
                message="Path already exists and is not a folder.",
                error="PATH_ALREADY_EXISTS_NOT_FOLDER",
            )

        target_path.mkdir(parents=True, exist_ok=False)

        if not target_path.exists() or not target_path.is_dir():
            return ToolResult(
                success=False,
                message="Folder creation could not be verified.",
                error="FOLDER_CREATION_NOT_VERIFIED",
            )

        return ToolResult(
            success=True,
            message="Folder created.",
            data={
                "relative_path": str(target_path.relative_to(self.vault_path)),
            },
        )

    def _is_inside_vault(self, path: Path) -> bool:
        return path == self.vault_path or self.vault_path in path.parents
