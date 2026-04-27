from abc import ABC, abstractmethod
import httpx

class YumeUranaiProvider(ABC):
    """夢占いの結果を取得するための抽象インターフェース"""
    
    @abstractmethod
    async def interpret(self, text: str, user_id: str) -> str:
        pass

class AdkApiProvider(YumeUranaiProvider):
    """Cloud Run 上などの API エンドポイントを叩いて結果を取得する実装（Bot本番用）"""
    
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url.rstrip("/")
        
    async def interpret(self, text: str, user_id: str) -> str:
        url = f"{self.api_base_url}/api/interpret"
        payload = {
            "text": text,
            "user_id": user_id
        }
        
        try:
            # タイムアウトは長めに設定 (コールドスタート + LLM推論のため180秒)
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("reply", "応答が空でした。")
        except httpx.TimeoutException as e:
            print(f"API Timeout Error: {type(e).__name__} - {str(e)}")
            return "夢見師の解釈に時間がかかりすぎています。少し待ってからもう一度試してください。"
        except httpx.HTTPStatusError as e:
            print(f"API HTTP Error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code in (429, 503):
                return "夢見師が少し混み合っています。少し待ってからもう一度試してください。"
            return "APIサーバーエラーが発生しました。"
        except httpx.RequestError as e:
            print(f"API Request Error: {type(e).__name__} - {str(e)}")
            return "夢見師へ繋ぐネットワークに問題が発生しました。"
