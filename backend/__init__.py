"""
Backend package for the Library Management System.

This module exposes helper functions to make it easier for the Streamlit
frontend to import backend utilities without worrying about package paths.
"""

from . import services  # noqa: F401

__all__ = ["services"]

