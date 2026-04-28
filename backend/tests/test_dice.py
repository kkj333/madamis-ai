from madamis import dice


def test_roll_dice_with_count_and_sides(monkeypatch):
    rolls = iter([3, 5])
    monkeypatch.setattr(dice.random, "randint", lambda _start, _end: next(rolls))

    result = dice.roll_dice(count=2, sides=6)

    assert result == {
        "ok": True,
        "expression": "2d6",
        "rolls": [3, 5],
        "total": 8,
    }


def test_roll_dice_defaults_to_one_die(monkeypatch):
    monkeypatch.setattr(dice.random, "randint", lambda _start, _end: 17)

    result = dice.roll_dice(sides=20)

    assert result == {
        "ok": True,
        "expression": "1d20",
        "rolls": [17],
        "total": 17,
    }


def test_roll_dice_defaults_to_six_sides(monkeypatch):
    rolls = iter([2, 6])
    monkeypatch.setattr(dice.random, "randint", lambda _start, _end: next(rolls))

    result = dice.roll_dice(count=2)

    assert result == {
        "ok": True,
        "expression": "2d6",
        "rolls": [2, 6],
        "total": 8,
    }


def test_roll_dice_accepts_agent_extracted_sides_and_count(monkeypatch):
    rolls = iter([7, 3, 10])
    monkeypatch.setattr(dice.random, "randint", lambda _start, _end: next(rolls))

    result = dice.roll_dice(count=3, sides=10)

    assert result == {
        "ok": True,
        "expression": "3d10",
        "rolls": [7, 3, 10],
        "total": 20,
    }


def test_roll_dice_accepts_agent_extracted_kanji_number(monkeypatch):
    monkeypatch.setattr(dice.random, "randint", lambda _start, _end: 42)

    result = dice.roll_dice(sides=100)

    assert result == {
        "ok": True,
        "expression": "1d100",
        "rolls": [42],
        "total": 42,
    }


def test_roll_dice_rejects_invalid_count():
    result = dice.roll_dice(count=0, sides=6)

    assert result["ok"] is False
    assert "1個以上" in result["error"]


def test_roll_dice_rejects_too_many_dice():
    result = dice.roll_dice(count=101, sides=6)

    assert result["ok"] is False
    assert "最大100個" in result["error"]


def test_roll_dice_rejects_too_few_sides():
    result = dice.roll_dice(count=1, sides=1)

    assert result["ok"] is False
    assert "2以上" in result["error"]
