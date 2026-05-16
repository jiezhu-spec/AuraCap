from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import httpx

from backend.app.core.config import Settings, get_settings
from backend.app.models.schemas import CaptureRequest, MediaType, SourceType, TransportMode
from backend.app.services.media import validate_media_payload
from backend.app.services.pipeline import PipelineService


class ResolvedPayload(NamedTuple):
    content: bytes
    mode: TransportMode
    payload_ref: str
    asset_id: int | None


def _github_headers(token: str, accept: str = "application/vnd.github+json") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _max_upload_bytes(settings: Settings) -> int:
    return settings.max_upload_mb * 1024 * 1024


async def _read_limited_response(response: httpx.Response, max_bytes: int, label: str) -> bytes:
    content_length = response.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > max_bytes:
                raise RuntimeError(f"PAYLOAD_TOO_LARGE: {label}")
        except ValueError as exc:
            raise RuntimeError(f"invalid content-length for {label}: {content_length}") from exc

    chunks: list[bytes] = []
    total = 0
    async for chunk in response.aiter_bytes():
        if not chunk:
            continue
        total += len(chunk)
        if total > max_bytes:
            raise RuntimeError(f"PAYLOAD_TOO_LARGE: {label}")
        chunks.append(chunk)
    return b"".join(chunks)


async def _download_release_asset(
    owner: str,
    repo: str,
    asset_id: int,
    token: str,
    timeout_seconds: int,
    max_bytes: int,
    client: httpx.AsyncClient | None = None,
) -> bytes:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{asset_id}"

    async def _download(active_client: httpx.AsyncClient) -> bytes:
        async with active_client.stream(
            "GET",
            url,
            headers=_github_headers(token, "application/octet-stream"),
            follow_redirects=True,
        ) as response:
            if response.status_code >= 400:
                body = (await response.aread()).decode("utf-8", errors="replace")
                raise RuntimeError(f"failed to download release asset {asset_id}: {response.status_code} {body}")
            return await _read_limited_response(response, max_bytes, f"release_asset:{asset_id}")

    if client is not None:
        return await _download(client)

    async with httpx.AsyncClient(timeout=timeout_seconds) as active_client:
        return await _download(active_client)


async def _delete_release_asset(owner: str, repo: str, asset_id: int, token: str, timeout_seconds: int) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{asset_id}"
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        resp = await client.delete(url, headers=_github_headers(token))
    if resp.status_code not in (204, 404):
        raise RuntimeError(f"failed to delete release asset {asset_id}: {resp.status_code} {resp.text}")


async def _delete_verified_release_asset(
    settings: Settings,
    owner: str,
    repo: str,
    asset_id: int,
    token: str,
) -> None:
    if not settings.github_release_delete_after_process:
        return
    try:
        await _delete_release_asset(owner, repo, asset_id, token, settings.provider_timeout_seconds)
    except Exception as exc:  # noqa: BLE001
        print(f"warn: failed to delete asset {asset_id}: {exc}")


def _parse_owner_repo() -> tuple[str, str]:
    repo_full = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo_full:
        raise RuntimeError("GITHUB_REPOSITORY is missing")
    owner, repo = repo_full.split("/", 1)
    return owner, repo


def _parse_asset_id(raw: object) -> int | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError as exc:
        raise RuntimeError(f"invalid asset_id: {raw}") from exc


async def _find_inbox_asset(
    owner: str,
    repo: str,
    asset_id: int,
    token: str,
    release_tag: str,
    timeout_seconds: int,
    client: httpx.AsyncClient | None = None,
) -> dict:
    async def _find(active_client: httpx.AsyncClient) -> dict:
        release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{release_tag}"
        release_resp = await active_client.get(release_url, headers=_github_headers(token))
        if release_resp.status_code == 404:
            raise RuntimeError(f"inbox release not found: {release_tag}")
        if release_resp.status_code >= 400:
            raise RuntimeError(f"failed to fetch inbox release {release_tag}: {release_resp.status_code} {release_resp.text}")

        release = release_resp.json()
        release_id = release.get("id")
        if release_id is None:
            raise RuntimeError(f"inbox release {release_tag} is missing id")

        page = 1
        while True:
            assets_url = f"https://api.github.com/repos/{owner}/{repo}/releases/{release_id}/assets"
            assets_resp = await active_client.get(
                assets_url,
                headers=_github_headers(token),
                params={"per_page": 100, "page": page},
            )
            if assets_resp.status_code >= 400:
                raise RuntimeError(f"failed to list inbox assets: {assets_resp.status_code} {assets_resp.text}")
            assets = assets_resp.json()
            if not isinstance(assets, list):
                raise RuntimeError("failed to list inbox assets: unexpected response")
            for asset in assets:
                try:
                    current_id = int(asset.get("id"))
                except (TypeError, ValueError):
                    continue
                if current_id == asset_id:
                    return asset
            if len(assets) < 100:
                break
            page += 1

        raise RuntimeError(f"release asset {asset_id} is not in inbox release {release_tag}")

    if client is not None:
        return await _find(client)

    async with httpx.AsyncClient(timeout=timeout_seconds) as active_client:
        return await _find(active_client)


def _assert_github_asset_size(asset: dict, max_bytes: int, asset_id: int) -> None:
    size = asset.get("size")
    if size is None:
        return
    try:
        size_i = int(size)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"invalid size metadata for release asset {asset_id}: {size}") from exc
    if size_i > max_bytes:
        raise RuntimeError(f"PAYLOAD_TOO_LARGE: release_asset:{asset_id}")


async def _resolve_release_asset_payload(asset_id: int, settings: Settings, token: str) -> ResolvedPayload:
    owner, repo = _parse_owner_repo()
    max_bytes = _max_upload_bytes(settings)
    verified_inbox_asset = False
    try:
        asset = await _find_inbox_asset(
            owner,
            repo,
            asset_id,
            token,
            settings.github_release_inbox_tag,
            settings.provider_timeout_seconds,
        )
        verified_inbox_asset = True
        _assert_github_asset_size(asset, max_bytes, asset_id)
        data = await _download_release_asset(
            owner,
            repo,
            asset_id,
            token,
            settings.provider_timeout_seconds,
            max_bytes,
        )
    except Exception as exc:
        if verified_inbox_asset and str(exc).startswith("PAYLOAD_TOO_LARGE"):
            await _delete_verified_release_asset(settings, owner, repo, asset_id, token)
        raise
    return ResolvedPayload(data, TransportMode.GITHUB_RELEASE_ASSET, f"release_asset:{asset_id}", asset_id)


async def _resolve_payload_bytes(payload: dict, settings: Settings) -> ResolvedPayload:
    asset_id = _parse_asset_id(payload.get("asset_id"))
    payload_ref = str(payload.get("payload_ref") or "").strip()

    if asset_id is not None:
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            raise RuntimeError("GITHUB_TOKEN is missing for release asset download")
        return await _resolve_release_asset_payload(asset_id, settings, token)

    if payload_ref:
        raise RuntimeError("payload_ref is no longer supported; use asset_id")

    raise RuntimeError("missing both asset_id and payload_ref")


def _load_event_payload(event_path: str) -> dict:
    data = json.loads(Path(event_path).read_text(encoding="utf-8"))
    return data.get("client_payload") or data.get("inputs") or {}


async def _main(event_path: str) -> int:
    settings = get_settings()
    payload = _load_event_payload(event_path)

    print(f"DEBUG payload keys: {list(payload.keys())}")
    print(f"DEBUG asset_id raw: {repr(payload.get('asset_id'))}")
    media_type = MediaType(payload.get("media_type", "screenshot"))
    mime_type = payload.get("mime_type", "image/png")
    locale = payload.get("locale", settings.output_locale)
    timezone = payload.get("timezone", settings.default_timezone)

    resolved: ResolvedPayload | None = None
    delete_asset = False
    try:
        resolved = await _resolve_payload_bytes(payload, settings)
        try:
            validate_media_payload(media_type, mime_type, resolved.content, settings)
        except ValueError:
            delete_asset = True
            raise

        request = CaptureRequest(
            source=SourceType.GITHUB_ACTION,
            media_type=media_type,
            transport_mode=resolved.mode,
            mime_type=mime_type,
            payload_ref=resolved.payload_ref,
            payload_bytes=resolved.content,
            locale=locale,
            timezone=timezone,
            captured_at=datetime.now().astimezone(),
            metadata=payload,
        )

        result = await PipelineService(settings).process_capture(request)
        delete_asset = result.status == "success"
        print(result.model_dump_json(indent=2, ensure_ascii=False))
        return 0 if result.status == "success" else 1
    finally:
        if delete_asset and resolved is not None and resolved.asset_id is not None:
            token = os.environ.get("GITHUB_TOKEN", "")
            if token:
                owner, repo = _parse_owner_repo()
                await _delete_verified_release_asset(settings, owner, repo, resolved.asset_id, token)


if __name__ == "__main__":
    import asyncio

    if len(sys.argv) < 2:
        print("Usage: python scripts/process_github_dispatch.py <event_path>")
        raise SystemExit(2)

    raise SystemExit(asyncio.run(_main(sys.argv[1])))
