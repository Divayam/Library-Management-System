"""
Database client helpers.

Instantiates a single Supabase client that can be reused across the backend.
"""

from __future__ import annotations

from typing import Optional

from supabase import Client, create_client

from .config import SUPABASE_KEY, SUPABASE_URL, validate_supabase_config

_client: Optional[Client] = None


def get_client() -> Client:
    """Return a singleton Supabase client."""
    global _client

    if _client is None:
        validate_supabase_config()
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)

    return _client

