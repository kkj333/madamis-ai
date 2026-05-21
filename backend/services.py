"""ADK Web service registrations for local debugging."""

import os
from urllib.parse import urlparse

from google.adk.cli.service_registry import get_service_registry
from google.adk.integrations.firestore.firestore_session_service import (
    FirestoreSessionService,
)
from google.cloud import firestore


def _firestore_session_factory(uri: str, **_kwargs):
    parsed = urlparse(uri)
    root_collection = (
        parsed.netloc
        or parsed.path.lstrip("/")
        or os.getenv("ADK_FIRESTORE_ROOT_COLLECTION")
        or None
    )
    client = firestore.AsyncClient(
        project=os.getenv("FIRESTORE_PROJECT_ID") or None,
        database=os.getenv("FIRESTORE_DATABASE_ID") or None,
    )
    return FirestoreSessionService(client=client, root_collection=root_collection)


get_service_registry().register_session_service(
    "firestore", _firestore_session_factory
)
