from pathlib import Path

from local_assistant.tools.vault.delete_folder import DeleteFolder


def test_delete_folder_deletes_empty_folder(tmp_path: Path) -> None:
    (tmp_path / "projects").mkdir()

    result = DeleteFolder(tmp_path).run("projects")

    assert result.success is True
    assert result.data == {"relative_path": "projects"}
    assert not (tmp_path / "projects").exists()


def test_delete_folder_deletes_empty_nested_folder(tmp_path: Path) -> None:
    (tmp_path / "projects" / "archive").mkdir(parents=True)

    result = DeleteFolder(tmp_path).run("projects/archive")

    assert result.success is True
    assert result.data == {"relative_path": "projects/archive"}
    assert not (tmp_path / "projects" / "archive").exists()
    assert (tmp_path / "projects").is_dir()


def test_delete_folder_rejects_empty_path(tmp_path: Path) -> None:
    result = DeleteFolder(tmp_path).run("")

    assert result.success is False
    assert result.error == "EMPTY_FOLDER_PATH"


def test_delete_folder_rejects_vault_root(tmp_path: Path) -> None:
    result = DeleteFolder(tmp_path).run(".")

    assert result.success is False
    assert result.error == "CANNOT_DELETE_VAULT_ROOT"
    assert tmp_path.exists()


def test_delete_folder_rejects_path_outside_vault(tmp_path: Path) -> None:
    result = DeleteFolder(tmp_path).run("../outside")

    assert result.success is False
    assert result.error == "PATH_OUTSIDE_VAULT"


def test_delete_folder_rejects_missing_folder(tmp_path: Path) -> None:
    result = DeleteFolder(tmp_path).run("missing")

    assert result.success is False
    assert result.error == "FOLDER_NOT_FOUND"


def test_delete_folder_rejects_file_path(tmp_path: Path) -> None:
    (tmp_path / "note.md").write_text("# Note", encoding="utf-8")

    result = DeleteFolder(tmp_path).run("note.md")

    assert result.success is False
    assert result.error == "NOT_A_FOLDER"
    assert (tmp_path / "note.md").exists()


def test_delete_folder_rejects_non_empty_folder(tmp_path: Path) -> None:
    (tmp_path / "projects").mkdir()
    (tmp_path / "projects" / "note.md").write_text("# Note", encoding="utf-8")

    result = DeleteFolder(tmp_path).run("projects")

    assert result.success is False
    assert result.error == "FOLDER_NOT_EMPTY"
    assert (tmp_path / "projects").is_dir()
    assert (tmp_path / "projects" / "note.md").exists()


def test_delete_folder_rejects_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()

    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)

    result = DeleteFolder(tmp_path).run("link")

    assert result.success is False
    assert result.error == "SYMLINK_NOT_ALLOWED"
    assert link.exists()
    assert target.exists()
