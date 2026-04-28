"""Google ADK 実行基盤の組み立て。"""

import os

from google.adk.integrations.firestore.firestore_session_service import (
    FirestoreSessionService,
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import firestore

from madamis.agent import root_agent
from madamis.config import APP_NAME
from madamis.interface import LocalAdkProvider


def build_session_service():
    backend = os.getenv("ADK_SESSION_SERVICE", "in_memory").lower()
    if backend == "firestore":
        client = firestore.AsyncClient(
            project=os.getenv("FIRESTORE_PROJECT_ID") or None,
            database=os.getenv("FIRESTORE_DATABASE_ID") or None,
        )
        return FirestoreSessionService(
            client=client,
            root_collection=(
                os.getenv("ADK_FIRESTORE_ROOT_COLLECTION")
                or os.getenv("FIRESTORE_COLLECTION")
                or None
            ),
        )
    if backend != "in_memory":
        raise ValueError(
            "ADK_SESSION_SERVICE must be either 'in_memory' or 'firestore'."
        )
    return InMemorySessionService()


def create_local_provider() -> LocalAdkProvider:
    session_service = build_session_service()
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    return LocalAdkProvider(
        runner=runner,
        session_service=session_service,
        app_name=APP_NAME,
    )
