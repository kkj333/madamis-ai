"""Repro tests: tools + Pydantic structured output failure modes."""

from __future__ import annotations

import pytest
from google.adk.tools.set_model_response_tool import SetModelResponseTool
from google.adk.utils.output_schema_utils import can_use_output_schema_with_tools

from madamis.agent import root_agent as madamis_agent
from madamis.schemas import Recipe
from tools_pydantic_repro.agent import root_agent as repro_agent


def test_madamis_agent_is_tools_only_control():
    assert repro_agent.output_schema is Recipe
    assert madamis_agent.output_schema is None
    assert madamis_agent.tools


def test_repro_agent_combines_roll_dice_and_recipe_schema():
    assert repro_agent.tools
    assert repro_agent.output_schema is Recipe


def test_vertex_gemini3_uses_native_output_schema_with_tools(monkeypatch):
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
    assert can_use_output_schema_with_tools(repro_agent.canonical_model) is True


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
