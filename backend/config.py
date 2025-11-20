"""
Application configuration helpers.

Environment variables are loaded via python-dotenv so the backend can be used
both locally and in deployment environments where the variables are already
present.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()


def validate_supabase_config() -> None:
    """Ensure Supabase credentials are present."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Supabase credentials are missing. Set SUPABASE_URL and "
            "SUPABASE_KEY in your environment or .env file."
        )

