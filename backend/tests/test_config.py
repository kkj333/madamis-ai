from madamis.config import DEFAULT_GEMINI_MODEL, get_gemini_model, llm_config_errors


def test_get_gemini_model_defaults(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert get_gemini_model() == DEFAULT_GEMINI_MODEL


def test_get_gemini_model_override(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    assert get_gemini_model() == "gemini-2.5-flash"


def test_llm_config_errors_for_missing_project(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "asia-northeast1")

    errors = llm_config_errors()
    assert any("GOOGLE_CLOUD_PROJECT" in error for error in errors)


def test_llm_config_errors_for_missing_location(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "demo-project")
    monkeypatch.delenv("GOOGLE_CLOUD_LOCATION", raising=False)

    errors = llm_config_errors()
    assert any("GOOGLE_CLOUD_LOCATION" in error for error in errors)


def test_llm_config_ok_for_vertex(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "demo-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "asia-northeast1")

    assert llm_config_errors() == []
