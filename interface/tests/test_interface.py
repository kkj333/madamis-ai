import pytest
import respx
import httpx
# src/yume_uranai_interface/interface.py から AdkApiProvider をインポート
from yume_uranai_interface.interface import AdkApiProvider

@pytest.mark.asyncio
async def test_interpret_success():
    """正常なレスポンスを返す場合のテスト"""
    api_url = "http://test-backend:8000"
    provider = AdkApiProvider(api_base_url=api_url)
    
    # httpx.post をモックする
    with respx.mock:
        respx.post(f"{api_url}/api/interpret").mock(
            return_value=httpx.Response(200, json={"reply": "テストの結果です。"})
        )
        
        reply = await provider.interpret("夢を見た", "user123")
        assert reply == "テストの結果です。"

@pytest.mark.asyncio
async def test_interpret_api_error():
    """APIサーバーがエラーを返す場合のテスト"""
    api_url = "http://test-backend:8000"
    provider = AdkApiProvider(api_base_url=api_url)
    
    with respx.mock:
        respx.post(f"{api_url}/api/interpret").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        
        reply = await provider.interpret("夢を見た", "user123")
        assert reply == "APIサーバーエラーが発生しました。"

@pytest.mark.asyncio
async def test_interpret_network_error():
    """通信エラーが発生した場合のテスト"""
    api_url = "http://test-backend:8000"
    provider = AdkApiProvider(api_base_url=api_url)
    
    with respx.mock:
        respx.post(f"{api_url}/api/interpret").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )
        
        reply = await provider.interpret("夢を見た", "user123")
        assert reply == "夢見師へ繋ぐネットワークに問題が発生しました。"
