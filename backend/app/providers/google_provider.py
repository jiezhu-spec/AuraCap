from __future__ import annotations

import base64

import httpx

from backend.app.providers.base import BaseProvider, ProviderError


class GoogleProvider(BaseProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        text_model: str,
        mm_model: str,
        asr_model: str,
        timeout_seconds: int,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.text_model = text_model
        self.mm_model = mm_model
        self.asr_model = asr_model
        self.timeout_seconds = timeout_seconds

    def _url(self, model: str) -> str:
        if not self.api_key:
            raise ProviderError("Google API key not configured", "AUTH_FAILED")
        return f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"

    async def analyze_text(self, prompt: str, text: str) -> str:
        body = {
            "contents": [{"parts": [{"text": f"{prompt}\n\n{text}"}]}],
            "generationConfig": {"temperature": 0.2},
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            r = await client.post(self._url(self.text_model), json=body)
            if r.status_code >= 400:
                raise ProviderError(f"Google text request failed: {r.text}")
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def analyze_multimodal(self, prompt: str, mime_type: str, payload: bytes) -> str:
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime_type, "data": base64.b64encode(payload).decode("utf-8")}},
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.1},
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            r = await client.post(self._url(self.mm_model), json=body)
            if r.status_code >= 400:
                raise ProviderError(f"Google multimodal request failed: {r.text}")
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def transcribe_audio(self, mime_type: str, payload: bytes) -> str:
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": "Transcribe this audio accurately."},
                        {"inline_data": {"mime_type": mime_type, "data": base64.b64encode(payload).decode("utf-8")}},
                    ]
                }
            ],
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            r = await client.post(self._url(self.asr_model), json=body)
            if r.status_code >= 400:
                raise ProviderError(f"Google ASR request failed: {r.text}")
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
