from pathlib import Path


class PromptLoader:
    """
    Loads versioned prompt templates from a configured prompts directory.

    Prompts are source-controlled artifacts.
    The loader prevents path traversal outside the configured prompt root.
    """

    def __init__(self, prompts_path: str | Path) -> None:
        self.prompts_path = Path(prompts_path).expanduser().resolve()

    def load(self, relative_path: str) -> str:
        if not relative_path.strip():
            raise ValueError("Prompt path cannot be empty.")

        prompt_path = (self.prompts_path / relative_path).resolve()

        if not self._is_inside_prompts_path(prompt_path):
            raise ValueError("Refusing to load a prompt outside the prompts directory.")

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file does not exist: {prompt_path}")

        if not prompt_path.is_file():
            raise ValueError(f"Prompt path is not a file: {prompt_path}")

        return prompt_path.read_text(encoding="utf-8")

    def _is_inside_prompts_path(self, path: Path) -> bool:
        try:
            path.relative_to(self.prompts_path)
            return True
        except ValueError:
            return False
