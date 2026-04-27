"""夢占いAI バックエンド - FastAPI (推論層)"""

# 自動チェックフックの動作確認用コメント
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from yume_uranai.agent import root_agent
from yume_uranai.interface import LocalAdkProvider

load_dotenv()

# --- 基盤設定 (推論層) ---
APP_NAME = "yume_uranai"
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# API全体で共通利用するローカルプロバイダー
local_provider = LocalAdkProvider(
    runner=runner,
    session_service=session_service,
    app_name=APP_NAME
)

# --- FastAPI 本体 ---
# Discord Bot部分は分離されたため、lifespanなし
app = FastAPI(title="夢占いAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    reply: str

class InterpretRequest(BaseModel):
    text: str
    user_id: str


def _is_transient_model_overload(error: Exception) -> bool:
    message = str(error)
    return (
        "503 UNAVAILABLE" in message
        or "'status': 'UNAVAILABLE'" in message
        or "429 RESOURCE_EXHAUSTED" in message
        or "'status': 'RESOURCE_EXHAUSTED'" in message
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Webフロントエンド用チャットエンドポイント"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="内容を入力してください")

    web_user_id = "web_default_user"
    try:
        reply_text = await local_provider.interpret(request.text, web_user_id)
        return ChatResponse(reply=reply_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interpret", response_model=ChatResponse)
async def interpret_api(request: InterpretRequest):
    """(推論層)外部インターフェース用 夢占いエンドポイント"""
    if not request.text.strip() or not request.user_id.strip():
        raise HTTPException(status_code=400, detail="無効なリクエストパラメータです")

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            reply_text = await local_provider.interpret(request.text, request.user_id)
            return ChatResponse(reply=reply_text)
        except Exception as e:
            is_last_attempt = attempt == max_attempts - 1
            if _is_transient_model_overload(e) and not is_last_attempt:
                await asyncio.sleep(1.2 * (attempt + 1))
                continue

            if _is_transient_model_overload(e):
                raise HTTPException(
                    status_code=429,
                    detail="現在AIが混み合っています。少し時間をおいて再度お試しください。",
                )
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {
        "status": "ok"
    }
