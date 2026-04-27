from fastapi.testclient import TestClient
from yume_uranai.main import app

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

def test_interpret_invalid_request():
    """不正なリクエストパラメータを送信した場合のテスト"""
    response = client.post("/api/interpret", json={"text": "", "user_id": ""})
    assert response.status_code == 400
