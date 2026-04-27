from __future__ import annotations

import hashlib
import hmac
import json
import logging
from urllib.parse import parse_qsl

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings

log = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


class TelegramAuthRequest(BaseModel):
    init_data: str


class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None


class TelegramAuthResponse(BaseModel):
    valid: bool
    user: TelegramUser | None = None


def _validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """
    Validate Telegram WebApp initData using HMAC-SHA256.
    Returns parsed user dict if valid, None otherwise.
    """
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    provided_hash = params.pop("hash", None)
    if not provided_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
    ).digest()
    expected_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, provided_hash):
        return None

    user_str = params.get("user", "{}")
    try:
        return json.loads(user_str)
    except json.JSONDecodeError:
        return None


@router.post("/telegram", response_model=TelegramAuthResponse)
def validate_telegram(body: TelegramAuthRequest) -> TelegramAuthResponse:
    token = settings.miniapp_bot_token
    if not token:
        raise HTTPException(
            status_code=503,
            detail="Telegram Mini App token not configured",
        )

    user_data = _validate_init_data(body.init_data, token)
    if user_data is None:
        return TelegramAuthResponse(valid=False)

    try:
        user = TelegramUser(**user_data)
    except Exception:
        log.warning("Failed to parse Telegram user from initData")
        return TelegramAuthResponse(valid=False)

    return TelegramAuthResponse(valid=True, user=user)
