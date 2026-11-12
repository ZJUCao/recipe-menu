"""Tests of F05 for main: the exit codes 0, 1, 2, and 130, other exceptions, and commands.

These are T39 to T43.
"""

import io
from collections.abc import Sequence
from pathlib import Path

import pytest

from f05_support import (
    TODAY,
    VERSION_LINE,
    Recorder,
    StandIns,
    go,
    in_folder,
    make_command,
    make_home,
)
from f05_texts import COMMANDS_EN, COMMANDS_ZH, err_result
from recipe_menu.app import Arguments, Command, Context, UsageError
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder
from recipe_menu.text import RUN_HELP_FOR_COMMANDS, Message

NOT_A_WEEK = Message('"{week}" is not a week.', "“{week}”不是一个周。")
HELP = Message("Show one recipe.", "查看一个菜谱。")


def run(context: Context, arguments: Arguments) -> int:
    """Stands in for the run of a command."""
    return 0


def test_f05_t39_main_gives_the_code_of_run_and_adds_no_output(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """A command writes its output and its message itself, and cli adds nothing."""
    home = make_home(tmp_path)
    env = in_folder(example_folder.root)

    def to_out(context: Context) -> None:
        """Writes the output of the command."""
        context.out.write("共 7 个菜谱。\n")

    def to_err(context: Context) -> None:
        """Writes the message that ends the command."""
        context.err.write('There is no recipe "x".\n')

    result, _ = go(home, "list", environ=env, behave={"LIST": Recorder(0, to_out)})
    assert result == (0, "共 7 个菜谱。\n", "")
    result, _ = go(home, "show", "x", environ=env, behave={"SHOW": Recorder(1, to_err)})
    assert result == (1, "", 'There is no recipe "x".\n')


def test_f05_t40_a_usage_error_of_a_command_gives_code_2_with_its_own_hint(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """The error text, and then the hint when the error has one, in the language of the line."""
    home = make_home(tmp_path)
    env = in_folder(example_folder.root)

    def without_hint(context: Context) -> None:
        """Raises a usage error that names no hint."""
        raise UsageError(NOT_A_WEEK, None, week="2026-W99")

    def with_hint(context: Context) -> None:
        """Raises a usage error that names a hint."""
        raise UsageError(NOT_A_WEEK, RUN_HELP_FOR_COMMANDS, week="2026-W99")

    line = ("menu", "show", "2026-W99")
    cases = [
        (without_hint, (), err_result(2, '"2026-W99" is not a week.')),
        (without_hint, ("--lang", "zh"), err_result(2, "“2026-W99”不是一个周。")),
        (with_hint, (), err_result(2, '"2026-W99" is not a week.', COMMANDS_EN)),
        (with_hint, ("--lang", "zh"), err_result(2, "“2026-W99”不是一个周。", COMMANDS_ZH)),
    ]
    for action, extra, expected in cases:
        result, _ = go(home, *line, *extra, environ=env, behave={"MENU_SHOW": Recorder(0, action)})
        assert result == expected, extra


def test_f05_t41_ctrl_c_in_run_gives_130_and_nothing_more(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """A KeyboardInterrupt in run gives 130, and the output so far stays."""
    home = make_home(tmp_path)

    def interrupt(context: Context) -> None:
        """Writes some output and then raises a KeyboardInterrupt."""
        context.out.write("partial\n")
        raise KeyboardInterrupt

    result, _ = go(
        home,
        "list",
        environ=in_folder(example_folder.root),
        behave={"LIST": Recorder(0, interrupt)},
    )
    assert result == (130, "partial\n", "")


def test_f05_t42_other_exceptions_go_on_to_python(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """A bug in a command is not caught, and neither is an error of a console stream."""
    home = make_home(tmp_path)
    env = in_folder(example_folder.root)
    for error in (RuntimeError("bug"), ValueError("bug"), OSError("bug")):

        def fail(context: Context, error: Exception = error) -> None:
            """Raises the error of the loop."""
            raise error

        with pytest.raises(type(error), match="bug"):
            go(home, "list", environ=env, behave={"LIST": Recorder(0, fail)})
    closed = io.StringIO()
    closed.close()
    with pytest.raises(ValueError):
        main(
            ["--version"],
            environ={},
            home=home,
            today=TODAY,
            stdout=closed,
            stderr=io.StringIO(),
            commands=StandIns().commands,
        )


def _call(home: Path, argv: Sequence[str], commands: Sequence[Command]) -> tuple[int, str, str]:
    """Calls ``main`` with new streams and gives the result, or raises what it raises."""
    out, err = io.StringIO(), io.StringIO()
    code = main(argv, environ={}, home=home, today=TODAY, stdout=out, stderr=err, commands=commands)
    return code, out.getvalue(), err.getvalue()


def test_f05_t43_commands_that_break_the_constraint_raise_value_error(tmp_path: Path) -> None:
    """The check comes before the arguments are read, so nothing is written."""
    home = make_home(tmp_path)
    menu = Command(("menu",), Message("Plan the week.", "安排一周。"), run)
    menu_new = make_command("MENU_NEW", run)
    again = Command(("menu", "new"), Message("Make a menu.", "新建菜单。"), run)
    lists = Command(("lists",), HELP, run)
    wrong = [
        (["--version"], [make_command("LIST", run), make_command("LIST", run)]),
        (["--help"], [menu_new, again]),
        (["--version"], [menu, make_command("MENU_SHOW", run)]),
        (["list", "--lang", "fr"], [make_command("MENU_SHOW", run), menu]),
    ]
    for argv, commands in wrong:
        out, err = io.StringIO(), io.StringIO()
        with pytest.raises(ValueError):
            main(
                argv,
                environ={},
                home=home,
                today=TODAY,
                stdout=out,
                stderr=err,
                commands=commands,
            )
        assert out.getvalue() == ""
        assert err.getvalue() == ""
    right = [
        [make_command("SHOW", run), make_command("MENU_SHOW", run)],
        [make_command("LIST", run), lists],
        [],
        list(StandIns().commands),
    ]
    for commands in right:
        assert _call(home, ["--version"], commands) == (0, VERSION_LINE, "")
