import pytest

from local_assistant.prompting.prompt_loader import PromptLoader


def test_prompt_loader_loads_prompt(tmp_path):
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()

    prompt_file = prompt_dir / "prompt.md"
    prompt_file.write_text("Hello {{request}}", encoding="utf-8")

    loader = PromptLoader(prompt_dir)

    assert loader.load("prompt.md") == "Hello {{request}}"


def test_prompt_loader_loads_nested_prompt(tmp_path):
    prompt_dir = tmp_path / "prompts"
    nested_dir = prompt_dir / "system"
    nested_dir.mkdir(parents=True)

    prompt_file = nested_dir / "command.md"
    prompt_file.write_text("Command {{request}}", encoding="utf-8")

    loader = PromptLoader(prompt_dir)

    assert loader.load("system/command.md") == "Command {{request}}"


def test_prompt_loader_rejects_empty_path(tmp_path):
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()

    loader = PromptLoader(prompt_dir)

    with pytest.raises(ValueError):
        loader.load("   ")


def test_prompt_loader_rejects_path_outside_prompt_dir(tmp_path):
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()

    outside_file = tmp_path / "outside.md"
    outside_file.write_text("Outside", encoding="utf-8")

    loader = PromptLoader(prompt_dir)

    with pytest.raises(ValueError):
        loader.load("../outside.md")


def test_prompt_loader_rejects_missing_prompt(tmp_path):
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()

    loader = PromptLoader(prompt_dir)

    with pytest.raises(FileNotFoundError):
        loader.load("missing.md")
