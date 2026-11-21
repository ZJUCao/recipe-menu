"""Tests of F15 for how add reads an answer: the prompt, the echo, the end, Ctrl+C (T17, T18)."""

import io
from datetime import date
from pathlib import Path

import pytest

from f05_support import make_home
from f05_texts import lines_text
from f08_support import CTRL_C, rule
from f13_support import pristine
from f15_blocks import BASE_FILE
from f15_support import (
    BASE,
    FlushOut,
    RecordingIn,
    Stopping,
    add,
    fresh,
    listing,
    recipe_names,
    terminal,
    traced_add,
)
from f15_texts import (
    EN_NAME_PROMPT,
    EN_STEPS_OPTIONAL_PROMPT,
    ID_PROMPT,
    INGREDIENTS_PROMPT,
    INPUT_ENDED,
    TAGS_PROMPT,
    ZH_NAME_PROMPT,
    ZH_STEPS_PROMPT,
    answer_cut,
    base_out,
    id_exists,
    recipe_path,
    saved,
    servings_prompt,
)
from recipe_menu.app import Arguments, Context
from recipe_menu.commands.add import ADD_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings

PROMPTS_ONLY = [ID_PROMPT[0], ZH_NAME_PROMPT[0], EN_NAME_PROMPT[0], servings_prompt()[0]]


def _check_terminal(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Lines 3 to 6: the streams whose ``isatty()`` gives true."""
    first = fresh(source, tmp_path, "terminal")
    spaces = "  "
    expected = "".join(
        [
            *PROMPTS_ONLY,
            TAGS_PROMPT[0],
            INGREDIENTS_PROMPT[0] + "\n",
            spaces * 2,
            ZH_STEPS_PROMPT[0] + "\n",
            spaces * 2,
            EN_STEPS_OPTIONAL_PROMPT[0] + "\n",
            spaces * 2,
            saved(recipe_path(first))[0] + "\n",
        ]
    )
    assert add(home, first, terminal(BASE)) == (0, expected, "")
    assert first.recipe_file("new-dish").read_bytes() == BASE_FILE.encode("utf-8")
    second = fresh(source, tmp_path, "terminal-exists")
    exists = ID_PROMPT[0] + id_exists("tomato-egg")[0] + "\n" + ID_PROMPT[0]
    assert add(home, second, terminal(["tomato-egg", ""])) == (0, exists, "")
    third = fresh(source, tmp_path, "terminal-ended")
    ended = (1, ID_PROMPT[0] + ZH_NAME_PROMPT[0] + EN_NAME_PROMPT[0], INPUT_ENDED[0] + "\n")
    assert add(home, third, terminal(BASE[:2])) == ended
    assert add(home, third, terminal([])) == (0, ID_PROMPT[0], "")
    assert recipe_names(third) == listing()


def _check_flush(source: DataFolder, tmp_path: Path) -> None:
    """Line 7: the output stream is flushed before each read, and each read ends in its prompt."""
    folder = fresh(source, tmp_path, "flush")
    out, err = FlushOut(), io.StringIO()
    answers = RecordingIn(BASE, out)
    context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10), input=answers)
    assert len(answers.seen) == 0
    assert ADD_COMMAND.run(context, Arguments()) == 0
    assert len(answers.seen) == 11
    prompts = [*PROMPTS_ONLY, TAGS_PROMPT[0], *["  "] * 6]
    for (text, flushed), prompt in zip(answers.seen, prompts, strict=True):
        assert text == flushed
        assert text.endswith(prompt)
    assert folder.recipe_file("new-dish").read_bytes() == BASE_FILE.encode("utf-8")


def test_f15_t17_add_writes_a_prompt_flushes_it_and_reads_one_line(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven lines: the end after each answer, Chinese, the terminal, and the flush record."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    first = fresh(source, tmp_path, "first")
    for given in range(1, 11):
        lines, prompt = answer_cut(first, given)
        result = add(home, first, BASE[:given])
        assert result == (1, lines_text(*lines, prompt), lines_text(INPUT_ENDED[0])), given
    assert recipe_names(first) == listing()
    lines, prompt = answer_cut(first, 4, True)
    result = add(home, first, BASE[:4], "--lang", "zh")
    assert result == (1, lines_text(*lines, prompt), lines_text(INPUT_ENDED[1]))
    assert prompt == "标签，用逗号分隔："
    _check_terminal(home, source, tmp_path)
    _check_flush(source, tmp_path)


def test_f15_t18_ctrl_c_leaves_no_file_and_gives_130(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Four lines: Ctrl+C at five questions, a direct call, and Ctrl+C while the file is written."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    first = fresh(source, tmp_path, "first")
    for stop in (1, 2, 6, 8, 11):
        lines, prompt = answer_cut(first, stop - 1)
        result = add(home, first, Stopping(BASE, stop))
        assert result == (130, lines_text(*lines) + prompt, ""), stop
    assert recipe_names(first) == listing()
    second = fresh(source, tmp_path, "second")
    out, err = io.StringIO(), io.StringIO()
    stopped = Stopping(BASE, 3)
    context = Context(Lang.EN, second, Settings(), out, err, date(2026, 11, 10), input=stopped)
    with pytest.raises(KeyboardInterrupt):
        ADD_COMMAND.run(context, Arguments())
    for rules, name in (("write", "third"), ("close", "fourth")):
        folder = fresh(source, tmp_path, name)
        stop_rule = rule(rules, folder.recipe_file("new-dish"), CTRL_C)
        result, calls, _ = traced_add(home, folder, BASE, stop_rule)
        expected = lines_text(*base_out(folder, tail=[]))
        assert result == (130, expected, "")
        assert "unlink recipes/new-dish.toml" in calls
        assert recipe_names(folder) == listing()
