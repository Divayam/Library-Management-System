"""
Authentication helpers using Supabase Auth (GoTrue).
"""

from __future__ import annotations

from typing import Any, Dict

from .db import get_client


def sign_up(email: str, password: str, **user_metadata: Any) -> Dict[str, Any]:
    client = get_client()
    response = client.auth.sign_up(
        {"email": email, "password": password, "options": {"data": user_metadata}}
    )
    return response.__dict__


def sign_in(email: str, password: str) -> Dict[str, Any]:
    client = get_client()
    response = client.auth.sign_in_with_password({"email": email, "password": password})
    return response.__dict__


def sign_out(access_token: str | None = None) -> None:
    client = get_client()
    client.auth.sign_out(access_token)

