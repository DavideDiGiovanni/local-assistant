import os

from local_assistant.llm.ollama_provider import OllamaProvider


def main() -> None:
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    llm = OllamaProvider(
        model=model,
        base_url=base_url,
    )

    response = llm.generate("Rispondi solo con: OK")

    print(response)


if __name__ == "__main__":
    main()
