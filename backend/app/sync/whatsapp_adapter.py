from __future__ import annotations

import httpx

from backend.app.models.schemas import DeliveryResult, SyncEvent
from backend.app.sync.base_adapter import SyncAdapter


class WhatsAppAdapter(SyncAdapter):
    channel = "whatsapp"

    def __init__(self, gateway_url: str, token: str) -> None:
        self.gateway_url = gateway_url
        self.token = token

    async def send(self, event: SyncEvent) -> DeliveryResult:
        if not self.gateway_url or not self.token:
            return DeliveryResult(channel=self.channel, success=False, detail="Missing gateway/token")
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"text": f"{event.title}\n{event.body}"}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(self.gateway_url, headers=headers, json=payload)
        ok = resp.status_code < 400
        return DeliveryResult(channel=self.channel, success=ok, detail=f"status={resp.status_code}")
