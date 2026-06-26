from local_assistant.config.settings import load_settings
from local_assistant.llm.ollama_provider import OllamaProvider


def main() -> None:
    settings = load_settings()

    if settings.llm_provider != "ollama":
        raise RuntimeError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )

    llm = OllamaProvider(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        timeout_seconds=settings.ollama_timeout_seconds,
    )

    response = llm.generate("Rispondi solo con: OK")

    print(response)


if __name__ == "__main__":
    main()
