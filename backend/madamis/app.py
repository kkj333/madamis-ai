"""FastAPI アプリケーション生成。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from madamis.interface import MadamisSupportProvider
from madamis.routes import create_router


def create_app(provider: MadamisSupportProvider) -> FastAPI:
    app = FastAPI(title="マダミスサポート AI API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(create_router(provider))
    return app
