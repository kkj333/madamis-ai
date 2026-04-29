import asyncio
from types import SimpleNamespace

from madamis.interface import LocalAdkProvider, _session_id_for_user


class FakeSessionService:
    def __init__(self):
        self.sessions = {}
        self.create_calls = []

    async def get_session(self, app_name: str, user_id: str, session_id: str):
        return self.sessions.get((app_name, user_id, session_id))

    async def create_session(self, app_name: str, user_id: str, session_id: str):
        self.create_calls.append((app_name, user_id, session_id))
        session = SimpleNamespace(id=session_id)
        self.sessions[(app_name, user_id, session_id)] = session
        return session


def test_user_session_id_is_stable_for_same_user():
    session_service = FakeSessionService()
    provider = LocalAdkProvider(
        runner=None,
        session_service=session_service,
        app_name="test_app",
    )

    first = asyncio.run(provider._get_or_create_user_session("user-1"))
    second = asyncio.run(provider._get_or_create_user_session("user-1"))

    assert first.id == _session_id_for_user("user-1")
    assert second.id == first.id
    assert session_service.create_calls == [
        ("test_app", "user-1", _session_id_for_user("user-1"))
    ]
