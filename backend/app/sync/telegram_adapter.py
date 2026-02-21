from __future__ import annotations

import httpx

from backend.app.models.schemas import DeliveryResult, SyncEvent
from backend.app.sync.base_adapter import SyncAdapter


class TelegramAdapter(SyncAdapter):
    channel = "telegram"

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    async def send(self, event: SyncEvent) -> DeliveryResult:
        if not self.bot_token or not self.chat_id:
            return DeliveryResult(channel=self.channel, success=False, detail="Missing token/chat_id")
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": f"{event.title}\n\n{event.body}"}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, json=payload)
        ok = resp.status_code < 400
        return DeliveryResult(channel=self.channel, success=ok, detail=f"status={resp.status_code}")
