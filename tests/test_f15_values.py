"""Tests of F15 for Context, main, use_utf8_input, check_recipe, and problem_block (T03 to T06)."""

import dataclasses
import io
import sys
from datetime import date
from pathlib import Path
from random import Random

import pytest

from f03_support import at_line, write
from f04_support import M_NO_EN_STEPS, STEPS, check_problems, err, warn
from f05_support import make_home
from f05_texts import lines_text
from f07_changes import catalog_brace, mapo_mistake
from f07_support import AFTER, call, check, snapshot
from f09_support import at, made
from f09_texts import FILE_MISSING, LIST, MISSING_BRACE, TOMATO, out
from f11_texts import SHOW_47
from f13_support import pristine, shop_faults
from f15_support import Watched, terminal
from recipe_menu.app import Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.commands.check import check_recipe, problem_block
from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message, use_utf8_input

TODAY = date(2026, 11, 10)


def _check_context_example() -> None:
    """Runs the example of 3.1."""
    out_stream, err_stream = io.StringIO(), io.StringIO()
    folder = DataFolder(Path("C:/Users/Troy/recipe-menu"))
    answers = io.StringIO("garlic-broccoli\n")
    context = Context(Lang.EN, folder, Settings(), out_stream, err_stream, TODAY, input=answers)
    assert context.input is answers
    assert context.input.readline() == "garlic-broccoli\n"
    first = Context(Lang.EN, folder, Settings(), out_stream, err_stream, TODAY)
    second = Context(Lang.EN, folder, Settings(), out_stream, err_stream, TODAY)
    assert first.input is not second.input
    assert first.input.readline() == second.input.readline() == ""
    assert first != second


def _run_echo(context: Context, arguments: Arguments) -> int:
    """Stands in for a command that reads a line, as the example of 3.2 has it."""
    context.out.write(context.input.readline().upper())
    return 0


def _echo(home: Path, example: DataFolder, stdin: io.StringIO | None) -> tuple[int, str, str]:
    """Runs the example of 3.2, with ``stdin`` or without it."""
    echo = Command(("echo",), Message("Repeat a line.", "重复一行。"), _run_echo)
    stdout, stderr = io.StringIO(), io.StringIO()
    code = main(
        ["echo", "--data", str(example.root)],
        environ={},
        home=home,
        today=TODAY,
        stdout=stdout,
        stderr=stderr,
        commands=[echo],
        stdin=stdin,
    )
    return code, stdout.getvalue(), stderr.getvalue()


def _check_context_values(example: DataFolder) -> None:
    """Inputs 1 to 3: the fields, the equality, and the frozen context."""
    names = [field.name for field in dataclasses.fields(Context)]
    assert names == ["lang", "folder", "settings", "out", "err", "today", "random", "input"]
    shared = Random(0)  # noqa: S311 - a fixed seed, no security
    streams = (io.StringIO(), io.StringIO(), io.StringIO())

    def make(stream: io.StringIO) -> Context:
        """Builds a context of the eight values."""
        settings = Settings()
        return Context(Lang.EN, example, settings, *streams[:2], TODAY, shared, stream)

    one, two, other = make(streams[2]), make(streams[2]), make(io.StringIO())
    assert one == two
    assert hash(one) == hash(two)
    assert other not in (one, two)
    with pytest.raises(dataclasses.FrozenInstanceError):
        one.input = io.StringIO()  # type: ignore[misc]


def test_f15_t03_context_holds_the_input_and_main_passes_it_on(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The examples of 3.1 and 3.2, the fields, the standard input, and the watched stream."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_context_example()
    assert _echo(home, example_folder, io.StringIO("salt to taste\n")) == (0, "SALT TO TASTE\n", "")
    _check_context_values(example_folder)
    plain_help = call(home, ["--help"])
    data = b"\xef\xbb\xbf" + "salt 适量\r\n".encode()
    wrapper = io.TextIOWrapper(io.BytesIO(data), encoding="cp1252")
    monkeypatch.setattr(sys, "stdin", wrapper)
    assert _echo(home, example_folder, None) == (0, "SALT 适量\n", "")
    assert (wrapper.encoding, wrapper.errors) == ("utf-8-sig", "replace")
    monkeypatch.setattr(sys, "stdin", Watched())
    assert at(home, source, "list") == out(LIST)
    assert check(home, source.root) == (0, lines_text(*AFTER), "")
    assert at(home, source, "show", "tomato-egg") == out(TOMATO)
    assert at(home, source, "menu", "show", "2026-W47") == out(SHOW_47)
    assert call(home, ["--help"]) == plain_help


def _read_all(stream: io.TextIOWrapper) -> list[str]:
    """Reads a stream with ``readline`` until it gives the empty text."""
    lines = []
    while text := stream.readline():
        lines.append(text)
    return lines


def _wrapped(data: bytes, encoding: str) -> io.TextIOWrapper:
    """Makes a text stream over bytes, and calls ``use_utf8_input`` on it."""
    stream = io.TextIOWrapper(io.BytesIO(data), encoding=encoding)
    use_utf8_input(stream)
    return stream


def test_f15_t04_use_utf8_input_makes_a_stream_read_utf8() -> None:
    """The example of 3.3, and four inputs: other code pages, bad bytes, and other streams."""
    data = b"\xef\xbb\xbf" + "蒜蓉西兰花\r\n".encode() + b"\xffx\n"
    stream = io.TextIOWrapper(io.BytesIO(data), encoding="cp1252")
    use_utf8_input(stream)
    assert (stream.encoding, stream.errors) == ("utf-8-sig", "replace")
    assert stream.readline() == "蒜蓉西兰花\n"
    assert stream.readline() == "\ufffdx\n"
    answers = io.StringIO("西兰花 300 g\n")
    use_utf8_input(answers)
    assert answers.readline() == "西兰花 300 g\n"
    assert _read_all(_wrapped(b"a\n\xef\xbb\xbfb\n", "ascii")) == ["a\n", "\ufeffb\n"]
    chinese = "西兰花 300 g\r\n盐 适量\n".encode()
    assert _read_all(_wrapped(chinese, "gbk")) == ["西兰花 300 g\n", "盐 适量\n"]
    assert _read_all(_wrapped(b"\x80\xfe\n\xe8\xa5", "latin-1")) == ["\ufffd\ufffd\n", "\ufffd"]
    console = terminal(["Rice 300 g"])
    use_utf8_input(console)
    assert console.readline() == "Rice 300 g\n"
    assert console.isatty()
    crlf = io.StringIO("x\r\ny\n")
    use_utf8_input(crlf)
    assert [crlf.readline(), crlf.readline()] == ["x\r\n", "y\n"]


def _check_check_example(example: DataFolder) -> None:
    """Runs the example of 3.4."""
    assert check_recipe(example, "tomato-egg") == ()
    problems = check_recipe(example, "red-braised-pork")
    assert [problem.place for problem in problems] == [BiText("steps", "步骤")]
    mapo_mistake(example.root)
    problems = check_recipe(example, "mapo-tofu")
    assert [problem.file for problem in problems] == [Path("recipes", "mapo-tofu.toml")]
    zh_text = "未知食材“豆瓣酱”。请把它加入目录，或改用目录里的名称。"
    assert problems[0].text(Lang.ZH) == zh_text
    write(example.catalog, "categories = [\n")
    problems = check_recipe(example, "tomato-egg")
    assert [problem.file for problem in problems] == [Path("catalog.toml")]
    with pytest.raises(ValueError):
        check_recipe(example, "Tomato-Egg")


def test_f15_t05_check_recipe_checks_one_recipe_with_the_catalog(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 3.4, and four inputs in the fault harness with the record of the reads."""
    source = pristine(example_folder, tmp_path)
    _check_check_example(example_folder)
    first = made(source, tmp_path, "first")
    before = snapshot(first)
    with shop_faults(first) as state:
        assert check_recipe(DataFolder(first), "tomato-egg") == ()
    assert state.calls == ["read catalog.toml", "read recipes/tomato-egg.toml"]
    assert state.listings == []
    assert snapshot(first) == before
    brace = DataFolder(made(source, tmp_path, "brace", catalog_brace))
    before = snapshot(brace.root)
    with shop_faults(brace.root) as state:
        problems = check_recipe(brace, "red-braised-pork")
    check_problems(
        problems,
        [
            err(at_line(11), MISSING_BRACE, "catalog.toml"),
            warn(STEPS, M_NO_EN_STEPS, "recipes/red-braised-pork.toml"),
        ],
    )
    assert snapshot(brace.root) == before
    second = DataFolder(made(source, tmp_path, "second"))
    before = snapshot(second.root)
    with shop_faults(second.root) as state:
        problems = check_recipe(second, "garlic-broccoli")
    check_problems(problems, [err(None, FILE_MISSING, "recipes/garlic-broccoli.toml")])
    assert snapshot(second.root) == before
    third = DataFolder(made(source, tmp_path, "third"))
    before = snapshot(third.root)
    with shop_faults(third.root) as state:
        for value in ("", "con", "tomato egg", "rice.toml"):
            with pytest.raises(ValueError):
                check_recipe(third, value)
    assert state.calls == []
    assert snapshot(third.root) == before


def test_f15_t06_problem_block_gives_two_lines_for_each_problem() -> None:
    """The example of 3.5, and three inputs: a list, an iterator, and a generator."""
    unknown = Message('Unknown ingredient "{name}".', "未知食材“{name}”。")
    missing_text = Message("The file is missing.", "文件不存在。")
    mapo = Path("recipes", "mapo-tofu.toml")
    problem = Problem.error(mapo, BiText("ingredient 3", "食材 3"), unknown, name="豆瓣酱")
    missing = Problem.error(Path("catalog.toml"), None, missing_text)
    assert problem_block([problem, missing], Lang.ZH) == (
        f"  {mapo}，食材 3",
        "    未知食材“豆瓣酱”。",
        "  catalog.toml",
        "    文件不存在。",
    )
    assert problem_block([], Lang.EN) == ()
    english = problem_block([problem, missing], Lang.EN)
    assert english == (
        f"  {mapo}, ingredient 3",
        '    Unknown ingredient "豆瓣酱".',
        "  catalog.toml",
        "    The file is missing.",
    )
    chinese = problem_block(iter([missing, problem]), Lang.ZH)
    assert chinese == (
        "  catalog.toml",
        "    文件不存在。",
        f"  {mapo}，食材 3",
        "    未知食材“豆瓣酱”。",
    )
    rice = Path("recipes", "rice.toml")
    text = Message("No English steps.", "没有英文步骤。")
    warning = Problem.warning(rice, BiText("steps", "步骤"), text)
    assert problem_block((item for item in [warning]), Lang.EN) == (
        f"  {rice}, steps",
        "    No English steps.",
    )
    assert not any("\n" in line for line in (*english, *chinese))
