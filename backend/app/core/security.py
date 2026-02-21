from __future__ import annotations

import hashlib
import hmac

from fastapi import Header, HTTPException

from backend.app.core.config import Settings


def verify_signature(settings: Settings, raw_body: bytes, signature: str | None) -> None:
    if settings.skip_signature_verification:
        return
    if not settings.request_signature_secret:
        raise HTTPException(status_code=500, detail="request_signature_secret is empty")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    expected = hmac.new(
        settings.request_signature_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


def signature_header(x_auracap_signature: str | None = Header(default=None)) -> str | None:
    return x_auracap_signature
