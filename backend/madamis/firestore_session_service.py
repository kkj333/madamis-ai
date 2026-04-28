"""Firestore-backed ADK session service."""

from __future__ import annotations

import asyncio
import base64
import copy
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from uuid import uuid4

from google.adk.errors.already_exists_error import AlreadyExistsError
from google.adk.events.event import Event
from google.adk.platform import time as platform_time
from google.adk.sessions import _session_util
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.base_session_service import GetSessionConfig
from google.adk.sessions.base_session_service import ListSessionsResponse
from google.adk.sessions.session import Session
from google.adk.sessions.state import State
from google.cloud.firestore_v1 import AsyncClient
from google.cloud.firestore_v1 import AsyncDocumentReference
from google.cloud.firestore_v1 import FieldFilter
from google.cloud.firestore_v1 import Query
from typing_extensions import override


def _document_id(*parts: str) -> str:
    raw = "\x1f".join(parts).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _merge_state(
    app_state: dict[str, Any],
    user_state: dict[str, Any],
    session_state: dict[str, Any],
) -> dict[str, Any]:
    merged_state = copy.deepcopy(session_state)
    for key, value in app_state.items():
        merged_state[State.APP_PREFIX + key] = value
    for key, value in user_state.items():
        merged_state[State.USER_PREFIX + key] = value
    return merged_state


class FirestoreSessionService(BaseSessionService):
    """Stores ADK sessions under one Firestore root collection.

    Layout:
      {collection}/{app_doc}/users/{user_doc}/sessions/{session_doc}/events/{event_doc}
    """

    def __init__(
        self,
        *,
        project: str | None = None,
        database: str | None = None,
        collection: str = "adk_sessions",
    ) -> None:
        self.client = AsyncClient(project=project, database=database)
        self.collection = collection
        self._session_locks: dict[tuple[str, str, str], asyncio.Lock] = {}
        self._session_locks_guard = asyncio.Lock()

    def _app_ref(self, app_name: str) -> AsyncDocumentReference:
        return self.client.collection(self.collection).document(_document_id(app_name))

    def _user_ref(self, app_name: str, user_id: str) -> AsyncDocumentReference:
        return (
            self._app_ref(app_name)
            .collection("users")
            .document(_document_id(app_name, user_id))
        )

    def _session_ref(
        self, app_name: str, user_id: str, session_id: str
    ) -> AsyncDocumentReference:
        return (
            self._user_ref(app_name, user_id)
            .collection("sessions")
            .document(_document_id(app_name, user_id, session_id))
        )

    @asynccontextmanager
    async def _with_session_lock(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> AsyncIterator[None]:
        lock_key = (app_name, user_id, session_id)
        async with self._session_locks_guard:
            lock = self._session_locks.setdefault(lock_key, asyncio.Lock())
        async with lock:
            yield

    async def _load_state(
        self, app_name: str, user_id: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        app_snapshot, user_snapshot = await asyncio.gather(
            self._app_ref(app_name).get(),
            self._user_ref(app_name, user_id).get(),
        )
        app_state = (app_snapshot.to_dict() or {}).get("state", {})
        user_state = (user_snapshot.to_dict() or {}).get("state", {})
        return app_state, user_state

    def _session_from_data(
        self,
        data: dict[str, Any],
        *,
        state: dict[str, Any] | None = None,
        events: list[Event] | None = None,
    ) -> Session:
        return Session(
            id=data["id"],
            app_name=data["app_name"],
            user_id=data["user_id"],
            state=state if state is not None else data.get("state", {}),
            events=events or [],
            last_update_time=data.get("last_update_time", 0.0),
        )

    @override
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> Session:
        session_id = (
            session_id.strip() if session_id and session_id.strip() else uuid4().hex
        )
        session_ref = self._session_ref(app_name, user_id, session_id)
        if (await session_ref.get()).exists:
            raise AlreadyExistsError(f"Session with id {session_id} already exists.")

        state_deltas = _session_util.extract_state_delta(state or {})
        app_state_delta = state_deltas["app"]
        user_state_delta = state_deltas["user"]
        session_state = state_deltas["session"] or {}
        app_ref = self._app_ref(app_name)
        user_ref = self._user_ref(app_name, user_id)
        app_state, user_state = await self._load_state(app_name, user_id)
        app_state = app_state | app_state_delta
        user_state = user_state | user_state_delta

        now = platform_time.get_time()
        batch = self.client.batch()
        batch.set(
            app_ref,
            {
                "app_name": app_name,
                "state": app_state,
                "last_update_time": now,
            },
            merge=True,
        )
        batch.set(
            user_ref,
            {
                "app_name": app_name,
                "user_id": user_id,
                "state": user_state,
                "last_update_time": now,
            },
            merge=True,
        )
        batch.create(
            session_ref,
            {
                "id": session_id,
                "app_name": app_name,
                "user_id": user_id,
                "state": session_state,
                "create_time": now,
                "last_update_time": now,
            },
        )
        await batch.commit()

        return Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=_merge_state(app_state, user_state, session_state),
            last_update_time=now,
        )

    @override
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: GetSessionConfig | None = None,
    ) -> Session | None:
        session_snapshot = await self._session_ref(app_name, user_id, session_id).get()
        if not session_snapshot.exists:
            return None

        session_data = session_snapshot.to_dict() or {}
        app_state, user_state = await self._load_state(app_name, user_id)
        merged_state = _merge_state(
            app_state, user_state, session_data.get("state", {})
        )

        events: list[Event] = []
        if not config or config.num_recent_events != 0:
            event_query = session_snapshot.reference.collection("events")
            if config and config.after_timestamp:
                event_query = event_query.where(
                    filter=FieldFilter("timestamp", ">=", config.after_timestamp)
                )
            event_query = event_query.order_by("timestamp", direction=Query.DESCENDING)
            if config and config.num_recent_events:
                event_query = event_query.limit(config.num_recent_events)

            event_snapshots = [snapshot async for snapshot in event_query.stream()]
            events = [
                Event.model_validate((snapshot.to_dict() or {})["event"])
                for snapshot in reversed(event_snapshots)
            ]

        return self._session_from_data(session_data, state=merged_state, events=events)

    @override
    async def list_sessions(
        self, *, app_name: str, user_id: str | None = None
    ) -> ListSessionsResponse:
        user_refs = []
        if user_id is not None:
            user_refs.append(self._user_ref(app_name, user_id))
        else:
            user_refs = [
                snapshot.reference
                async for snapshot in self._app_ref(app_name)
                .collection("users")
                .stream()
            ]

        app_snapshot = await self._app_ref(app_name).get()
        app_state = (app_snapshot.to_dict() or {}).get("state", {})
        sessions: list[Session] = []
        for user_ref in user_refs:
            user_snapshot = await user_ref.get()
            user_data = user_snapshot.to_dict() or {}
            current_user_state = user_data.get("state", {})
            session_snapshots = [
                snapshot async for snapshot in user_ref.collection("sessions").stream()
            ]
            for session_snapshot in session_snapshots:
                session_data = session_snapshot.to_dict() or {}
                merged_state = _merge_state(
                    app_state,
                    current_user_state,
                    session_data.get("state", {}),
                )
                sessions.append(
                    self._session_from_data(session_data, state=merged_state)
                )

        sessions.sort(key=lambda session: session.last_update_time, reverse=True)
        return ListSessionsResponse(sessions=sessions)

    @override
    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        session_ref = self._session_ref(app_name, user_id, session_id)
        event_refs = [
            snapshot.reference
            async for snapshot in session_ref.collection("events").stream()
        ]
        batch = self.client.batch()
        for event_ref in event_refs:
            batch.delete(event_ref)
        batch.delete(session_ref)
        await batch.commit()

    @override
    async def append_event(self, session: Session, event: Event) -> Event:
        if event.partial:
            return event

        self._apply_temp_state(session, event)
        event = self._trim_temp_delta_state(event)
        state_delta = (
            event.actions.state_delta
            if event.actions and event.actions.state_delta
            else {}
        )
        state_deltas = _session_util.extract_state_delta(state_delta)

        async with self._with_session_lock(
            app_name=session.app_name,
            user_id=session.user_id,
            session_id=session.id,
        ):
            session_ref = self._session_ref(
                session.app_name, session.user_id, session.id
            )
            session_snapshot = await session_ref.get()
            if not session_snapshot.exists:
                raise ValueError(f"Session {session.id} not found.")

            app_state, user_state = await self._load_state(
                session.app_name, session.user_id
            )
            session_data = session_snapshot.to_dict() or {}
            session_state = session_data.get("state", {})

            app_state = app_state | state_deltas["app"]
            user_state = user_state | state_deltas["user"]
            session_state = session_state | state_deltas["session"]

            batch = self.client.batch()
            batch.set(
                self._app_ref(session.app_name),
                {"state": app_state, "last_update_time": event.timestamp},
                merge=True,
            )
            batch.set(
                self._user_ref(session.app_name, session.user_id),
                {"state": user_state, "last_update_time": event.timestamp},
                merge=True,
            )
            batch.set(
                session_ref,
                {
                    "state": session_state,
                    "last_update_time": event.timestamp,
                },
                merge=True,
            )
            batch.set(
                session_ref.collection("events").document(_document_id(event.id)),
                {
                    "id": event.id,
                    "timestamp": event.timestamp,
                    "event": event.model_dump(
                        mode="json", by_alias=False, exclude_none=True
                    ),
                },
            )
            await batch.commit()

        await super().append_event(session=session, event=event)
        return event
