"""ADK structured output + tools edge cases (offline; no live Gemini)."""

from __future__ import annotations

import pytest
from google.adk.agents import Agent
from google.adk.tools.set_model_response_tool import SetModelResponseTool
from google.adk.utils.output_schema_utils import can_use_output_schema_with_tools

from madamis.agent import root_agent as madamis_agent
from madamis.config import get_gemini_model
from madamis.schemas import Recipe


def test_madamis_agent_has_tools_only():
    assert madamis_agent.output_schema is None
    assert madamis_agent.tools


def test_vertex_gemini3_uses_native_output_schema_with_tools(monkeypatch):
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
    agent = Agent(
        model=get_gemini_model(),
        name="schema_probe",
        output_schema=Recipe,
    )
    assert can_use_output_schema_with_tools(agent.canonical_model) is True


def test_set_model_response_tool_dict_schema_fails_declaration():
    """Known ADK bug repro: raw dict schema breaks tool declaration."""
    schema = {"type": "object", "properties": {"result": {"type": "string"}}}
    tool = SetModelResponseTool(schema)
    with pytest.raises(Exception, match="Unknown schema type|SchemaError"):
        tool._get_declaration()


def test_set_model_response_tool_recipe_declaration_has_nested_fields():
    tool = SetModelResponseTool(Recipe)
    declaration = tool._get_declaration()
    assert declaration is not None
    assert "ingredients" in declaration.parameters_json_schema["properties"]
