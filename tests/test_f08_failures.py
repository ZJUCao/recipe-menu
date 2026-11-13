"""Tests of F08 for a failure, Ctrl+C, and a mistake on the command line of recipe-menu init.

These are T19 to T21.
"""

from pathlib import Path

from f05_support import make_home, unreadable_name
from f07_support import check, rep
from f07_texts import FILE_MISSING, FOLDER_MISSING, Prob
from f08_support import (
    CTRL_C,
    DENIED,
    IO,
    call_main,
    faults,
    file_of,
    init,
    new_tree,
    rule,
    system_message,
    tree,
)
from f08_texts import (
    FILE_EXISTS,
    FILE_WRITE_DENIED,
    FOLDER_CREATE_DENIED,
    FOLDER_EXISTS,
    MISSING_PANTRY,
    err_of,
    fail,
    file_error,
    holds,
    leftover,
    new,
    out_of,
)


def _new_home(tmp_path: Path, number: int) -> tuple[Path, Path]:
    """Makes the home ``h<number>`` and gives it with the default folder, which is missing."""
    home = tmp_path / f"h{number}"
    home.mkdir()
    return home, home / "recipe-menu"


def _failures_in_both_languages(tmp_path: Path) -> None:
    """Runs inputs 1 and 2 of F08-T19: a failure in English and in Chinese."""
    home, root = _new_home(tmp_path, 1)
    root.mkdir()
    with faults(home, rule("mkdir", root / "recipes", DENIED)):
        first, second = init(home), init(home, "--lang", "zh")
    assert first == err_of(1, fail(root / "recipes", FOLDER_CREATE_DENIED))
    assert second == err_of(1, fail(root / "recipes", FOLDER_CREATE_DENIED, zh=True))
    assert tree(root) == {}

    home, root = _new_home(tmp_path, 2)
    recipe = root / "recipes" / "tomato-egg.toml"
    msg = file_error("Input/output error")
    with faults(home, rule("open", recipe, IO)):
        first, second = init(home), init(home, "--lang", "zh")
    assert first == err_of(1, fail(recipe, msg))
    assert second == err_of(1, fail(recipe, msg, zh=True))
    assert not root.exists()


def _races(tmp_path: Path) -> None:
    """Runs inputs 3 and 4 of F08-T19: a file and a folder that another program made."""
    home, root = _new_home(tmp_path, 3)
    root.mkdir()
    with faults(home, rule("open", root / "catalog.toml", how="race")):
        first = init(home)
    assert first == err_of(1, fail(root / "catalog.toml", FILE_EXISTS))
    assert tree(root) == {"catalog.toml": file_of(b"mine\n")}
    assert init(home) == err_of(1, [holds(root)])

    home, root = _new_home(tmp_path, 4)
    with faults(home, rule("mkdir", root, how="race")):
        first = init(home)
    assert first == err_of(1, fail(root, FOLDER_EXISTS))


def _left_behind(tmp_path: Path) -> None:
    """Runs input 6 of F08-T19: a removal that fails, and the folder that stays."""
    home, root = _new_home(tmp_path, 6)
    rules = (
        rule("open", root / "pantry.toml", DENIED),
        rule("unlink", root / "settings.toml", DENIED),
    )
    with faults(home, *rules):
        first = init(home)
    assert first == err_of(1, leftover(root / "pantry.toml", FILE_WRITE_DENIED, root))
    assert tree(root) == {"settings.toml": new_tree()["settings.toml"]}
    assert init(home) == err_of(1, [holds(root)])
    (root / "settings.toml").unlink()
    assert init(home) == out_of(0, new(root))

    home, root = _new_home(tmp_path, 7)
    rules = (
        rule("open", root / "pantry.toml", DENIED),
        rule("unlink", root / "settings.toml", DENIED),
    )
    with faults(home, *rules):
        last = init(home, "--lang", "zh")
    expected = leftover(root / "pantry.toml", FILE_WRITE_DENIED, root, zh=True)
    assert last == err_of(1, expected)


def test_f08_t19_a_failure_is_three_lines_on_the_error_stream_with_exit_code_1(
    tmp_path: Path,
) -> None:
    """The file of the problem, its text, and `init changed nothing.` or the data folder."""
    _failures_in_both_languages(tmp_path)
    _races(tmp_path)
    home = make_home(tmp_path)
    unreadable = unreadable_name(tmp_path)
    msg = system_message("folder", unreadable)
    assert init(home, folder=unreadable) == err_of(1, fail(unreadable, msg))
    nested = unreadable / "recipe-menu"
    assert init(home, folder=nested) == err_of(1, fail(nested, msg))
    _left_behind(tmp_path)


def _interrupted(tmp_path: Path, number: int, found: tuple, *argv: str) -> tuple[Path, Path]:
    """Runs ``init`` with the rules and expects exit code 130 with nothing written."""
    home, root = _new_home(tmp_path, number)
    if number == 2:
        root.mkdir()
    rules = [rule(kind, root / name, effect, how) for kind, name, effect, how in found]
    with faults(home, *rules):
        assert call_main(home, ["init", *argv]) == (130, "", "")
    return home, root


def test_f08_t20_ctrl_c_gives_130_with_nothing_written_and_the_removal_has_run(
    tmp_path: Path,
) -> None:
    """Ctrl+C removes what `init` made, except in the two cases that act like a killed process."""
    _, root = _interrupted(tmp_path, 1, [("open", "catalog.toml", CTRL_C, "raise")])
    assert not root.exists()
    _, root = _interrupted(tmp_path, 2, [("mkdir", "menus", CTRL_C, "raise")], "--lang", "zh")
    assert tree(root) == {}
    _, root = _interrupted(tmp_path, 3, [("write", "recipes/tomato-egg.toml", CTRL_C, "raise")])
    assert not root.exists()

    home, root = _interrupted(tmp_path, 4, [("open", "pantry.toml", CTRL_C, "after")])
    assert tree(root) == {"pantry.toml": file_of(b"")}
    assert init(home) == err_of(1, [holds(root)])
    missing = [
        Prob("settings.toml", None, FILE_MISSING),
        Prob("catalog.toml", None, FILE_MISSING),
        Prob("pantry.toml", None, MISSING_PANTRY),
        Prob("recipes", None, FOLDER_MISSING),
        Prob("menus", None, FOLDER_MISSING),
    ]
    assert check(home, None) == rep(1, 0, 0, missing, [])

    found = [
        ("open", "catalog.toml", CTRL_C, "raise"),
        ("unlink", "settings.toml", CTRL_C, "raise"),
    ]
    home, root = _interrupted(tmp_path, 5, found)
    kept = {"settings.toml": new_tree()["settings.toml"]}
    folders = {name: new_tree()[name] for name in ("recipes", "menus", "shopping")}
    assert tree(root) == kept | folders
    two = [Prob("catalog.toml", None, FILE_MISSING), Prob("pantry.toml", None, FILE_MISSING)]
    assert check(home, None) == rep(1, 0, 0, two, [])
    assert init(home) == err_of(1, [holds(root)])


def _usage_errors(home: Path, tmp_path: Path) -> None:
    """Runs the usage errors of F08-T21: nothing is created in ``M``."""
    target = tmp_path / "m"
    cases = [
        (["extra"], 'Unexpected argument "extra". Write "recipe-menu init".'),
        (["extra", "--lang", "zh"], "多余的参数“extra”。请写成“recipe-menu init”。"),
        (["--tag", "快手"], '"init" has no option "--tag". It has no options of its own.'),
        (["--tag", "快手", "--lang", "zh"], "“init”没有选项“--tag”。它没有自己的选项。"),
        (["--lang", "fr"], '--lang must be en or zh, not "fr".'),
    ]
    second = [
        'Run "recipe-menu --help" to see the commands.',
        "运行“recipe-menu --help”查看命令。",
        'Run "recipe-menu --help" to see the options.',
        "运行“recipe-menu --help”查看选项。",
        'Run "recipe-menu --help" to see the options.',
    ]
    for (argv, first), last in zip(cases, second, strict=True):
        assert init(home, *argv, folder=target) == err_of(2, [first, last]), argv
        assert not target.exists(), argv
    for argv in (["--help"], ["--help", "--lang", "zh"]):
        plain = call_main(home, argv)
        assert plain[0] == 0
        assert plain[1] != ""
        assert plain[2] == ""
        assert init(home, *argv, folder=target) == plain
        assert not target.exists(), argv


def test_f08_t21_init_takes_no_argument_and_cli_rejects_a_mistake_before_it_runs(
    tmp_path: Path,
) -> None:
    """One new folder, the usage errors with nothing created, and `init --help`."""
    home = make_home(tmp_path)
    target = tmp_path / "n"
    assert init(home, folder=target) == out_of(0, new(target))
    _usage_errors(home, tmp_path)
