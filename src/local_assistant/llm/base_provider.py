from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Base interface for language model providers.

    The rest of the application should depend on this abstraction,
    not on a specific provider such as Ollama.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a text response from a prompt.
        """
        raise NotImplementedError
