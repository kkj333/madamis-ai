#!/usr/bin/env python3
"""Repro: google.genai + JSON schema constraint, then Pydantic parse (Vertex ADC).

Gemini returns JSON text (schema-constrained). The API does not return a
Pydantic model — the app calls ``Recipe.model_validate_json`` explicitly.

Google's newer docs show ``response_format``; google-genai 1.73 uses
``response_mime_type`` + ``response_json_schema`` instead.

Run from backend/:
  uv run python scripts/genai_pydantic_repro.py
"""

from __future__ import annotations

import os
import sys

from google import genai
from google.genai import types

from madamis.core.config import ensure_llm_config, get_gemini_model, load_environment
from madamis.models.recipe import Recipe

PROMPT = """
Please extract the recipe from the following text.
The user wants to make delicious chocolate chip cookies.
They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
For the best part, they'll need 2 cups of semisweet chocolate chips.
First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
onto ungreased baking sheets and bake for 9 to 11 minutes.
"""


def build_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
    )


def extract_recipe(client: genai.Client, *, model: str | None = None) -> Recipe:
    response = client.models.generate_content(
        model=model or get_gemini_model(),
        contents=PROMPT,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=Recipe.model_json_schema(),
        ),
    )
    if not response.text:
        raise RuntimeError("Empty model response")
    # JSON string from Gemini → Pydantic instance on the app side.
    return Recipe.model_validate_json(response.text)


def main() -> int:
    load_environment()
    try:
        ensure_llm_config()
    except RuntimeError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    recipe = extract_recipe(build_client())
    print(recipe.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
