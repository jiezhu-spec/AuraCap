from __future__ import annotations

from abc import ABC, abstractmethod

from backend.app.models.schemas import DeliveryResult, SyncEvent


class SyncAdapter(ABC):
    channel: str

    @abstractmethod
    async def send(self, event: SyncEvent) -> DeliveryResult:
        raise NotImplementedError
