"""Dice rolling tool for madamis support."""

import random

MAX_DICE_COUNT = 100
MAX_DICE_SIDES = 1000


def _validate_dice(count: int, sides: int) -> str | None:
    if count < 1:
        return "サイコロの個数は1個以上にしてください。"
    if sides < 2:
        return "サイコロの面数は2以上にしてください。"
    if count > MAX_DICE_COUNT:
        return f"サイコロの個数は最大{MAX_DICE_COUNT}個までです。"
    if sides > MAX_DICE_SIDES:
        return f"サイコロの面数は最大{MAX_DICE_SIDES}面までです。"
    return None


def roll_dice(count: int = 1, sides: int = 6) -> dict[str, object]:
    """Roll dice with structured values extracted by the agent.

    Args:
        count: Number of dice to roll. Defaults to 1.
        sides: Number of sides on each die. Defaults to 6.

    Returns:
        A dictionary with normalized dice expression, individual rolls, and
        total. If the values are invalid, returns an error message instead of
        rolling.
    """
    error = _validate_dice(count, sides)
    if error:
        return {
            "ok": False,
            "error": error,
        }

    rolls = [random.randint(1, sides) for _ in range(count)]
    return {
        "ok": True,
        "expression": f"{count}d{sides}",
        "rolls": rolls,
        "total": sum(rolls),
    }
