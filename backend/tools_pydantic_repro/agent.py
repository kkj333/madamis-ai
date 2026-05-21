"""Repro: ``tools`` + nested Pydantic ``output_schema`` on the same ADK agent.

This mirrors ``roll_dice`` + ``Recipe`` — the pattern that routes through
``SetModelResponseTool`` when native ``response_schema`` + tools is unavailable.

On Vertex + ``gemini-3-flash-preview``, ADK usually takes the native path and
may *not* error. See ``docs/tools-pydantic-repro.md`` for how to hit the
fallback path or the deterministic declaration bug.
"""

from google.adk.agents import Agent

from madamis.core.config import get_gemini_model, load_environment
from madamis.models.recipe import Recipe
from madamis.tools.dice import roll_dice

load_environment()

REPRO_INSTRUCTION = """
サイコロの依頼があれば ``roll_dice`` tool を使う。
レシピ抽出や構造化回答が必要なときは output_schema（Recipe）に従う。
"""

root_agent = Agent(
    model=get_gemini_model(),
    name="tools_pydantic_repro_agent",
    description="tools + nested Pydantic output_schema の ADK 再現用",
    instruction=REPRO_INSTRUCTION,
    tools=[roll_dice],
    output_schema=Recipe,
)
