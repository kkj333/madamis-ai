"""FastAPI ルート定義。"""

import asyncio
import logging

from fastapi import APIRouter, HTTPException

from madamis.config import DEFAULT_WEB_USER_ID
from madamis.interface import MadamisSupportProvider
from madamis.schemas import ChatRequest, ChatResponse, InterpretRequest

logger = logging.getLogger(__name__)


def create_router(provider: MadamisSupportProvider) -> APIRouter:
    router = APIRouter()

    @router.post("/api/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """Web フロントエンド用チャット（マダミス相談）"""
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="内容を入力してください")

        web_user_id = (request.user_id or "").strip() or DEFAULT_WEB_USER_ID
        try:
            reply_text = await provider.interpret(request.text, web_user_id)
            return ChatResponse(reply=reply_text)
        except Exception as e:
            logger.exception("POST /api/chat failed")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/api/interpret", response_model=ChatResponse)
    async def interpret_api(request: InterpretRequest):
        """外部インターフェース用（Discord 等）マダミス相談エンドポイント"""
        if not request.text.strip() or not request.user_id.strip():
            raise HTTPException(
                status_code=400, detail="無効なリクエストパラメータです"
            )

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                reply_text = await provider.interpret(request.text, request.user_id)
                return ChatResponse(reply=reply_text)
            except Exception as e:
                is_last_attempt = attempt == max_attempts - 1
                if _is_transient_model_overload(e) and not is_last_attempt:
                    logger.warning(
                        "POST /api/interpret transient error, retrying: %s", e
                    )
                    await asyncio.sleep(1.2 * (attempt + 1))
                    continue

                if _is_transient_model_overload(e):
                    logger.warning(
                        "POST /api/interpret overloaded after retries: %s", e
                    )
                    raise HTTPException(
                        status_code=429,
                        detail="現在AIが混み合っています。少し時間をおいて再度お試しください。",
                    )
                logger.exception("POST /api/interpret failed")
                raise HTTPException(status_code=500, detail=str(e))

    @router.get("/health")
    async def health():
        return {"status": "ok"}

    return router


def _is_transient_model_overload(error: Exception) -> bool:
    message = str(error)
    return (
        "503 UNAVAILABLE" in message
        or "'status': 'UNAVAILABLE'" in message
        or "429 RESOURCE_EXHAUSTED" in message
        or "'status': 'RESOURCE_EXHAUSTED'" in message
    )
