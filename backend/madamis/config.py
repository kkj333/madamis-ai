"""アプリ全体で使う設定値と環境読み込み。"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

APP_NAME = "madamis_ai"
DEFAULT_WEB_USER_ID = "web_default_user"
DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"


def load_environment() -> None:
    backend_root = Path(__file__).resolve().parent.parent
    load_dotenv(backend_root / ".env")
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")


def get_gemini_model() -> str:
    """Model id passed to ADK Agent (overridable via GEMINI_MODEL)."""
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
    return model or DEFAULT_GEMINI_MODEL


def llm_config_errors() -> list[str]:
    """Return human-readable config problems for Vertex AI (ADC)."""
    errors: list[str] = []
    if not os.getenv("GOOGLE_CLOUD_PROJECT", "").strip():
        errors.append("GOOGLE_CLOUD_PROJECT is required")
    if not os.getenv("GOOGLE_CLOUD_LOCATION", "").strip():
        errors.append("GOOGLE_CLOUD_LOCATION is required")
    return errors


def ensure_llm_config() -> None:
    """Fail fast before invoking Gemini when env is incomplete."""
    errors = llm_config_errors()
    if errors:
        raise RuntimeError("; ".join(errors))
