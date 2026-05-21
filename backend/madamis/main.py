"""マダミスサポート AI バックエンド - FastAPI エントリポイント"""

from madamis.api.app import create_app
from madamis.core.config import load_environment
from madamis.core.logging_config import configure_logging
from madamis.runtime.adk import create_local_provider

load_environment()
configure_logging()
app = create_app(create_local_provider())
