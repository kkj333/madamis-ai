import os

import pytest

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "asia-northeast1")


@pytest.fixture(autouse=True)
def _default_vertex_env_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep Vertex env stable when individual tests mutate os.environ."""
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "asia-northeast1")
