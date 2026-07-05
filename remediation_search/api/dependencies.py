"""API dependency utilities such as auth stubs."""

import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_ENV = "AVI_API_KEY"
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str = Security(_api_key_header)) -> None:
    """
    API-key auth stub for backend protection.

    Behavior:
    - If AVI_API_KEY is not set, auth is bypassed (dev mode).
    - If AVI_API_KEY is set, X-API-Key header is required and must match.
    """
    expected_key = os.getenv(API_KEY_ENV)

    if not expected_key:
        return

    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: invalid or missing API key.",
        )
