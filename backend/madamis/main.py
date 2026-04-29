"""マダミスサポート AI バックエンド - FastAPI エントリポイント"""

from madamis.app import create_app
from madamis.config import load_environment
from madamis.logging_config import configure_logging
from madamis.runtime import create_local_provider

load_environment()
configure_logging()
app = create_app(create_local_provider())
