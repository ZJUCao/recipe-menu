"""Tests of F05 for main: the design's example, the prototypes, and the version scenarios.

These are T51 to T54.
"""

from pathlib import Path

from f03_support import write
from f05_support import (
    VERSION_LINE,
    assert_ran,
    copy_example,
    go,
    in_folder,
    make_folder,
    make_home,
    record,
    run_main,
)
from f05_texts import (
    COMMANDS_EN,
    COMMANDS_ZH,
    EN,
    OPTIONS_EN,
    OPTIONS_ZH,
    ZH,
    err_result,
    no_data_folder,
    stopped,
)
from recipe_menu.app import Arguments, Command, Context
from recipe_menu.datafile import DataFolder
from recipe_menu.text import Message

LANG_FR = '--lang must be en or zh, not "fr".'
INIT_HINT = 'Run "recipe-menu init" to create it, or name another folder with --data.'
TAG_ARGUMENTS = Arguments((), (("--tag", "素"),))


def run_list(context: Context, arguments: Arguments) -> int:
    """Writes the language and the value of ``--tag``, as the design's example does."""
    tag = arguments.option("--tag")
    context.out.write(f"{context.lang.value} {tag}\n")
    return 0


def test_f05_t51_the_design_example_of_main(tmp_path: Path, example_folder: DataFolder) -> None:
    """Every assertion of the example of 2.9, with the version of the project."""
    home = make_home(tmp_path)
    folder = example_folder
    listing = Command(
        ("list",), Message("List the recipes.", "列出菜谱。"), run_list, options=("--tag",)
    )
    environ: dict[str, str] = {}

    def run(*argv: str) -> tuple[int, str, str]:
        """Runs main with the design's command and gives the result."""
        return run_main(home, *argv, environ=environ, commands=[listing])

    data = str(folder.root)
    assert run("list", "--tag", "素", "--data", data) == (0, "en 素\n", "")
    assert run("--lang", "zh", "--data", data, "list") == (0, "zh None\n", "")
    assert run("--version") == (0, VERSION_LINE, "")
    code, out, err = run("cook", "--data", data)
    assert (code, out) == (2, "")
    assert err.splitlines() == ['Unknown command "cook".', COMMANDS_EN]
    code, _, err = run("list", "--tags", "素", "--data", data)
    assert err.splitlines() == [
        '"list" has no option "--tags". Its own option is "--tag".',
        OPTIONS_EN,
    ]
    assert run("list", "--tag", "--data", data) == (2, "", "--tag needs a value.\n")
    code, _, err = run("list", "--lang", "--lang", "zh", "--data", data)
    assert err.splitlines() == ["--lang 后面要写一个值。", OPTIONS_ZH]
    write(folder.settings, 'language = "zh"\n')
    code, _, err = run("cook", "--data", data)
    assert err.splitlines() == ["未知命令“cook”。", COMMANDS_ZH]
    assert run("list", "--data", data) == (0, "zh None\n", "")
    code, _, err = run("list")
    assert code == 1
    default = home / "recipe-menu"
    assert err.splitlines() == [f"There is no data folder at {default}.", INIT_HINT]
    assert run("list", "--data", "~/recipe-menu") == (1, "", err)
    environ["RECIPE_MENU_DATA"] = data
    code, _, err = run("list", "--data")
    assert err.splitlines() == ["--data 后面要写一个值。", OPTIONS_ZH]


def test_f05_t52_the_prototype_mistakes_and_the_missing_folder(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """Mistakes on the command line, no data folder yet, and a broken settings file."""
    home = make_home(tmp_path)
    env = in_folder(example_folder.root)
    folder = home / "recipe-menu"
    cases = [
        (("list", "--lang", "fr"), env, err_result(2, LANG_FR, OPTIONS_EN)),
        (("cook",), env, err_result(2, 'Unknown command "cook".', COMMANDS_EN)),
        (("list",), {}, no_data_folder(folder)),
        (("list", "--lang", "zh"), {}, no_data_folder(folder, ZH)),
    ]
    for argv, environ, expected in cases:
        result, kit = go(home, *argv, environ=environ)
        assert result == expected, argv
        assert kit.nothing_ran(), argv
    write(example_folder.settings, 'meals = ["lunch", "supper"]\n')
    result, kit = go(home, "list", environ=env)
    unknown = 'Unknown meal "supper". The meals are breakfast, lunch, and dinner.'
    assert result == stopped("settings.toml, meals", unknown)
    assert kit.nothing_ran()


def test_f05_t53_data_option_variable_and_language_of_the_settings(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """v0.1-S20 and S21 at main: --data wins, and the settings' language holds for a command."""
    home = make_home(tmp_path)
    b = copy_example(example_folder, tmp_path / "One Drive" / "菜谱")
    c = copy_example(example_folder, tmp_path / "C")
    cases = [
        (("list", "--data", str(b)), {}, b),
        (("list",), in_folder(c), c),
        (("list", "--data", str(b)), in_folder(c), b),
    ]
    for argv, environ, root in cases:
        result, kit = go(home, *argv, environ=environ)
        assert result == (0, "", ""), argv
        context, _ = kit.ran("LIST")
        assert str(context.folder.root) == str(root), argv
    missing = home / "recipe-menu"
    assert go(home, "list")[0] == no_data_folder(missing)
    assert go(home, "list", "--lang", "zh")[0] == no_data_folder(missing, ZH)
    env = in_folder(example_folder.root)
    path = example_folder.settings
    path.write_bytes(path.read_bytes().replace(b'language = "en"', b'language = "zh"'))
    for argv, lang in [
        (("list", "--tag", "素"), ZH),
        (("list", "--tag", "素", "--lang", "en"), EN),
    ]:
        result, kit = go(home, *argv, environ=env)
        assert result == (0, "", ""), argv
        assert_ran(kit, "LIST", lang, TAG_ARGUMENTS)
    lines = path.read_bytes().splitlines(keepends=True)
    path.write_bytes(b"".join(line for line in lines if not line.startswith(b"language")))
    result, kit = go(home, "list", "--tag", "素", environ=env)
    assert result == (0, "", "")
    assert_ran(kit, "LIST", EN, TAG_ARGUMENTS)


def test_f05_t54_main_writes_no_file_and_keeps_no_state(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """The same line gives the same result twice, and the folders hold the same bytes after."""
    home = make_home(tmp_path)
    example = in_folder(example_folder.root)
    zh = in_folder(make_folder(tmp_path, "zh"))
    broken = in_folder(make_folder(tmp_path, "broken"))
    lines = [
        (("--help",), {}),
        (("--version",), {}),
        (("cook",), {}),
        (("list", "--tag", "素"), example),
        (("list",), broken),
        (("check",), broken),
        (("init",), {}),
        (("list",), {}),
        (("list", "--lang", "fr"), zh),
        (("show", "a", "b"), {}),
    ]
    before = record(tmp_path)
    for argv, environ in lines:
        first, first_kit = go(home, *argv, environ=environ)
        second, second_kit = go(home, *argv, environ=environ)
        assert first == second, argv
        assert first_kit.snapshot() == second_kit.snapshot(), argv
    assert record(tmp_path) == before
