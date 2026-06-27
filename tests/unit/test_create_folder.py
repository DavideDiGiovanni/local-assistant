from pathlib import Path

from local_assistant.tools.vault.create_folder import CreateFolder


def test_create_folder_creates_folder(tmp_path: Path) -> None:
    result = CreateFolder(tmp_path).run("projects")

    assert result.success is True
    assert result.data == {"relative_path": "projects"}
    assert (tmp_path / "projects").is_dir()


def test_create_folder_creates_nested_folder(tmp_path: Path) -> None:
    result = CreateFolder(tmp_path).run("projects/salesforce")

    assert result.success is True
    assert result.data == {"relative_path": "projects/salesforce"}
    assert (tmp_path / "projects" / "salesforce").is_dir()


def test_create_folder_rejects_empty_path(tmp_path: Path) -> None:
    result = CreateFolder(tmp_path).run("")

    assert result.success is False
    assert result.error == "EMPTY_FOLDER_PATH"


def test_create_folder_rejects_vault_root(tmp_path: Path) -> None:
    result = CreateFolder(tmp_path).run(".")

    assert result.success is False
    assert result.error == "EMPTY_FOLDER_PATH"


def test_create_folder_rejects_path_outside_vault(tmp_path: Path) -> None:
    result = CreateFolder(tmp_path).run("../outside")

    assert result.success is False
    assert result.error == "PATH_OUTSIDE_VAULT"


def test_create_folder_rejects_existing_folder(tmp_path: Path) -> None:
    (tmp_path / "projects").mkdir()

    result = CreateFolder(tmp_path).run("projects")

    assert result.success is False
    assert result.error == "FOLDER_ALREADY_EXISTS"


def test_create_folder_rejects_existing_file(tmp_path: Path) -> None:
    (tmp_path / "projects").write_text("not a folder", encoding="utf-8")

    result = CreateFolder(tmp_path).run("projects")

    assert result.success is False
    assert result.error == "PATH_ALREADY_EXISTS_NOT_FOLDER"
