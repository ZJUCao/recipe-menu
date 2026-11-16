"""Flow 3, plan the week: v0.1-S13 to v0.1-S16."""

from pathlib import Path

from support import (
    World,
    cells,
    change,
    check_result,
    file_bytes,
    on_one_day,
    put,
    read,
    snapshot,
)
from texts_files import MENU_47_FILE
from texts_plan import (
    MENU_MISTAKE,
    MENU_NEW_EN,
    MENU_NEW_EXISTS_ZH,
    MENU_SHOW_EN,
    MENU_SHOW_ZH,
    NEW_MENU_FILE,
    NO_MENU,
    NOT_A_WEEK,
    SHOP_EMPTY,
    SHOP_NO_MENU,
)
from texts_start import CHECK_FIXED

EM_DASH = "\u2014"


def test_v0_1_s13_plan_a_week_and_show_it(world: World) -> None:
    """v0.1-S13: `menu new` writes the empty menu and keeps it, and `menu show` shows it."""
    world.copy_example()
    world.clear_menus()
    menu = world.data / "menus" / "2026-W47.toml"
    check_result(world, world.run("menu", "new", "2026-W47"), 0, MENU_NEW_EN)
    assert menu.read_bytes() == file_bytes(NEW_MENU_FILE)
    before = snapshot(world.data / "menus")
    check_result(world, world.run("menu", "new", "2026-W47", "--lang", "zh"), 1, MENU_NEW_EXISTS_ZH)
    assert snapshot(world.data / "menus").files == before.files
    put(menu, MENU_47_FILE)
    check_result(world, world.run("check"), 0, CHECK_FIXED, report=True)
    check_result(world, world.run("menu", "show", "2026-W47"), 0, MENU_SHOW_EN)
    check_result(world, world.run("menu", "show", "2026-W47", "--lang", "zh"), 0, MENU_SHOW_ZH)


def steps_of_s14(world: World, this_week: str, next_week: str) -> None:
    """Runs the steps of v0.1-S14 for the weeks ``<T>`` and ``<N>``."""
    world.copy_example()
    world.clear_menus()
    for argument, week in ((None, this_week), ("next", next_week)):
        args = ["menu", "new", *([argument] if argument else [])]
        result = world.run(*args)
        assert (result.code, result.err) == (0, ""), result
        path = world.data / "menus" / f"{week}.toml"
        assert path.is_file(), result
        lines = read(path).split("\n")
        assert f'week = "{week}"' in lines
    shown = world.run("menu", "show", "this")
    assert (shown.code, shown.err) == (0, ""), shown
    lines = shown.out.split("\n")
    assert lines[0].startswith(f"Menu for {this_week},")
    rows = lines[3:10]
    assert [cells(row)[1:] for row in rows] == [[EM_DASH, EM_DASH]] * 7
    assert not any(name in shown.out for name in ("Tomato", "Mapo", "Cola", "rice", "Choy"))
    message = SHOP_EMPTY[0].replace("2026-W46", this_week)
    check_result(world, world.run("shop"), 0, [message])
    check_result(world, world.run("shop", "next"), 0, [message.replace(this_week, next_week)])
    assert list((world.data / "shopping").iterdir()) == []


def test_v0_1_s14_this_and_next_follow_the_pcs_date(tmp_path: Path) -> None:
    """v0.1-S14: `this` and `next` name the weeks of the PC's date and of 7 days later."""
    on_one_day(tmp_path, steps_of_s14)


def test_v0_1_s15_a_missing_menu_a_wrong_week_and_a_menu_with_a_mistake(world: World) -> None:
    """v0.1-S15: missing menus, a wrong week, and an unknown recipe stop `menu show` and `shop`."""
    world.copy_example()
    check_result(world, world.run("menu", "show", "2026-W48"), 1, NO_MENU)
    check_result(world, world.run("menu", "show", "2026-W99"), 2, NOT_A_WEEK)
    check_result(world, world.run("shop", "2026-W48"), 1, SHOP_NO_MENU)
    change(world.data / "menus" / "2026-W47.toml", '"tomato-egg"', '"tomato-eggs"')
    check_result(world, world.run("menu", "show", "2026-W47"), 1, MENU_MISTAKE)
    check_result(world, world.run("shop", "2026-W47"), 1, MENU_MISTAKE)
    assert list((world.data / "shopping").iterdir()) == []


def test_v0_1_s16_the_settings_name_the_meals_and_the_default_servings(world: World) -> None:
    """v0.1-S16: three meals and 3 servings change `menu new`, `menu show`, and `shop`."""
    world.init_folder()
    settings = world.data / "settings.toml"
    change(settings, '["lunch", "dinner"]', '["breakfast", "lunch", "dinner"]')
    change(settings, "servings = 2", "servings = 3")
    new = world.run("menu", "new", "2026-W48")
    assert (new.code, new.err) == (0, "")
    assert new.out.split("\n")[1] == "7 days with breakfast, lunch, and dinner, all empty."
    menu = world.data / "menus" / "2026-W48.toml"
    keys = [line.split(" = ")[0] for line in read(menu).split("\n") if " = " in line]
    meals = [key for key in keys if not key.startswith("#")]
    assert meals[1:] == ["breakfast", "lunch", "dinner"] * 7
    change(menu, "breakfast = []", 'breakfast = ["tomato-egg"]')
    assert_s16_menu_show(world)
    assert_s16_shop(world)


def assert_s16_menu_show(world: World) -> None:
    """Checks `menu show 2026-W48` of v0.1-S16."""
    shown = world.run("menu", "show", "2026-W48")
    assert (shown.code, shown.err) == (0, "")
    lines = shown.out.split("\n")
    assert cells(lines[2]) == ["Day", "Breakfast", "Lunch", "Dinner"]
    monday = next(line for line in lines if line.startswith("Mon 23 Nov"))
    assert cells(monday)[:2] == ["Mon 23 Nov", "Tomato and egg stir-fry \u00d73"]
    assert lines[-3:] == ["", "1 meal, 1 dish. \u00d7n: servings.", ""]


def assert_s16_shop(world: World) -> None:
    """Checks `shop 2026-W48` of v0.1-S16."""
    shopped = world.run("shop", "2026-W48")
    assert (shopped.code, shopped.err) == (0, "")
    lines = shopped.out.split("\n")
    assert lines[0].startswith("Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish")
    produce = lines.index("Vegetables and fruit")
    assert [cells(line) for line in lines[produce + 1 : produce + 3]] == [
        ["Tomato", "450 g"],
        ["Scallion", "2 stalks"],
    ]
    eggs = lines.index("Eggs, dairy, and tofu")
    assert eggs == produce + 3
    assert cells(lines[eggs + 1]) == ["Egg", "5 pieces"]
    pantry = "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar"
    assert pantry in lines
