"""Utilities Module"""

from .logger import setup_logger
from .helpers import export_to_excel, export_to_json

try:
    # Keep DB utilities optional for app-only deployments (e.g., Streamlit Cloud).
    from .database import DatabaseManager
except Exception:  # pragma: no cover - optional dependency import guard
    DatabaseManager = None

__all__ = [
    "setup_logger",
    "DatabaseManager",
    "export_to_excel",
    "export_to_json"
]
