"""Tests of F13 for SHOP_COMMAND, its run, the week argument, and the help (T01, T02)."""

import io
from datetime import date
from pathlib import Path

import pytest

from f05_support import make_home
from f05_texts import HELP_EN, HELP_ZH, lines_text
from f06_support import MEALS_DINNER, m_unknown_meal
from f07_support import call
from f07_texts import Prob, p_slot
from f09_support import new_context, run_command
from f09_texts import E_NO_CATALOG, EN, out, stop
from f11_texts import not_a_week, not_a_week_zh
from f13_blocks import block_a
from f13_support import old_list, shop_faults
from f13_texts import FILE_47, PROTOTYPE_FILE, shop_47, shop_47_zh
from recipe_menu.app import Argument, Arguments, Context, FolderUse, UsageError
from recipe_menu.commands.shop import SHOP_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message

BAD_WEEKS = [
    "2026-W99",
    "Next",
    "THIS",
    "",
    " 2026-W47",
    "2026-W47\n",
    "2026-w47",
    "2026-W7",
    "2025-W53",
    "2026-W00",
    "this week",
    "\uff12\uff10\uff12\uff16-W47",
]
GOOD_WEEKS = [(), ("this",), ("next",), ("2026-W47",), ("2026-W53",), ("0001-W01",)]


def _check_fields() -> None:
    """Checks the fields of ``SHOP_COMMAND``."""
    assert SHOP_COMMAND.words == ("shop",)
    assert SHOP_COMMAND.usage == BiText("shop [WEEK]", "shop [周]")
    assert SHOP_COMMAND.help_line.render(Lang.EN) == "Make the shopping list of a week menu."
    assert SHOP_COMMAND.help_line.render(Lang.ZH) == "生成一个周菜单的购物清单。"
    assert SHOP_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
    assert SHOP_COMMAND.options == ()
    assert SHOP_COMMAND.folder is FolderUse.READ


def _check_example(example: DataFolder, home: Path) -> None:
    """Runs the example of 2.1, then the call that raises and the two helps, and checks them."""
    stdout, stderr = io.StringIO(), io.StringIO()
    context = Context(Lang.EN, example, Settings(), stdout, stderr, date(2026, 11, 10))
    assert SHOP_COMMAND.run(context, Arguments(("next",))) == 0
    file = example.shopping_file("2026-W47")
    assert stdout.getvalue() == lines_text(*shop_47(file))
    assert stderr.getvalue() == ""
    text = file.read_bytes().decode("utf-8")
    assert text.split("\n")[:7] == [
        "# Shopping list for 2026-W47",
        "",
        "16 to 22 November 2026: 4 meals, 9 dishes.",
        "",
        "## Vegetables and fruit",
        "",
        "- [ ] Tomato 600 g",
    ]
    pantry = "Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper"
    assert text.endswith(
        f"- [ ] Cola 2 cans\n\nNot on the list, because they are in the pantry: {pantry}\n"
    )
    assert "\r" not in text
    assert [path.name for path in example.shopping.iterdir()] == ["2026-W47.md"]
    assert file.read_bytes() == FILE_47
    assert call(home, ["--help"]) == (0, HELP_EN, "")
    assert call(home, ["--help", "--lang", "zh"]) == (0, HELP_ZH, "")
    context, stdout, stderr = new_context(Lang.EN, example)
    with pytest.raises(UsageError):
        SHOP_COMMAND.run(context, Arguments(("2026-W99",)))
    assert (stdout.getvalue(), stderr.getvalue()) == ("", "")
    assert [path.name for path in example.shopping.iterdir()] == ["2026-W47.md"]
    assert file.read_bytes() == FILE_47


def test_f13_t01_the_shop_command_takes_its_week_and_settings_and_the_help_lists_it(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.1, then the runs of inputs 1 to 5 and the whole help."""
    home = make_home(tmp_path)
    example = example_folder
    _check_fields()
    _check_example(example, home)
    file = example.shopping_file("2026-W47")
    every = Settings(Lang.ZH, tuple(Meal), 3)
    result = run_command(
        SHOP_COMMAND, Lang.EN, example, Arguments(("2026-W47",)), every, today=date(2030, 1, 1)
    )
    assert result == out(block_a(file))
    assert file.read_bytes().startswith(b"# Shopping list for 2026-W47\n")
    assert b"- [ ] Tomato 900 g\n" in file.read_bytes()
    lunch_dinner = Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2)
    result = run_command(
        SHOP_COMMAND, Lang.ZH, example, Arguments(()), lunch_dinner, today=date(2026, 11, 17)
    )
    assert result == out(shop_47_zh(file))
    assert file.read_bytes() == PROTOTYPE_FILE
    dinner = Settings(Lang.EN, (Meal.DINNER,), 5)
    saturday = Prob(
        "menus/2026-W47.toml", p_slot("saturday", "lunch"), m_unknown_meal("lunch", MEALS_DINNER)
    )
    result = run_command(
        SHOP_COMMAND, Lang.EN, example, Arguments(()), dinner, today=date(2026, 11, 17)
    )
    assert result == stop(saturday)
    assert file.read_bytes() == PROTOTYPE_FILE
    for _ in range(2):
        result = run_command(SHOP_COMMAND, Lang.EN, example, Arguments(("next",)))
        assert result == out(shop_47(file))
        assert file.read_bytes() == FILE_47


def _check_wrong_week(folder: DataFolder, value: str) -> None:
    """Runs ``shop`` with a value that is not a week, and checks the error and the streams."""
    context, stdout, stderr = new_context(EN, folder)
    with pytest.raises(UsageError) as caught:
        SHOP_COMMAND.run(context, Arguments((value,)))
    assert (stdout.getvalue(), stderr.getvalue()) == ("", "")
    raised = caught.value
    assert raised.text(EN) == not_a_week(value)
    assert raised.text(Lang.ZH) == not_a_week_zh(value)
    assert (raised.hint, raised.values) == (None, (("week", value),))


def test_f13_t02_a_value_that_is_not_a_week_raises_before_the_disk_is_touched(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Step 1: twelve wrong values raise ``UsageError``, and six good ones pass."""
    folder = DataFolder(tmp_path / "missing")
    with shop_faults(tmp_path) as state:
        for value in BAD_WEEKS:
            _check_wrong_week(folder, value)
        assert (state.calls, state.listings) == ([], [])
        for values in GOOD_WEEKS:
            result = run_command(SHOP_COMMAND, EN, folder, Arguments(values))
            assert result == stop(E_NO_CATALOG), values
    assert not (tmp_path / "missing").exists()
    old_list(example_folder.root)
    with shop_faults(example_folder.root) as state:
        for value in BAD_WEEKS:
            _check_wrong_week(example_folder, value)
        assert (state.calls, state.listings) == ([], [])
    assert example_folder.shopping_file("2026-W47").read_bytes() == b"old\n"
