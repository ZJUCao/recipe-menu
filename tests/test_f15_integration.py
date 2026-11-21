"""Tests of F15 for the scenarios of v0.2 at ``main`` and for the real entry point (T25 to T27)."""

from pathlib import Path

import pytest

from f03_support import put_bytes
from f05_support import copy_example, make_home
from f05_texts import err_result, lines_text
from f07_support import snapshot
from f09_support import at
from f09_texts import RUN_HELP_COMMANDS
from f13_support import pristine
from f15_blocks import BASE_FILE, BASE_NAME_LINE, S09_FILE, S10_FILE
from f15_support import BASE, S09, S10, add, fresh, pipe_module
from f15_texts import (
    EN_NAME_PROMPT,
    ID_PROMPT,
    INPUT_ENDED,
    ZH_NAME_PROMPT,
    base_out,
    s09_out,
    s10_out,
)
from recipe_menu.datafile import DataFolder


def test_f15_t25_the_english_session_of_v02_s10_gives_one_message_for_each_wrong_answer(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The run of S10, its file, and ``show`` of the new recipe, as in a copy with the file."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    result = add(home, example_folder, S10)
    assert result == (0, lines_text(*s10_out(example_folder)), "")
    rice = example_folder.recipe_file("egg-fried-rice")
    assert rice.read_bytes() == S10_FILE.encode("utf-8")
    other = fresh(source, tmp_path, "other")
    put_bytes(other.recipe_file("egg-fried-rice"), S10_FILE.encode("utf-8"))
    shown = at(home, example_folder, "show", "egg-fried-rice")
    assert shown == at(home, other, "show", "egg-fried-rice")
    head = "Egg fried rice  蛋炒饭\nServings: 3   Tags: quick, staple\n"
    assert shown[0] == 0
    assert shown[1].startswith(head)
    assert shown[2] == ""


def test_f15_t26_add_creates_only_the_new_recipe_file(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The run of v0.2-S15 step 2: one new file, and every other file keeps its bytes and time."""
    home = make_home(tmp_path)
    folder = DataFolder(copy_example(example_folder, home / "recipe-menu"))
    (folder.root / "shopping").mkdir()
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    before_home, before_cwd = snapshot(home), snapshot(cwd)
    result = add(home, None, S09, "--lang", "zh")
    assert result == (0, lines_text(*s09_out(folder)), "")
    after_home = snapshot(home)
    new = "recipe-menu/recipes/garlic-broccoli.toml"
    assert set(after_home) - set(before_home) == {new}
    assert set(before_home) - set(after_home) == set()
    assert after_home[new][0] == S09_FILE.encode("utf-8")
    for name, held in before_home.items():
        if name == "recipe-menu/recipes":
            assert after_home[name][0] == held[0]
        else:
            assert after_home[name] == held, name
    assert snapshot(cwd) == before_cwd


def test_f15_t27_the_real_entry_point_reads_utf8_answers_from_a_pipe(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Five runs of ``python -m recipe_menu add`` with bytes on the pipe."""
    source = pristine(example_folder, tmp_path)
    first = fresh(source, tmp_path, "first")
    data = b"\xef\xbb\xbf" + b"".join(f"{answer}\r\n".encode() for answer in S09)
    result = pipe_module(tmp_path, data, "add", "--lang", "zh", "--data", str(first.root))
    assert result == (0, lines_text(*s09_out(first)), "")
    assert first.recipe_file("garlic-broccoli").read_bytes() == S09_FILE.encode("utf-8")
    second = fresh(source, tmp_path, "second")
    pieces = [answer.encode() for answer in BASE]
    pieces[1] = b"\xff" + "新菜".encode()
    data = b"".join(piece + b"\n" for piece in pieces)
    result = pipe_module(tmp_path, data, "add", "--data", str(second.root))
    broken = ZH_NAME_PROMPT[0] + "\ufffd新菜"
    assert result == (0, lines_text(*base_out(second, zh_name=[broken])), "")
    name = BASE_NAME_LINE.replace("新菜", "\ufffd新菜")
    expected = BASE_FILE.replace(BASE_NAME_LINE, name).encode("utf-8")
    assert second.recipe_file("new-dish").read_bytes() == expected
    third = fresh(source, tmp_path, "third")
    data = b"new-dish\n" + "新菜".encode() + b"\n"
    result = pipe_module(tmp_path, data, "add", "--data", str(third.root))
    shown = [ID_PROMPT[0] + "new-dish", ZH_NAME_PROMPT[0] + "新菜", EN_NAME_PROMPT[0]]
    assert result == (1, lines_text(*shown), lines_text(INPUT_ENDED[0]))
    fourth = fresh(source, tmp_path, "fourth")
    result = pipe_module(tmp_path, b"", "add", "--data", str(fourth.root))
    assert result == (0, lines_text(ID_PROMPT[0]), "")
    unexpected = 'Unexpected argument "garlic-broccoli". Write "recipe-menu add".'
    result = pipe_module(tmp_path, b"", "add", "garlic-broccoli", "--data", str(fourth.root))
    assert result == err_result(2, unexpected, RUN_HELP_COMMANDS[0])
