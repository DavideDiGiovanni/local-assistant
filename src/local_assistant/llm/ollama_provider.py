import json
import urllib.error
import urllib.request

from local_assistant.llm.base_provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """
    Minimal Ollama provider.

    This provider talks to the local Ollama HTTP API.
    It does not know anything about agents, tools, memory or orchestration.
    """

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout_seconds: int = 120,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                raw_body = response.read().decode("utf-8")

        except urllib.error.URLError as exc:
            raise RuntimeError(f"Failed to connect to Ollama at {url}") from exc

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned invalid JSON") from exc

        if "error" in body:
            raise RuntimeError(f"Ollama error: {body['error']}")

        if "response" not in body:
            raise RuntimeError("Ollama response does not contain 'response' field")

        return body["response"].strip()
