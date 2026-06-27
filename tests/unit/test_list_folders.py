from pathlib import Path

from local_assistant.tools.vault.list_folders import ListFolders


def test_list_folders_from_vault_root(tmp_path: Path) -> None:
    (tmp_path / "folder-a").mkdir()
    (tmp_path / "folder-b").mkdir()
    (tmp_path / "note.md").write_text("# Note", encoding="utf-8")

    result = ListFolders(tmp_path).run()

    assert result.success is True
    assert result.data == {
        "relative_path": ".",
        "folders": [
            {"name": "folder-a", "relative_path": "folder-a"},
            {"name": "folder-b", "relative_path": "folder-b"},
        ],
    }


def test_list_folders_from_nested_folder(tmp_path: Path) -> None:
    (tmp_path / "parent" / "child").mkdir(parents=True)

    result = ListFolders(tmp_path).run("parent")

    assert result.success is True
    assert result.data == {
        "relative_path": "parent",
        "folders": [
            {"name": "child", "relative_path": "parent/child"},
        ],
    }


def test_list_folders_rejects_path_outside_vault(tmp_path: Path) -> None:
    result = ListFolders(tmp_path).run("../outside")

    assert result.success is False
    assert result.error == "PATH_OUTSIDE_VAULT"


def test_list_folders_rejects_missing_folder(tmp_path: Path) -> None:
    result = ListFolders(tmp_path).run("missing")

    assert result.success is False
    assert result.error == "FOLDER_NOT_FOUND"


def test_list_folders_rejects_file_path(tmp_path: Path) -> None:
    (tmp_path / "note.md").write_text("# Note", encoding="utf-8")

    result = ListFolders(tmp_path).run("note.md")

    assert result.success is False
    assert result.error == "NOT_A_FOLDER"


def test_list_folders_empty_vault(tmp_path: Path) -> None:
    result = ListFolders(tmp_path).run()

    assert result.success is True
    assert result.data["folders"] == []
    assert result.message == "Found 0 folder(s)."


def test_list_folders_default_relative_path(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()

    result = ListFolders(tmp_path).run("")

    assert result.success is True
    assert result.data["relative_path"] == "."
    assert len(result.data["folders"]) == 1
