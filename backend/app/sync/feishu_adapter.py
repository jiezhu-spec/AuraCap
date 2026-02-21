from __future__ import annotations

import httpx

from backend.app.models.schemas import DeliveryResult, SyncEvent
from backend.app.sync.base_adapter import SyncAdapter


class FeishuAdapter(SyncAdapter):
    channel = "feishu"

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def send(self, event: SyncEvent) -> DeliveryResult:
        if not self.webhook_url:
            return DeliveryResult(channel=self.channel, success=False, detail="Missing webhook")
        payload = {"msg_type": "text", "content": {"text": f"{event.title}\n{event.body}"}}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(self.webhook_url, json=payload)
        ok = resp.status_code < 400
        return DeliveryResult(channel=self.channel, success=ok, detail=f"status={resp.status_code}")
