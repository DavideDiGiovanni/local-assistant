import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    """
    Application settings.

    Settings are read from environment variables.

    This keeps personal paths, local model choices and provider-specific
    endpoints outside the source code.
    """

    llm_provider: str
    ollama_model: str
    ollama_base_url: str
    ollama_timeout_seconds: int
    vault_path: Path


def load_settings() -> AppSettings:
    return AppSettings(
        llm_provider=os.getenv("LOCAL_ASSISTANT_LLM_PROVIDER", "ollama"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_timeout_seconds=int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120")),
        vault_path=Path(
            os.getenv("LOCAL_ASSISTANT_VAULT_PATH", "examples/sample_vault")
        ).expanduser(),
    )
