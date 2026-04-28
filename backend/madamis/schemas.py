"""API リクエスト / レスポンスモデル。"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    text: str
    user_id: str | None = None


class ChatResponse(BaseModel):
    reply: str


class InterpretRequest(BaseModel):
    text: str
    user_id: str
