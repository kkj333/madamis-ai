"""Unit tests for genai + Pydantic structured output schema (no live Gemini call)."""

from __future__ import annotations

import json

from madamis.models.recipe import Ingredient, Recipe


def test_recipe_model_json_schema_has_nested_ingredients():
    schema = Recipe.model_json_schema()
    assert "ingredients" in schema["properties"]
    assert schema["properties"]["ingredients"]["type"] == "array"


def test_recipe_model_validate_json_roundtrip():
    payload = {
        "recipe_name": "Chocolate Chip Cookies",
        "prep_time_minutes": 30,
        "ingredients": [
            {"name": "flour", "quantity": "2 1/4 cups"},
        ],
        "instructions": ["Preheat oven to 375°F."],
    }
    recipe = Recipe.model_validate_json(json.dumps(payload))
    assert recipe.recipe_name == "Chocolate Chip Cookies"
    assert isinstance(recipe.ingredients[0], Ingredient)
