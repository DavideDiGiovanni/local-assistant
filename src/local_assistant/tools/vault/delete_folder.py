from pathlib import Path

from local_assistant.models.tool_result import ToolResult


class DeleteFolder:

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

        if not relative_path:
            return ToolResult(
                success=False,
                message="Folder path is required.",
                error="EMPTY_FOLDER_PATH",
            )

        raw_path = self.vault_path / relative_path
        target_path = raw_path.resolve()

        if not self._is_inside_vault(target_path):
            return ToolResult(
                success=False,
                message="Path is outside the Vault.",
                error="PATH_OUTSIDE_VAULT",
            )

        if target_path == self.vault_path:
            return ToolResult(
                success=False,
                message="Cannot delete the Vault root.",
                error="CANNOT_DELETE_VAULT_ROOT",
            )

        if raw_path.is_symlink():
            return ToolResult(
                success=False,
                message="Refusing to delete symbolic links.",
                error="SYMLINK_NOT_ALLOWED",
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

        if any(target_path.iterdir()):
            return ToolResult(
                success=False,
                message="Folder is not empty.",
                error="FOLDER_NOT_EMPTY",
            )

        target_path.rmdir()

        if target_path.exists():
            return ToolResult(
                success=False,
                message="Folder deletion could not be verified.",
                error="FOLDER_DELETION_NOT_VERIFIED",
            )

        return ToolResult(
            success=True,
            message="Folder deleted.",
            data={
                "relative_path": str(target_path.relative_to(self.vault_path)),
            },
        )

    def _is_inside_vault(self, path: Path) -> bool:
        return path == self.vault_path or self.vault_path in path.parents
