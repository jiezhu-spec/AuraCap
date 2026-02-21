from __future__ import annotations

import logging
from datetime import datetime

from backend.app.core.config import Settings
from backend.app.core.i18n import t
from backend.app.models.schemas import AudioMode, CaptureRequest, ProcessResult, SyncEvent
from backend.app.providers.base import ProviderError
from backend.app.providers.factory import ProviderBundle
from backend.app.services.common import load_prompt
from backend.app.services.custom_operation import run_custom_operation
from backend.app.services.sync_queue import enqueue as sync_enqueue
from backend.app.services.timeline import append_timeline

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.providers = ProviderBundle(settings)

    async def _extract_content(self, request: CaptureRequest) -> str:
        timeline_prompt = load_prompt(
            self.settings.timeline_prompt_file,
            "Extract concise structured facts, actions, and context from the input.",
        )
        if request.media_type.value == "screenshot":
            return await self.providers.mm.analyze_multimodal(
                prompt=timeline_prompt,
                mime_type=request.mime_type,
                payload=request.payload_bytes,
            )

        audio_mode = AudioMode(self.settings.audio_mode)
        if audio_mode == AudioMode.TRANSCRIBE_THEN_ANALYZE:
            transcript = await self.providers.asr.transcribe_audio(request.mime_type, request.payload_bytes)
            return await self.providers.text.analyze_text(prompt=timeline_prompt, text=transcript)

        return await self.providers.mm.analyze_multimodal(
            prompt=timeline_prompt,
            mime_type=request.mime_type,
            payload=request.payload_bytes,
        )

    async def process_capture(self, request: CaptureRequest) -> ProcessResult:
        request_id = datetime.now().astimezone().strftime("%Y%m%d%H%M%S%f")
        try:
            extracted = await self._extract_content(request)
            entry = append_timeline(
                settings=self.settings,
                source=request.source,
                input_type=request.media_type,
                extracted_content=extracted,
                locale=request.locale,
                timezone=request.timezone,
                metadata=request.metadata,
                trace={
                    "transport_mode": request.transport_mode,
                    "mime_type": request.mime_type,
                    "payload_ref": request.payload_ref,
                    "request_id": request_id,
                },
                timestamp=request.captured_at,
            )

            customized_path = None
            if self.settings.enable_custom_operation and self.settings.custom_operation_mode == "ON_EACH_TRIGGER":
                customized_path = await run_custom_operation(
                    settings=self.settings,
                    provider=self.providers.text,
                    input_text=extracted,
                    suffix=entry.id,
                )

            sync_results = await sync_enqueue(
                self.settings,
                SyncEvent(
                    event_type="timeline",
                    title=f"{t('timeline_title', self.settings.output_locale)} {entry.timestamp_display}",
                    body=entry.extracted_content,
                    artifact_path=str(self.settings.timeline_file),
                ),
            )

            return ProcessResult(
                request_id=request_id,
                timeline_path=str(self.settings.timeline_file),
                extracted_content=extracted,
                customized_path=customized_path,
                sync_results=sync_results,
                status="success",
            )
        except ProviderError as exc:
            logger.error("provider_error", extra={"extra": {"code": exc.code, "detail": str(exc)}})
            print(f"PROVIDER_ERROR: code={exc.code} detail={exc}")
            return ProcessResult(
                request_id=request_id,
                timeline_path=str(self.settings.timeline_file),
                extracted_content="",
                status="failed",
                error_code=exc.code,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("process_capture_failed")
            return ProcessResult(
                request_id=request_id,
                timeline_path=str(self.settings.timeline_file),
                extracted_content="",
                status="failed",
                error_code=str(exc),
            )
