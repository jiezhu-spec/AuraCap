from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(RuntimeError):
    def __init__(self, message: str, code: str = "PROVIDER_UNAVAILABLE") -> None:
        super().__init__(message)
        self.code = code


class BaseProvider(ABC):
    @abstractmethod
    async def analyze_text(self, prompt: str, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def analyze_multimodal(self, prompt: str, mime_type: str, payload: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    async def transcribe_audio(self, mime_type: str, payload: bytes) -> str:
        raise NotImplementedError


class MockProvider(BaseProvider):
    async def analyze_text(self, prompt: str, text: str) -> str:
        return f"[mock-text]\nPrompt: {prompt[:80]}\nText: {text[:1200]}"

    async def analyze_multimodal(self, prompt: str, mime_type: str, payload: bytes) -> str:
        return (
            "[mock-mm]\n"
            f"Prompt: {prompt[:80]}\n"
            f"Mime: {mime_type}\n"
            f"PayloadBytes: {len(payload)}"
        )

    async def transcribe_audio(self, mime_type: str, payload: bytes) -> str:
        return f"[mock-asr] mime={mime_type} bytes={len(payload)}"
