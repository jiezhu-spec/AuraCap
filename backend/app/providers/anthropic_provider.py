from __future__ import annotations

import base64

import httpx

from backend.app.providers.base import BaseProvider, ProviderError


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str, text_model: str, mm_model: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.text_model = text_model
        self.mm_model = mm_model
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ProviderError("Anthropic API key not configured", "AUTH_FAILED")
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    async def analyze_text(self, prompt: str, text: str) -> str:
        body = {
            "model": self.text_model,
            "max_tokens": 1200,
            "system": prompt,
            "messages": [{"role": "user", "content": [{"type": "text", "text": text}]}],
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            r = await client.post(f"{self.base_url}/v1/messages", headers=self._headers(), json=body)
            if r.status_code >= 400:
                raise ProviderError(f"Anthropic text request failed: {r.text}")
            data = r.json()
            return "\n".join(item.get("text", "") for item in data.get("content", []) if item.get("type") == "text")

    async def analyze_multimodal(self, prompt: str, mime_type: str, payload: bytes) -> str:
        encoded = base64.b64encode(payload).decode("utf-8")
        body = {
            "model": self.mm_model,
            "max_tokens": 1200,
            "system": prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": encoded}},
                        {"type": "text", "text": "提取结构化信息并输出。"},
                    ],
                }
            ],
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            r = await client.post(f"{self.base_url}/v1/messages", headers=self._headers(), json=body)
            if r.status_code >= 400:
                raise ProviderError(f"Anthropic multimodal request failed: {r.text}")
            data = r.json()
            return "\n".join(item.get("text", "") for item in data.get("content", []) if item.get("type") == "text")

    async def transcribe_audio(self, mime_type: str, payload: bytes) -> str:
        raise ProviderError("Anthropic ASR not configured, switch asr_provider", "PROVIDER_UNAVAILABLE")
