from abc import ABC, abstractmethod
from pathlib import Path


class AIProvider(ABC):
    """Abstract base — swap implementations without touching the rest of the app."""

    @abstractmethod
    def suggest_name(self, file: Path) -> str: ...

    @abstractmethod
    def summarize(self, file: Path) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def available(self) -> bool: ...


class NoAIProvider(AIProvider):
    """Default provider — no AI, always works."""

    @property
    def name(self) -> str:
        return "No AI"

    @property
    def available(self) -> bool:
        return True

    def suggest_name(self, file: Path) -> str:
        return file.name

    def summarize(self, file: Path) -> str:
        return ""


class OllamaProvider(AIProvider):
    """Local AI via Ollama — private, no internet required."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    @property
    def name(self) -> str:
        return f"Ollama ({self.model})"

    @property
    def available(self) -> bool:
        try:
            import urllib.request
            urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=2)
            return True
        except Exception:
            return False

    def suggest_name(self, file: Path) -> str:
        # Reads first 500 chars of text files and asks the model for a clean name
        try:
            content = file.read_text(errors="ignore")[:500]
            return self._ask(
                f"Suggest a concise filename (no extension) for this content:\n{content}"
            )
        except Exception:
            return file.stem

    def summarize(self, file: Path) -> str:
        try:
            content = file.read_text(errors="ignore")[:2000]
            return self._ask(f"Summarize this document in 2 sentences:\n{content}")
        except Exception:
            return ""

    def _ask(self, prompt: str) -> str:
        import json, urllib.request
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["response"].strip()
