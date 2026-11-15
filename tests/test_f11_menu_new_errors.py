"""Tests of F11 for menu new when it refuses, fails, or is interrupted, and what it reads."""

from pathlib import Path

from f03_support import write
from f05_support import make_home
from f07_changes import catalog_brace, mapo_mistake, the_typo
from f07_texts import NOT_A_WEEK_NAME, Prob
from f08_support import (
    CTRL_C,
    DENIED,
    IO,
    NO_SPACE,
    call_main,
    dangling_link,
    faults,
    full_record,
    rule,
    tree,
)
from f08_texts import FILE_WRITE_DENIED, FOLDER_ACCESS_DENIED, file_error, folder_system_error
from f09_support import assert_among_check, at, made
from f09_texts import (
    E_BRACE,
    FILE_IS_FOLDER,
    FOLDER_IS_FILE,
    FOLDER_MISSING,
    TOML_ENDING_NOT_SMALL,
    err,
    out,
    stop,
)
from f11_support import (
    empty_menus,
    first_half,
    held,
    menu_text,
    menus_as_file,
    no_menus_folder,
)
from f11_texts import (
    DATES,
    LUNCH_DINNER,
    exists,
    exists_zh,
    fail,
    fail_zh,
    left,
    left_zh,
    new,
)
from recipe_menu.datafile import DataFolder

BOTH = "lunch and dinner"
MISSING_KEY_WEEK = ('The key "week" is missing.', "缺少键“week”。")
NO_SPACE_TEXT = file_error("No space left on device")
READ_SETTINGS = "read settings.toml"
OPEN_48 = "open menus/2026-W48.toml"
UNLINK_48 = "unlink menus/2026-W48.toml"
# Inputs 2 to 8 of F11-T22: the name of the entry, and its bytes (None for a folder or a link).
ENTRIES = {
    2: ("2026-W47.toml", b"[[[\n"),
    3: ("2026-W47.toml", b""),
    4: ("2026-w47.toml", b""),
    5: ("2026-W47.TOML", b""),
    6: ("2026-W47.Toml", b""),
    7: ("2026-W47.toml", None),
    8: ("2026-W47.toml", None),
}
# What ``menu show 2026-W47`` stops at for the inputs that also run it and ``check``.
STOPS = {
    3: Prob("menus/2026-W47.toml", None, MISSING_KEY_WEEK),
    4: Prob("menus/2026-w47.toml", None, NOT_A_WEEK_NAME),
    5: Prob("menus/2026-W47.TOML", None, TOML_ENDING_NOT_SMALL),
    7: Prob("menus/2026-W47.toml", None, FILE_IS_FOLDER),
}


def _put_entry(root: Path, number: int) -> Path:
    """Puts the entry of input ``number`` of F11-T22 into ``menus/`` and gives its path."""
    name, data = ENTRIES[number]
    path = root / "menus" / name
    if data is not None:
        write(path, data.decode())
    elif number == 7:
        path.mkdir()
    else:
        dangling_link(path)
    return path


def _check_refusals(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Runs inputs 1 to 8 of F11-T22 and checks that no entry changes."""
    before = full_record(example.root)
    file = example.menu_file("2026-W47")
    assert at(home, example, "menu", "new", "2026-W47") == err(1, [exists(file)])
    assert at(home, example, "menu", "new", "next", "--lang", "zh") == err(1, [exists_zh(file)])
    assert full_record(example.root) == before
    for number in ENTRIES:
        root = made(example, tmp_path, f"x{number}", empty_menus)
        entry = _put_entry(root, number)
        before = full_record(root)
        assert at(home, root, "menu", "new", "2026-W47") == err(1, [exists(entry)]), number
        result = at(home, root, "menu", "new", "2026-W47", "--lang", "zh")
        assert result == err(1, [exists_zh(entry)]), number
        if number in STOPS:
            result = at(home, root, "menu", "show", "2026-W47")
            assert result == stop(STOPS[number]), number
            assert_among_check(home, root, STOPS[number])
        assert full_record(root) == before, number


def test_f11_t22_an_entry_with_the_name_of_the_file_gives_a_refusal_that_changes_nothing(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Eight inputs of an entry that is there, and a file that appears after the listing."""
    home = make_home(tmp_path)
    _check_refusals(home, example_folder, tmp_path)
    x = made(example_folder, tmp_path, "race", empty_menus)
    file = x / "menus" / "2026-W47.toml"
    with faults(x, rule("open", file, how="race")) as state:
        result = at(home, x, "menu", "new", "2026-W47")
    assert result == err(1, [exists(file)])
    assert state.calls == [READ_SETTINGS, "open menus/2026-W47.toml"]
    assert held(file) == b"mine\n"


def _run_new(home: Path, root: Path, *argv: str, rules: tuple = ()) -> tuple[tuple, list[str]]:
    """Runs ``menu new`` with the arguments inside the fault harness, and gives the record."""
    with faults(root, *rules) as state:
        result = at(home, root, "menu", "new", *argv)
    return result, state.calls


def _check_listing_failures(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Runs inputs 1 to 4 of F11-T23: a listing that fails names the folder in full."""
    inputs = [
        (1, no_menus_folder, FOLDER_MISSING, True),
        (2, menus_as_file, FOLDER_IS_FILE, True),
        (3, None, FOLDER_ACCESS_DENIED, True),
        (4, None, folder_system_error("Input/output error"), False),
    ]
    for number, change, message, both in inputs:
        root = made(example, tmp_path, f"r{number}", *([change] if change else []))
        menus = root / "menus"
        rules = ()
        if number in (3, 4):
            rules = (rule("list", menus, DENIED if number == 3 else IO),)
        before = tree(root)
        assert _run_new(home, root, "2026-W48", rules=rules)[0] == err(1, fail(menus, message))
        if both:
            result = _run_new(home, root, "2026-W48", "--lang", "zh", rules=rules)[0]
            assert result == err(1, fail_zh(menus, message))
        assert tree(root) == before, number


def _check_open_failures(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Runs inputs 5 to 7 of F11-T23: a failed open or write names the file in full."""
    inputs = [
        (5, "open", DENIED, FILE_WRITE_DENIED),
        (6, "open", IO, file_error("Input/output error")),
        (7, "write", NO_SPACE, NO_SPACE_TEXT),
    ]
    for number, kind, effect, message in inputs:
        root = made(example, tmp_path, f"r{number}")
        path = root / "menus" / "2026-W48.toml"
        found = (rule(kind, path, effect),)
        before = tree(root)
        result, record = _run_new(home, root, "2026-W48", rules=found)
        assert result == err(1, fail(path, message)), number
        if number == 5:
            result, _ = _run_new(home, root, "2026-W48", "--lang", "zh", rules=found)
            assert result == err(1, fail_zh(path, message))
        if number == 7:
            assert record == [READ_SETTINGS, OPEN_48, UNLINK_48]
        assert tree(root) == before, number


def _check_left_behind(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Runs inputs 8 to 10 of F11-T23: a file that cannot be removed stays and is named."""
    root = made(example, tmp_path, "r8")
    path = root / "menus" / "2026-W48.toml"
    stuck = (rule("write", path, NO_SPACE), rule("unlink", path, DENIED))
    result, _ = _run_new(home, root, "2026-W48", rules=stuck)
    assert result == err(1, left(path, NO_SPACE_TEXT, "2026-W48"))
    assert held(path) == first_half(menu_text("2026-W48", LUNCH_DINNER))
    assert at(home, root, "menu", "new", "2026-W48") == err(1, [exists(path)])
    path.unlink()
    again = at(home, root, "menu", "new", "2026-W48")
    assert again == out(new(path, DATES["2026-W48"][0], BOTH))
    assert held(path) == menu_text("2026-W48", LUNCH_DINNER)
    root = made(example, tmp_path, "r9")
    path = root / "menus" / "2026-W48.toml"
    stuck = (rule("write", path, NO_SPACE), rule("unlink", path, DENIED))
    result, _ = _run_new(home, root, "2026-W48", "--lang", "zh", rules=stuck)
    assert result == err(1, left_zh(path, NO_SPACE_TEXT, "2026-W48"))
    root = made(example, tmp_path, "r10", empty_menus)
    path = root / "menus" / "2026-W47.toml"
    stuck = (rule("write", path, NO_SPACE), rule("unlink", path, DENIED))
    result, _ = _run_new(home, root, "next", rules=stuck)
    assert result == err(1, left(path, NO_SPACE_TEXT, "2026-W47"))


def test_f11_t23_a_failure_names_the_file_or_the_folder_in_full_and_says_what_is_left(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Ten inputs: a failed listing, open, or write, and a removal that fails."""
    home = make_home(tmp_path)
    _check_listing_failures(home, example_folder, tmp_path)
    _check_open_failures(home, example_folder, tmp_path)
    _check_left_behind(home, example_folder, tmp_path)


def _ctrl_c(home: Path, root: Path, rules: tuple, *argv: str) -> tuple[tuple, list[str]]:
    """Runs ``menu new`` with the arguments through ``call_main`` inside the fault harness."""
    with faults(root, *rules) as state:
        result = call_main(home, ["menu", "new", *argv, "--data", str(root)])
    return result, state.calls


def test_f11_t24_ctrl_c_during_menu_new_exits_with_130_and_removes_the_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Three inputs: a Ctrl+C in the write, in the open, and in the write with a stuck file."""
    home = make_home(tmp_path)
    root = made(example_folder, tmp_path, "r1")
    path = root / "menus" / "2026-W48.toml"
    result, record = _ctrl_c(home, root, (rule("write", path, CTRL_C),), "2026-W48")
    assert (result, record) == ((130, "", ""), [READ_SETTINGS, OPEN_48, UNLINK_48])
    assert held(path) is None
    root = made(example_folder, tmp_path, "r2")
    path = root / "menus" / "2026-W48.toml"
    result, record = _ctrl_c(home, root, (rule("open", path, CTRL_C, "after"),), "2026-W48")
    assert (result, record) == ((130, "", ""), [READ_SETTINGS, OPEN_48])
    assert held(path) == b""
    assert at(home, root, "menu", "new", "2026-W48") == err(1, [exists(path)])
    problem = Prob("menus/2026-W48.toml", None, MISSING_KEY_WEEK)
    assert at(home, root, "menu", "show", "2026-W48") == stop(problem)
    assert_among_check(home, root, problem)
    root = made(example_folder, tmp_path, "r3")
    path = root / "menus" / "2026-W48.toml"
    stuck = (rule("write", path, CTRL_C), rule("unlink", path, DENIED))
    result, _ = _ctrl_c(home, root, stuck, "2026-W48", "--lang", "zh")
    assert result == (130, "", "")
    assert held(path) == first_half(menu_text("2026-W48", LUNCH_DINNER))
    assert at(home, root, "menu", "new", "2026-W48", "--lang", "zh") == err(1, [exists_zh(path)])


def _broken(root: Path) -> None:
    """Breaks the pantry and the menu of week 48, and adds two names that are not menus."""
    write(root / "pantry.toml", "[[[\n")
    write(root / "menus" / "2026-W48.toml", "[[[\n")
    write(root / "menus" / "plan.toml", "")
    write(root / "menus" / "2026-w49.toml", "")


def test_f11_t25_menu_new_reads_no_data_file_and_a_broken_file_does_not_stop_it(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The broken data folder B: a new menu, the refusals, and ``menu show`` that stops."""
    home = make_home(tmp_path)
    changes = (catalog_brace, mapo_mistake, the_typo, _broken)
    b = made(example_folder, tmp_path, "b", *changes)
    file = b / "menus" / "2026-W50.toml"
    with faults(b) as state:
        result = at(home, b, "menu", "new", "2026-W50")
    assert result == out(new(file, DATES["2026-W50"][0], BOTH))
    assert held(file) == menu_text("2026-W50", LUNCH_DINNER)
    assert state.calls == [READ_SETTINGS, "open menus/2026-W50.toml"]
    assert state.listings == ["menus"]
    result = at(home, b, "menu", "new", "2026-W47", "--lang", "zh")
    assert result == err(1, [exists_zh(b / "menus" / "2026-W47.toml")])
    assert at(home, b, "menu", "new", "2026-W48") == err(1, [exists(b / "menus" / "2026-W48.toml")])
    assert at(home, b, "menu", "new", "2026-W49") == err(1, [exists(b / "menus" / "2026-w49.toml")])
    assert at(home, b, "menu", "show", "2026-W50") == stop(E_BRACE)
