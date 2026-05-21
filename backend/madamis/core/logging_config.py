"""アプリ共通の logging 初期化（uvicorn 子プロセスでも一度だけ有効）"""

import logging
import os


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        force=True,
    )
