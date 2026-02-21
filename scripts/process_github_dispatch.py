from __future__ import annotations

import json
import os
import sys
from datetime import datetime

import httpx

from backend.app.core.config import get_settings
from backend.app.models.schemas import CaptureRequest, MediaType, SourceType, TransportMode
from backend.app.services.media import fetch_remote_payload
from backend.app.services.pipeline import PipelineService


async def _download_release_asset(owner: str, repo: str, asset_id: int, token: str, timeout_seconds: int) -> bytes:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/octet-stream",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{asset_id}"
    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
    if resp.status_code >= 400:
        raise RuntimeError(f"failed to download release asset {asset_id}: {resp.status_code} {resp.text}")
    return resp.content


async def _delete_release_asset(owner: str, repo: str, asset_id: int, token: str, timeout_seconds: int) -> None:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{asset_id}"
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        resp = await client.delete(url, headers=headers)
    if resp.status_code not in (204, 404):
        raise RuntimeError(f"failed to delete release asset {asset_id}: {resp.status_code} {resp.text}")


def _parse_owner_repo() -> tuple[str, str]:
    repo_full = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo_full:
        raise RuntimeError("GITHUB_REPOSITORY is missing")
    owner, repo = repo_full.split("/", 1)
    return owner, repo


async def _resolve_payload_bytes(payload: dict, timeout_seconds: int) -> tuple[bytes, TransportMode, str, int | None]:
    asset_id_raw = payload.get("asset_id")
    payload_ref = payload.get("payload_ref", "")

    if asset_id_raw not in (None, ""):
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            raise RuntimeError("GITHUB_TOKEN is missing for release asset download")
        owner, repo = _parse_owner_repo()
        asset_id = int(str(asset_id_raw))
        data = await _download_release_asset(owner, repo, asset_id, token, timeout_seconds)
        return data, TransportMode.GITHUB_RELEASE_ASSET, f"release_asset:{asset_id}", asset_id

    if payload_ref:
        data = await fetch_remote_payload(payload_ref, timeout_seconds)
        return data, TransportMode.REMOTE_URL, payload_ref, None

    raise RuntimeError("missing both asset_id and payload_ref")


async def _main(event_path: str) -> int:
    settings = get_settings()
    data = json.loads(open(event_path, "r", encoding="utf-8").read())

    payload = data.get("client_payload") or data.get("inputs") or {}
    print(f"DEBUG payload keys: {list(payload.keys())}")
    print(f"DEBUG asset_id raw: {repr(payload.get('asset_id'))}")
    media_type = MediaType(payload.get("media_type", "screenshot"))
    mime_type = payload.get("mime_type", "image/png")
    locale = payload.get("locale", settings.output_locale)
    timezone = payload.get("timezone", settings.default_timezone)

    content, mode, payload_ref, asset_id = await _resolve_payload_bytes(payload, settings.provider_timeout_seconds)

    request = CaptureRequest(
        source=SourceType.GITHUB_ACTION,
        media_type=media_type,
        transport_mode=mode,
        mime_type=mime_type,
        payload_ref=payload_ref,
        payload_bytes=content,
        locale=locale,
        timezone=timezone,
        captured_at=datetime.now().astimezone(),
        metadata=payload,
    )

    result = await PipelineService(settings).process_capture(request)
    print(result.model_dump_json(indent=2, ensure_ascii=False))

    if asset_id is not None and settings.github_release_delete_after_process:
        token = os.environ.get("GITHUB_TOKEN", "")
        if token:
            owner, repo = _parse_owner_repo()
            try:
                await _delete_release_asset(owner, repo, asset_id, token, settings.provider_timeout_seconds)
            except Exception as exc:  # noqa: BLE001
                print(f"warn: failed to delete asset {asset_id}: {exc}")

    return 0 if result.status == "success" else 1


if __name__ == "__main__":
    import asyncio

    if len(sys.argv) < 2:
        print("Usage: python scripts/process_github_dispatch.py <event_path>")
        raise SystemExit(2)

    raise SystemExit(asyncio.run(_main(sys.argv[1])))
