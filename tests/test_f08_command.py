"""Tests of F08 for INIT_COMMAND and its run, and the output of recipe-menu init in full.

These are T14 to T16.
"""

import io
import os
from collections.abc import Callable
from datetime import date
from pathlib import Path

from f05_support import make_home
from f07_support import call, lines_text
from f08_support import EXAMPLE, faults, items, make_steps, new_tree, record_of, tree
from f08_texts import HELP, HELP_ZH, holds_zh, new, new_zh, out_of
from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.catalog import read_catalog, read_pantry
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.commands.init import INIT_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings, read_settings


def _run(context: Context) -> int:
    """Runs ``INIT_COMMAND`` with no arguments."""
    return INIT_COMMAND.run(context, Arguments())


def _context(
    lang: Lang, root: Path, settings: Settings, today: date
) -> tuple[Context, io.StringIO, io.StringIO]:
    """Makes a context with new streams, and gives it with them."""
    out, err = io.StringIO(), io.StringIO()
    return Context(lang, DataFolder(root), settings, out, err, today), out, err


def _fields() -> None:
    """Checks the fields of ``INIT_COMMAND``."""
    assert INIT_COMMAND.words == ("init",)
    assert INIT_COMMAND.usage == BiText("init", "init")
    assert INIT_COMMAND.help_line.render(Lang.EN) == "Create the data folder with example data."
    assert INIT_COMMAND.help_line.render(Lang.ZH) == "创建数据文件夹和示例数据。"
    assert (INIT_COMMAND.argument, INIT_COMMAND.options) == (None, ())
    assert INIT_COMMAND.folder is FolderUse.CREATE


def _second_column(lines: list[str]) -> int:
    """Gives the index of the second column of the line of ``--lang en|zh``."""
    option = next(line for line in lines if line.startswith("  --lang en|zh"))
    rest = option[len("  --lang en|zh") :]
    return len(option) - len(rest.lstrip(" "))


def _help_with_real_commands(home: Path) -> None:
    """Checks the line of ``init`` in the help, whatever commands F09 to F13 add after check."""
    cases = ((["--help"], Lang.EN, "Commands:"), (["--help", "--lang", "zh"], Lang.ZH, "命令："))
    for argv, lang, heading in cases:
        code, out, err = call(home, argv)
        assert (code, err) == (0, "")
        lines = out.splitlines()
        line, after = lines[lines.index(heading) + 1 :][:2]
        help_line = INIT_COMMAND.help_line.render(lang)
        assert line.startswith("  init ")
        assert line.endswith(help_line)
        assert line[_second_column(lines) :] == help_line
        assert after.startswith("  check ")


def _help_with_two_commands(home: Path) -> None:
    """Checks the whole help with ``INIT_COMMAND`` and ``CHECK_COMMAND`` alone."""
    commands = (INIT_COMMAND, CHECK_COMMAND)
    assert call(home, ["--help"], commands=commands) == out_of(0, HELP)
    assert call(home, ["--help", "--lang", "zh"], commands=commands) == out_of(0, HELP_ZH)
    assert len(HELP) == 15


def _runs_with_other_settings(home: Path) -> None:
    """Runs cases 1 and 2 of F08-T14: the output follows ``context.lang``, not the settings."""
    root = home / "en"
    folders, files = items(root)
    steps = make_steps(root, folders, files)
    context, out, err = _context(Lang.EN, root, Settings(Lang.ZH), date(2030, 1, 1))
    with faults(home) as seen:
        assert _run(context) == 0
    assert (out.getvalue(), err.getvalue()) == (lines_text(new(root)), "")
    assert read_settings(DataFolder(root)) == (Settings(Lang.EN), ())
    assert seen.calls == record_of(home, steps, len(steps), 0)

    root = home / "zh"
    other = Settings(Lang.EN, (Meal.BREAKFAST,), 5)
    context, out, err = _context(Lang.ZH, root, other, date(2026, 11, 10))
    assert _run(context) == 0
    assert (out.getvalue(), err.getvalue()) == (lines_text(new_zh(root)), "")
    assert read_settings(DataFolder(root)) == (Settings(Lang.ZH), ())


def test_f08_t14_the_command_fields_a_run_in_the_context_language_a_refusal_and_the_help(
    tmp_path: Path,
) -> None:
    """The example of 2.1, and the cases of `run` and of the help."""
    home = make_home(tmp_path)
    _fields()
    direct = home / "direct"
    context, out, err = _context(Lang.ZH, direct, Settings(Lang.EN), date(2026, 11, 10))
    assert _run(context) == 0
    assert err.getvalue() == ""
    assert out.getvalue().splitlines()[:1] == [f"已创建数据文件夹 {direct}："]
    assert out.getvalue() == lines_text(new_zh(direct))
    assert read_settings(DataFolder(direct)) == (Settings(Lang.ZH), ())
    _runs_with_other_settings(home)
    context, out, err = _context(Lang.ZH, direct, Settings(Lang.EN), date(2026, 11, 10))
    assert _run(context) == 1
    assert (out.getvalue(), err.getvalue()) == ("", holds_zh(direct) + "\n")
    _help_with_two_commands(home)
    _help_with_real_commands(home)


def _same_text(made: Path, source: Path) -> bool:
    """Tells whether a file holds the bytes of the source text, read as UTF-8 with LF ends."""
    return made.read_bytes() == source.read_text(encoding="utf-8").encode("utf-8")


def _example_first_run(home: Path, run: Callable) -> DataFolder:
    """Runs the first part of the example of 2.2: the new default folder."""
    folder = DataFolder(home / "recipe-menu")
    recipe = str(Path("recipes", "tomato-egg.toml"))
    menus, shopping = "menus" + os.sep, "shopping" + os.sep
    assert run("init") == (
        0,
        [
            f"Created the data folder {folder.root}:",
            "  settings.toml              English, lunch and dinner, 2 servings per dish",
            "  catalog.toml               6 categories, 22 ingredients, 5 tags",
            "  pantry.toml                5 ingredients",
            f"  {recipe}    an example recipe in both languages",
            f"  {menus}                     empty",
            f"  {shopping}                  empty",
            "",
            f'Next: add your recipes to recipes{os.sep}, then run "recipe-menu check".',
        ],
        [],
    )
    names = ["catalog.toml", "menus", "pantry.toml", "recipes", "settings.toml", "shopping"]
    assert sorted(entry.name for entry in folder.root.iterdir()) == names
    assert [entry.name for entry in folder.recipes.iterdir()] == ["tomato-egg.toml"]
    assert list(folder.menus.iterdir()) == list(folder.shopping.iterdir()) == []
    for name in ("settings.toml", "catalog.toml", "pantry.toml"):
        assert _same_text(folder.root / name, EXAMPLE / name)
    assert _same_text(folder.recipe_file("tomato-egg"), EXAMPLE / "recipes" / "tomato-egg.toml")
    assert read_settings(folder) == (Settings(Lang.EN), ())
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert problems == ()
    assert (len(catalog.categories), len(catalog.ingredients), len(catalog.tags)) == (6, 22, 5)
    pantry, problems = read_pantry(folder, catalog)
    assert pantry is not None
    assert problems == ()
    assert len(pantry.ingredients) == 5
    return folder


def _example_check_and_chinese(home: Path, run: Callable, folder: DataFolder) -> None:
    """Runs the check, the refusal, and the data folder in Chinese of the example of 2.2."""
    checked = [
        "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.",
        "",
        "No errors. No warnings.",
    ]
    assert run("check") == (0, checked, [])
    refusal = f"{folder.root} already holds files. init changed nothing."
    assert run("init") == (1, [], [refusal])

    other = home / "zh"
    code, lines, err = run("init", "--lang", "zh", "--data", str(other))
    assert (code, err) == (0, [])
    assert lines[0] == f"已创建数据文件夹 {other}："
    assert lines[1:4] == [
        "  settings.toml              中文，午餐和晚餐，每道菜 2 份",
        "  catalog.toml               6 个分类，22 种食材，5 个标签",
        "  pantry.toml                5 种食材",
    ]
    assert lines[-1] == f"下一步：把你的菜谱加进 recipes{os.sep}，然后运行“recipe-menu check”。"
    english_settings = folder.settings.read_bytes()
    chinese_settings = (other / "settings.toml").read_bytes()
    assert chinese_settings == english_settings.replace(b'language = "en"', b'language = "zh"')
    chinese = ["已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。", "", "没有错误，也没有警告。"]
    assert run("check", "--data", str(other)) == (0, chinese, [])


def _example_refusals(home: Path, run: Callable) -> None:
    """Runs the empty folder, the other refusals, a deep folder, and the extra word."""
    empty = home / "empty"
    empty.mkdir()
    assert run("init", "--data", str(empty))[0] == 0
    only_menus = home / "only-menus"
    (only_menus / "menus").mkdir(parents=True)
    hidden = home / "hidden"
    hidden.mkdir()
    (hidden / ".keep").write_text("", encoding="utf-8")
    for full in (only_menus, hidden):
        refusal = f"{full} already holds files. init changed nothing."
        assert run("init", "--data", str(full)) == (1, [], [refusal])
    assert [entry.name for entry in only_menus.iterdir()] == ["menus"]
    notes = home / "notes.txt"
    notes.write_text("Ideas\n", encoding="utf-8")
    expected = [f"{notes} is a file, not a folder. init changed nothing."]
    assert run("init", "--data", str(notes)) == (1, [], expected)
    deep = home / "a" / "b" / "recipe-menu"
    code, lines, _ = run("init", "--data", str(deep))
    assert (code, lines[0]) == (0, f"Created the data folder {deep}:")
    assert run("init", "extra") == (
        2,
        [],
        [
            'Unexpected argument "extra". Write "recipe-menu init".',
            'Run "recipe-menu --help" to see the commands.',
        ],
    )


def test_f08_t15_the_example_of_2_2_runs_in_order_with_the_real_commands(tmp_path: Path) -> None:
    """The example of 2.2: new, check, refused, Chinese, empty, only menus, hidden, file, deep."""
    home = make_home(tmp_path)

    def run(*argv: str) -> tuple[int, list[str], list[str]]:
        """Runs ``main`` with no ``commands`` and gives the code and the lines of each stream."""
        code, out, err = call(home, argv)
        return code, out.splitlines(), err.splitlines()

    folder = _example_first_run(home, run)
    _example_check_and_chinese(home, run, folder)
    _example_refusals(home, run)


def _check_columns(lines: list[str]) -> None:
    """Checks that each of the six rows has its first cell at index 2 and its second at 29."""
    firsts = [
        "settings.toml",
        "catalog.toml",
        "pantry.toml",
        str(Path("recipes", "tomato-egg.toml")),
        "menus" + os.sep,
        "shopping" + os.sep,
    ]
    for line, first in zip(lines[1:7], firsts, strict=True):
        assert line[:2] == "  "
        assert line.startswith(first, 2)
        assert line[2 + len(first) : 29] == " " * (27 - len(first))
        assert line[29] != " "


def _check_new_folder(root: Path, lines: list[str], zh: bool) -> None:
    """Checks the files of a new folder, and the counts that the readers find in them."""
    assert tree(root) == new_tree(zh)
    for entry in tree(root).values():
        assert entry[0] != "file" or not (entry[1].startswith(b"\xef\xbb\xbf") or b"\r" in entry[1])
    folder = DataFolder(root)
    assert read_settings(folder) == (Settings(Lang.ZH if zh else Lang.EN), ())
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert problems == ()
    counts = (len(catalog.categories), len(catalog.ingredients), len(catalog.tags))
    pantry, problems = read_pantry(folder, catalog)
    assert pantry is not None
    assert problems == ()
    assert (*counts, len(pantry.ingredients)) == (6, 22, 5, 5)
    expected = [
        f"{counts[0]} 个分类，{counts[1]} 种食材，{counts[2]} 个标签",
        f"{len(pantry.ingredients)} 种食材",
    ]
    if not zh:
        expected = [
            f"{counts[0]} categories, {counts[1]} ingredients, {counts[2]} tags",
            f"{len(pantry.ingredients)} ingredients",
        ]
    assert [line[29:] for line in lines[2:4]] == expected
    assert lines[2].startswith("  catalog.toml")


def test_f08_t16_the_output_of_a_new_folder_in_both_languages_and_its_files(
    tmp_path: Path,
) -> None:
    """The prototype's lines, the columns, the example's bytes, and the counts of the readers."""
    home = make_home(tmp_path)
    code, out, err = call(home, ["init"])
    root = home / "recipe-menu"
    assert (code, out, err) == out_of(0, new(root))
    _check_columns(out.splitlines())
    _check_new_folder(root, out.splitlines(), zh=False)

    zh_root = tmp_path / "zh"
    code, out, err = call(home, ["init", "--lang", "zh", "--data", str(zh_root)])
    assert (code, out, err) == out_of(0, new_zh(zh_root))
    _check_columns(out.splitlines())
    _check_new_folder(zh_root, out.splitlines(), zh=True)
