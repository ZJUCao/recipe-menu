"""Flow 4, shop: v0.1-S17 and v0.1-S18."""

from support import World, cells, change, check_result, file_bytes, put, read
from texts_plan import SHOP_EN, SHOP_FILE_ZH, SHOP_MIXED, SHOP_ZH


def test_v0_1_s17_make_the_weeks_shopping_list_in_english_and_in_chinese(world: World) -> None:
    """v0.1-S17: `shop` prints and saves the list, and a second run replaces the file."""
    world.copy_example()
    saved = world.data / "shopping" / "2026-W47.md"
    check_result(world, world.run("shop", "2026-W47"), 0, SHOP_EN)
    items = [cells(line) for line in SHOP_EN if line.startswith("  ")]
    file_lines = read(saved).split("\n")
    assert len(items) == 14
    assert [line for line in file_lines if line.startswith("- [ ]")] == [
        f"- [ ] {name} {amount}" for name, amount in items
    ]
    assert len([line for line in file_lines if line.startswith("- ")]) == 14
    check_result(world, world.run("shop", "2026-W47", "--lang", "zh"), 0, SHOP_ZH)
    assert saved.read_bytes() == file_bytes(SHOP_FILE_ZH)
    assert [path.name for path in (world.data / "shopping").iterdir()] == ["2026-W47.md"]


def scallion_noodles() -> list[str]:
    """Gives the lines of the recipe file `scallion-noodles` of v0.1-S18."""
    return [
        'name = { zh = "葱油拌面", en = "Scallion oil noodles" }',
        "servings = 2",
        'tags = ["快手", "主食"]',
        "",
        "ingredients = [",
        '  { item = "面条", amount = "200 g" },',
        '  { item = "葱", amount = "1 把" },',
        '  { item = "生抽", amount = "10 g" },',
        "]",
        "",
        "[steps]",
        "zh = [",
        '  "面条煮熟捞出\uff0c拌上葱油和生抽\u3002",',
        "]",
        "en = [",
        '  "Cook the noodles, and toss them with the scallion oil and soy sauce.",',
        "]",
    ]


def menu_of_s18() -> list[str]:
    """Gives the lines of the menu file of 2026-W48 of v0.1-S18: dinners from Monday to Friday."""
    dinners = {
        "monday": "red-braised-pork",
        "tuesday": "tomato-egg",
        "wednesday": "tomato-egg",
        "thursday": "tomato-egg-noodles",
        "friday": "scallion-noodles",
    }
    lines = ['week = "2026-W48"']
    for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
        dish = f'"{dinners[day]}"' if day in dinners else ""
        lines += ["", f"[{day}]", "lunch = []", f"dinner = [{dish}]"]
    return lines


def test_v0_1_s18_quantities_that_cannot_be_added_share_one_line(world: World) -> None:
    """v0.1-S18: 5 stalks + 1 bunch, and 30 ml + 10 g, each on one line."""
    world.copy_example()
    change(world.data / "pantry.toml", '"生抽", ', "")
    put(world.data / "recipes" / "scallion-noodles.toml", scallion_noodles())
    put(world.data / "menus" / "2026-W48.toml", menu_of_s18())
    english = world.run("shop", "2026-W48")
    assert (english.code, english.err) == (0, "")
    rows = [cells(line) for line in english.out.split("\n")]
    expected = [cells(line) for line in SHOP_MIXED]
    assert expected == [["Scallion", "5 stalks + 1 bunch"], ["Soy sauce", "30 ml + 10 g"]]
    for row in expected:
        assert rows.count(row) == 1
    chinese = world.run("shop", "2026-W48", "--lang", "zh")
    assert (chinese.code, chinese.err) == (0, "")
    rows = [cells(line) for line in chinese.out.split("\n")]
    assert rows.count(["葱", "5 根 + 1 把"]) == 1
    assert rows.count(["生抽", "30 ml + 10 g"]) == 1
