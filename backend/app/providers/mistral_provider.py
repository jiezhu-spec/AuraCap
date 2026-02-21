from __future__ import annotations

import base64

import httpx

from backend.app.providers.base import BaseProvider, ProviderError


class MistralProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str, text_model: str, mm_model: str, asr_model: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.text_model = text_model
        self.mm_model = mm_model
        self.asr_model = asr_model
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ProviderError("Mistral API key not configured", "AUTH_FAILED")
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def analyze_text(self, prompt: str, text: str) -> str:
        body = {
            "model": self.text_model,
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": text}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            r = await client.post(f"{self.base_url}/chat/completions", headers=self._headers(), json=body)
            if r.status_code >= 400:
                raise ProviderError(f"Mistral text request failed: {r.text}")
            return r.json()["choices"][0]["message"]["content"]

    async def analyze_multimodal(self, prompt: str, mime_type: str, payload: bytes) -> str:
        encoded = base64.b64encode(payload).decode("utf-8")
        body = {
            "model": self.mm_model,
            "messages": [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract information."},
                        {"type": "image_url", "image_url": f"data:{mime_type};base64,{encoded}"},
                    ],
                },
            ],
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            r = await client.post(f"{self.base_url}/chat/completions", headers=self._headers(), json=body)
            if r.status_code >= 400:
                raise ProviderError(f"Mistral multimodal request failed: {r.text}")
            return r.json()["choices"][0]["message"]["content"]

    async def transcribe_audio(self, mime_type: str, payload: bytes) -> str:
        encoded = base64.b64encode(payload).decode("utf-8")
        body = {"model": self.asr_model, "audio": {"data": encoded, "mime_type": mime_type}}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            r = await client.post(f"{self.base_url}/audio/transcriptions", headers=self._headers(), json=body)
            if r.status_code >= 400:
                raise ProviderError(f"Mistral ASR request failed: {r.text}")
            return r.json().get("text", "")
