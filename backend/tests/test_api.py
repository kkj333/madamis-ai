from fastapi.testclient import TestClient
from madamis.app import create_app
from madamis.config import DEFAULT_WEB_USER_ID
from madamis.main import app

client = TestClient(app)


def test_health_check():
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_invalid_request():
    """空のテキストを送信した場合のテスト"""
    response = client.post("/api/chat", json={"text": ""})
    assert response.status_code == 400


def test_chat_blank_user_id_uses_default():
    """空白だけの user_id は Web のデフォルトユーザーとして扱う"""

    class FakeProvider:
        def __init__(self):
            self.user_id = None

        async def interpret(self, text: str, user_id: str) -> str:
            self.user_id = user_id
            return text

    provider = FakeProvider()
    test_client = TestClient(create_app(provider))

    response = test_client.post("/api/chat", json={"text": "hello", "user_id": "   "})

    assert response.status_code == 200
    assert response.json() == {"reply": "hello"}
    assert provider.user_id == DEFAULT_WEB_USER_ID


def test_interpret_invalid_request():
    """不正なリクエストパラメータを送信した場合のテスト"""
    response = client.post("/api/interpret", json={"text": "", "user_id": ""})
    assert response.status_code == 400
