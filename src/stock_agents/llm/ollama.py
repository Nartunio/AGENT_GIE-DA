from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class OllamaClient:
    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: int = 120

    def generate(self, model: str, prompt: str, system: str | None = None) -> str:
        payload: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.25,
                "num_ctx": 8192,
            },
        }
        if system:
            payload["system"] = system

        response = httpx.post(
            f"{self.base_url.rstrip('/')}/api/generate",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return str(data.get("response", "")).strip()

    def is_available(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url.rstrip('/')}/api/tags", timeout=3)
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False
