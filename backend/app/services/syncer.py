from __future__ import annotations

from backend.app.core.config import Settings
from backend.app.models.schemas import DeliveryResult, SyncEvent
from backend.app.sync.discord_adapter import DiscordAdapter
from backend.app.sync.feishu_adapter import FeishuAdapter
from backend.app.sync.telegram_adapter import TelegramAdapter
from backend.app.sync.whatsapp_adapter import WhatsAppAdapter


class SyncService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.adapters = []
        if settings.feishu_enabled:
            self.adapters.append(FeishuAdapter(settings.feishu_webhook_url))
        if settings.telegram_enabled:
            self.adapters.append(TelegramAdapter(settings.telegram_bot_token, settings.telegram_chat_id))
        if settings.discord_enabled:
            self.adapters.append(DiscordAdapter(settings.discord_webhook_url))
        if settings.whatsapp_enabled:
            self.adapters.append(WhatsAppAdapter(settings.whatsapp_gateway_url, settings.whatsapp_token))

    def should_send(self, event_type: str) -> bool:
        if event_type == "timeline":
            return self.settings.sync_send_timeline
        if event_type == "insight":
            return self.settings.sync_send_insight
        if event_type == "summary":
            return self.settings.sync_send_summary
        if event_type == "customized":
            return self.settings.sync_send_customized
        if event_type == "error":
            return self.settings.sync_send_errors
        return False

    async def dispatch(self, event: SyncEvent) -> list[DeliveryResult]:
        if not self.settings.sync_enable:
            return []
        if not self.should_send(event.event_type):
            return []
        results = []
        for adapter in self.adapters:
            results.append(await adapter.send(event))
        return results
