import logging
from abc import ABC, abstractmethod

import httpx

logger = logging.getLogger(__name__)


class MadamisSupportProvider(ABC):
    """マダミスサポートの応答を取得するための抽象インターフェース"""

    @abstractmethod
    async def interpret(self, text: str, user_id: str) -> str:
        pass


class AdkApiProvider(MadamisSupportProvider):
    """Cloud Run 上などの API エンドポイントを叩いて結果を取得する実装（Bot 本番用）"""

    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url.rstrip("/")

    async def interpret(self, text: str, user_id: str) -> str:
        url = f"{self.api_base_url}/api/interpret"
        payload = {
            "text": text,
            "user_id": user_id,
        }

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("reply", "応答が空でした。")
        except httpx.TimeoutException as e:
            logger.warning("API Timeout: %s", e)
            return "応答に時間がかかりすぎています。少し待ってからもう一度試してください。"
        except httpx.HTTPStatusError as e:
            logger.warning(
                "API HTTP Error: %s %s", e.response.status_code, e.response.text[:500]
            )
            if e.response.status_code in (429, 503):
                return "サーバーが混み合っています。少し待ってからもう一度試してください。"
            return "API サーバーエラーが発生しました。"
        except httpx.RequestError as e:
            logger.warning("API Request Error: %s", e)
            return "バックエンドへの接続に問題が発生しました。"
