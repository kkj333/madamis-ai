#!/usr/bin/env python3
"""Run live repro cases for tools + Pydantic on ADK.

Prints which scenarios error vs succeed. Not all failures reproduce on
Vertex + gemini-3-flash (native response_schema path).

  uv run python scripts/adk_tools_pydantic_error_repro.py
"""

from __future__ import annotations

import asyncio
import sys
from unittest.mock import patch

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.tools.set_model_response_tool import SetModelResponseTool
from google.genai import types

from madamis.core.config import ensure_llm_config, get_gemini_model, load_environment
from madamis.models.recipe import Recipe
from madamis.tools.dice import roll_dice

PROMPT = "2d6振って。クッキーレシピ: 2 cups flour, bake 375F."


def repro_dict_schema_declaration_error() -> None:
    print("\n=== [offline] SetModelResponseTool(dict schema) ===")
    schema = {"type": "object", "properties": {"result": {"type": "string"}}}
    try:
        SetModelResponseTool(schema)._get_declaration()
        print("unexpected OK")
    except Exception as exc:
        print(f"ERROR (expected): {type(exc).__name__}: {exc}")


async def _run_agent(label: str, agent: Agent, *, force_fallback: bool = False) -> None:
    print(f"\n=== [live] {label} ===")
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent, app_name="tools-pydantic-repro", session_service=session_service
    )
    session = await session_service.create_session(
        app_name="tools-pydantic-repro", user_id="repro-user"
    )
    message = types.Content(role="user", parts=[types.Part(text=PROMPT)])

    patches = []
    if force_fallback:
        p_basic = patch(
            "google.adk.flows.llm_flows.basic.can_use_output_schema_with_tools",
            return_value=False,
        )
        p_proc = patch(
            "google.adk.flows.llm_flows._output_schema_processor.can_use_output_schema_with_tools",
            return_value=False,
        )
        patches = [p_basic, p_proc]

    try:
        if patches:
            with patches[0], patches[1]:
                await _consume(runner, session, message)
        else:
            await _consume(runner, session, message)
        print("OK")
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {str(exc)[:800]}")


async def _consume(runner: Runner, session, message: types.Content) -> None:
    async for event in runner.run_async(
        user_id="repro-user",
        session_id=session.id,
        new_message=message,
    ):
        if event.error_code:
            raise RuntimeError(
                f"{event.error_code} {getattr(event, 'error_message', '')}"
            )


async def run_live_cases() -> None:
    model = get_gemini_model()
    base = dict(
        name="repro",
        model=model,
        instruction="Use roll_dice and structured Recipe output.",
    )

    await _run_agent(
        f"tools=[roll_dice] + output_schema=Recipe (native path, model={model})",
        Agent(tools=[roll_dice], output_schema=Recipe, **base),
    )
    await _run_agent(
        f"same agent but SetModelResponseTool fallback forced (model={model})",
        Agent(tools=[roll_dice], output_schema=Recipe, **base),
        force_fallback=True,
    )
    await _run_agent(
        "tools=[roll_dice, SetModelResponseTool(Recipe)] only",
        Agent(tools=[roll_dice, SetModelResponseTool(Recipe)], **base),
    )


def main() -> int:
    load_environment()
    try:
        ensure_llm_config()
    except RuntimeError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    repro_dict_schema_declaration_error()
    asyncio.run(run_live_cases())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
