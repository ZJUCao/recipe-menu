"""Flow 1, start and check: v0.1-S01 to v0.1-S08."""

from pathlib import Path

from support import World, cells, change, check_result, file_bytes, put, to_bom_crlf
from texts_files import CATALOG_FILE, PANTRY_FILE, SETTINGS_FILE, TOMATO_EGG_FILE
from texts_find import SHOW_EN
from texts_plan import MENU_SHOW_EN, SHOP_EN
from texts_start import (
    CHECK_ERRORS_EN,
    CHECK_ERRORS_ZH,
    CHECK_FIXED,
    CHECK_INIT,
    CHECK_SYNTAX,
    INIT_EN,
    INIT_REFUSED,
    INIT_ZH,
)

COLA = '{ zh = "可乐", en = "Cola", category = "other", unit = "罐" },\n'


def assert_init_folder(root: Path, language: str) -> None:
    """Checks the files and folders that ``init`` creates, byte for byte."""
    settings = [
        line.replace('language = "en"', f'language = "{language}"') for line in SETTINGS_FILE
    ]
    expected = {
        "settings.toml": file_bytes(settings),
        "catalog.toml": file_bytes(CATALOG_FILE),
        "pantry.toml": file_bytes(PANTRY_FILE),
        "recipes\\tomato-egg.toml": file_bytes(TOMATO_EGG_FILE),
    }
    found = {
        str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }
    assert found == expected
    folders = {str(path.relative_to(root)) for path in root.rglob("*") if path.is_dir()}
    assert folders == {"recipes", "menus", "shopping"}


def test_v0_1_s01_start_a_data_folder_in_english_then_check_it(world: World) -> None:
    """v0.1-S01: `init` creates the example folder, and `check` finds nothing wrong."""
    check_result(world, world.run("init"), 0, INIT_EN)
    assert_init_folder(world.data, "en")
    check_result(world, world.run("check"), 0, CHECK_INIT)


def test_v0_1_s02_start_a_data_folder_in_chinese(world: World) -> None:
    """v0.1-S02: `init --lang zh` writes `zh`, and `check` then reports in Chinese."""
    check_result(world, world.run("init", "--lang", "zh"), 0, INIT_ZH)
    assert_init_folder(world.data, "zh")
    result = world.run("check")
    assert result.code == 0
    assert result.err == ""
    lines = result.out.split("\n")
    assert lines[0] == "已检查设置\u3001目录\u3001常备清单\u30011 个菜谱和 0 个周菜单\u3002"
    assert len(lines) == 4
    assert lines[1] == ""
    assert "没有错误" in lines[2]
    assert "没有警告" in lines[2]


def test_v0_1_s03_init_refuses_a_folder_that_holds_files(world: World) -> None:
    """v0.1-S03: `init` changes nothing in a folder with a file, and works in a new folder."""
    notes = world.data / "notes.txt"
    notes.parent.mkdir()
    notes.write_bytes(b"my notes\r\n\xe7\xac\x94\xe8\xae\xb0\n")
    before = (notes.read_bytes(), notes.stat().st_mtime_ns)
    check_result(world, world.run("init"), 1, INIT_REFUSED)
    assert [path.name for path in world.data.iterdir()] == ["notes.txt"]
    assert (notes.read_bytes(), notes.stat().st_mtime_ns) == before
    other = world.root / "other"
    check_result(world, world.run("init", "--data", other), 0, INIT_EN, data=other)
    assert_init_folder(other, "en")


def cucumber_salad() -> list[str]:
    """Gives the lines of the recipe file `cucumber-salad` of v0.1-S04."""
    return [
        'name = { zh = "拍黄瓜", en = "Smashed cucumber" }',
        "servings = 2",
        'tags = ["快手", "素"]',
        "",
        "ingredients = [",
        '  { item = "黄瓜", amount = "2 个" },',
        '  { item = "大蒜", amount = "2 瓣" },',
        "]",
        "",
        "[steps]",
        "zh = [",
        '  "黄瓜拍碎\uff0c加蒜末和盐拌匀\u3002",',
        "]",
        "en = [",
        '  "Smash the cucumbers, and mix them with garlic and salt.",',
        "]",
    ]


def test_v0_1_s04_add_a_recipe_that_needs_a_new_ingredient(world: World) -> None:
    """v0.1-S04: `check` names the unknown ingredient, and the catalog entry fixes it."""
    world.init_folder()
    put(world.data / "recipes" / "cucumber-salad.toml", cucumber_salad())
    first = "Checked the settings, the catalog, the pantry, 2 recipes, and 0 week menus."
    result = world.run("check")
    assert result.code == 1
    assert result.err == ""
    lines = result.out.split("\n")
    assert lines[0] == first
    at = lines.index("1 error:")
    assert lines[at + 1 : at + 3] == [
        "  recipes\\cucumber-salad.toml, ingredient 1",
        '    Unknown ingredient "黄瓜". Add it to the catalog, or use its name in the catalog.',
    ]
    entry = '  { zh = "黄瓜", en = "Cucumber", category = "produce" },\n'
    change(world.data / "catalog.toml", COLA, COLA + entry)
    result = world.run("check")
    assert (result.code, result.err) == (0, "")
    assert result.out.split("\n") == [first, "", "No errors. No warnings.", ""]
    assert_s04_list_and_show(world)


def assert_s04_list_and_show(world: World) -> None:
    """Checks `list` and `show cucumber-salad` after the catalog has the cucumber."""
    listing = world.run("list")
    assert (listing.code, listing.err) == (0, "")
    rows = listing.out.split("\n")
    assert [cells(line)[0] for line in rows[1:3]] == ["cucumber-salad", "tomato-egg"]
    assert rows[-3:] == ["", "2 recipes.", ""]
    shown = world.run("show", "cucumber-salad")
    assert (shown.code, shown.err) == (0, "")
    ingredients = [cells(line) for line in shown.out.split("\n")]
    assert ["Cucumber", "2 pieces"] in ingredients
    assert ["Garlic", "2 cloves"] in ingredients


def test_v0_1_s05_fix_the_mistakes_that_check_reports(world: World) -> None:
    """v0.1-S05: `check` reports two errors and a warning, and passes after the fixes."""
    world.copy_example()
    change(world.data / "recipes" / "mapo-tofu.toml", "郫县豆瓣酱", "豆瓣酱")
    change(world.data / "menus" / "2026-W47.toml", '"tomato-egg"', '"tomato-eggs"')
    check_result(world, world.run("check"), 1, CHECK_ERRORS_EN, report=True)
    check_result(world, world.run("check", "--lang", "zh"), 1, CHECK_ERRORS_ZH, report=True)
    change(world.data / "recipes" / "mapo-tofu.toml", "豆瓣酱", "郫县豆瓣酱")
    change(world.data / "menus" / "2026-W47.toml", '"tomato-eggs"', '"tomato-egg"')
    check_result(world, world.run("check"), 0, CHECK_FIXED)


def test_v0_1_s06_a_syntax_mistake_names_its_line(world: World) -> None:
    """v0.1-S06: a missing comma in `pantry.toml` is reported with its line, and a warning stays."""
    world.copy_example()
    change(world.data / "pantry.toml", '"盐", "糖"', '"盐" "糖"')
    check_result(world, world.run("check"), 1, CHECK_SYNTAX, report=True)


OTHER_PROBLEMS = [
    (
        "catalog.toml, ingredient 23",
        'The English name "Broccoli" is also ingredient 3\'s name. Names must be unique.',
    ),
    (
        "catalog.toml, ingredient 24",
        'Unknown category "meats". The categories are produce, meat, eggs, staples, '
        "seasonings, and other.",
    ),
    ("pantry.toml, item 3", 'Unknown ingredient "sesame oil".'),
    ("recipes\\rice.toml, servings", "Servings must be a whole number of 1 or more, not 0."),
    ("recipes\\rice.toml, ingredient 1", 'Unknown unit "cups" in "1 cups".'),
    ("recipes\\rice.toml, tags", 'Unknown tag "breakfast". Add it to the catalog\'s tags.'),
    (
        "menus\\2026-W47.toml, week",
        "The file name says 2026-W47, but the file says 2026-W48.",
    ),
    (
        "menus\\2026-W47.toml, Friday supper",
        'Unknown meal "supper". The settings name lunch and dinner.',
    ),
    (
        "menus\\2026-W47.toml, Sunday dinner, dish 1",
        "Servings must be a whole number of 1 or more, not 0.",
    ),
]


def make_nine_mistakes(world: World) -> None:
    """Puts the 9 mistakes of v0.1-S07 into the example folder."""
    data = world.data
    added = (
        '  { zh = "芥兰", en = "Broccoli", category = "produce" },\n'
        '  { zh = "香菜", en = "Coriander", category = "meats" },\n'
    )
    change(data / "catalog.toml", COLA, COLA + added)
    change(data / "pantry.toml", '"糖"', '"sesame oil"')
    change(data / "recipes" / "rice.toml", "servings = 2", "servings = 0")
    change(data / "recipes" / "rice.toml", '"160 g"', '"1 cups"')
    change(data / "recipes" / "rice.toml", 'tags = ["主食"]', 'tags = ["breakfast"]')
    menu = data / "menus" / "2026-W47.toml"
    change(menu, 'week = "2026-W47"', 'week = "2026-W48"')
    change(menu, "[friday]\n", "[friday]\nsupper = []\n")
    change(
        menu, '{ recipe = "cola-wings", servings = 4 }', '{ recipe = "cola-wings", servings = 0 }'
    )


def test_v0_1_s07_one_check_run_lists_every_problem(world: World) -> None:
    """v0.1-S07: `check` lists the 9 errors and the warning in one run."""
    world.copy_example()
    make_nine_mistakes(world)
    result = world.run("check")
    assert (result.code, result.err) == (1, "")
    lines = result.out.split("\n")
    assert lines[0] == "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu."
    at = lines.index("9 errors:")
    block = lines[at + 1 : lines.index("", at)]
    assert len(block) == 18
    found = [(block[i].strip(), block[i + 1].strip()) for i in range(0, len(block), 2)]
    assert sorted(found) == sorted(OTHER_PROBLEMS)
    warning = list(CHECK_FIXED[CHECK_FIXED.index("1 warning:") :])
    assert lines[lines.index("1 warning:") :][: len(warning)] == warning
    assert lines[-2] == 'Fix the errors and run "recipe-menu check" again.'


def test_v0_1_s08_a_byte_order_mark_and_crlf_read_the_same(world: World) -> None:
    """v0.1-S08: the example folder saved with a BOM and CRLF works as before."""
    world.copy_example()
    to_bom_crlf(world.data)
    check_result(world, world.run("check"), 0, CHECK_FIXED)
    check_result(world, world.run("show", "tomato-egg"), 0, SHOW_EN)
    check_result(world, world.run("menu", "show", "2026-W47"), 0, MENU_SHOW_EN)
    check_result(world, world.run("shop", "2026-W47"), 0, SHOP_EN)
    saved = (world.data / "shopping" / "2026-W47.md").read_bytes()
    assert not saved.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in saved
    saved.decode("utf-8")
