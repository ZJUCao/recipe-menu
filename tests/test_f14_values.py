"""Tests of F14 for the generator of Context and main, read_file_text, and parse_toml (T25-T27)."""

import io
from pathlib import Path
from random import Random

import pytest

from f03_support import M_ACCESS_DENIED, M_NOT_UTF8, m_system_error, put_bytes
from f05_support import TODAY, make_home
from f08_support import DENIED, IO, rule
from f09_support import made
from f09_texts import FILE_IS_FOLDER
from f13_support import pristine, shop_faults
from f14_support import FILE_47, assert_text_problem, seeded
from f14_texts import R3
from recipe_menu.app import Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder, Problem, parse_toml, read_file_text
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

FILE_49 = "menus/2026-W49.toml"


def _check_context_example(folder: DataFolder) -> Context:
    """The example of 3.3: the generator that a context holds, and the default of each context."""
    out, err = io.StringIO(), io.StringIO()
    given = seeded(5)
    context = Context(Lang.EN, folder, Settings(), out, err, TODAY, given)
    assert context.random is given
    first = Context(Lang.EN, folder, Settings(), out, err, TODAY)
    second = Context(Lang.EN, folder, Settings(), out, err, TODAY)
    assert first.random is not second.random
    assert first != second
    assert first.random.random() == second.random.random() == seeded(0).random()
    return context


def _pick_command(seen: list[Random]) -> Command:
    """Makes the command ``pick`` of the example of 3.4, which keeps the generator it gets."""

    def run_pick(context: Context, arguments: Arguments) -> int:
        """Keeps the generator of the context."""
        seen.append(context.random)
        return 0

    return Command(("pick",), Message("Pick a recipe.", "挑一个菜谱。"), run_pick)


def test_f14_t25_context_holds_the_generator_that_main_passes_on(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The examples of 3.3 and 3.4, the hash of a context, and a new generator for each call."""
    home = make_home(tmp_path)
    context = _check_context_example(DataFolder(tmp_path / "unused"))
    assert isinstance(hash(context), int)
    seen: list[Random] = []
    pick = _pick_command(seen)

    def run(random: Random | None) -> int:
        """Runs ``main`` with the command ``pick`` and a generator, or none."""
        return main(
            ["pick", "--data", str(example_folder.root)],
            environ={},
            home=home,
            today=TODAY,
            stdout=io.StringIO(),
            stderr=io.StringIO(),
            commands=[pick],
            random=random,
        )

    given = seeded(9)
    assert run(given) == 0
    assert seen == [given]
    assert run(None) == 0
    assert isinstance(seen[1], Random)
    assert seen[1] is not given
    assert run(None) == 0
    assert isinstance(seen[2], Random)
    assert seen[2] is not given
    assert seen[2] is not seen[1]
    assert seen[1].getstate() != seen[2].getstate()


def _check_text_example(folder: DataFolder) -> None:
    """The example of 3.5, up to its call that raises."""
    file = folder.menu_file("2026-W47")
    text = read_file_text(folder, file)
    assert isinstance(text, str)
    assert text.splitlines()[:2] == ["# 2026-W47: 16 to 22 November 2026", 'week = "2026-W47"']
    file.write_bytes(b'\xef\xbb\xbfweek = "2026-W47"\r\n')
    assert read_file_text(folder, file) == 'week = "2026-W47"\r\n'
    file.write_bytes(b"week = 1\n\xff\n")
    broken = read_file_text(folder, file)
    assert isinstance(broken, Problem)
    assert broken.place == BiText("line 2", "第 2 行")
    assert broken.text(Lang.EN) == M_NOT_UTF8[0]
    missing = read_file_text(folder, folder.menu_file("2026-W48"))
    assert isinstance(missing, Problem)
    assert (missing.file, missing.place) == (Path("menus", "2026-W48.toml"), None)
    assert missing.text(Lang.EN) == "The file is missing."
    with pytest.raises(ValueError):
        read_file_text(folder, folder.root.parent / "elsewhere.toml")


def _check_texts_and_problems(folder: DataFolder) -> None:
    """Inputs 1 to 3: the text as it is, a file that is not UTF-8, and a folder."""
    file = folder.menu_file("2026-W49")
    for data, text in (
        (b"", ""),
        (b"\xef\xbb\xbf", ""),
        (b"a\r\nb\rc\n", "a\r\nb\rc\n"),
        (b'dinner = ["rice"\n', 'dinner = ["rice"\n'),
    ):
        put_bytes(file, data)
        assert read_file_text(folder, file) == text, data
    for data, place in ((b"week = 1\nx = 2\n\xe4\xb8\n", "line 3"), (b"\xff\xfew\x00", "line 1")):
        put_bytes(file, data)
        problem = read_file_text(folder, file)
        number = place.split()[1]
        assert_text_problem(problem, FILE_49, BiText(place, f"第 {number} 行"), M_NOT_UTF8)
    file.unlink()
    file.mkdir()
    assert_text_problem(read_file_text(folder, file), FILE_49, None, FILE_IS_FOLDER)


def _check_failed_reads(folder: DataFolder) -> None:
    """Inputs 4 and 5: a read that the system refuses, and a path outside the data folder."""
    file = folder.menu_file("2026-W47")
    for effect, message in ((DENIED, M_ACCESS_DENIED), (IO, m_system_error("Input/output error"))):
        with shop_faults(folder.root, rule("read", file, effect)):
            problem = read_file_text(folder, file)
        assert_text_problem(problem, FILE_47, None, message)
    elsewhere = folder.root.parent / "elsewhere.toml"
    put_bytes(elsewhere, b"x\n")
    with shop_faults(folder.root.parent) as state, pytest.raises(ValueError):
        read_file_text(folder, elsewhere)
    assert state.calls == []


def test_f14_t26_read_file_text_gives_the_text_as_it_is_or_a_problem(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 3.5, then the text of a file, a file that is not UTF-8, and a failed read."""
    source = pristine(example_folder, tmp_path)
    _check_text_example(example_folder)
    folder = DataFolder(made(source, tmp_path, "f"))
    _check_texts_and_problems(folder)
    _check_failed_reads(folder)


def test_f14_t27_parse_toml_gives_the_table_of_a_text_or_none(default_int_limit: None) -> None:
    """The example of 3.6, then three inputs."""
    assert parse_toml('week = "2026-W47"\n[monday]\ndinner = ["rice"]\n') == {
        "week": "2026-W47",
        "monday": {"dinner": ["rice"]},
    }
    assert parse_toml("") == {}
    assert parse_toml("[monday]\n[monday]\n") is None
    assert parse_toml('dinner = ["rice"') is None
    assert parse_toml("servings = " + "1" * 5000) is None
    assert parse_toml("x = " + "[" * 5000 + "]" * 5000) is None
    assert parse_toml("a = 1\r\n") == {"a": 1}
    assert parse_toml("[monday]\ndinner = [\n]\n") == {"monday": {"dinner": []}}
    for text in ("\x00", "\ufeffa = 1\n", "a = 1\rb = 2\n", R3 + '\n[monday]\nlunch = ["rice"]\n'):
        assert parse_toml(text) is None, text
