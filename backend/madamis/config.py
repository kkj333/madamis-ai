"""アプリ全体で使う設定値と環境読み込み。"""

from pathlib import Path

from dotenv import load_dotenv

APP_NAME = "madamis_ai"
DEFAULT_WEB_USER_ID = "web_default_user"


def load_environment() -> None:
    backend_root = Path(__file__).resolve().parent.parent
    load_dotenv(backend_root / ".env")
