"""Tests of F04 for is_recipe_id and list_recipe_ids (T06 to T13)."""

import shutil
import sys
from pathlib import Path

import pytest

from f04_support import (
    EXAMPLE_IDS,
    M_FOLDER_IS_FILE,
    M_FOLDER_MISSING,
    M_NOT_A_RECIPE_ID,
    M_RESERVED_ID,
    M_TOML_ENDING,
    check_problems,
    dish_text,
    err,
    put_bytes,
    touch,
    write,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.recipes import is_recipe_id, list_recipe_ids

ACCEPTED = (
    "tomato-egg",
    "2-minute-noodles",
    "choy-sum",
    "a",
    "0",
    "9a",
    "a-",
    "a--b",
    "abcdefghijklmnopqrstuvwxyz0123456789-",
    "a" * 300,
)

REJECTED = (
    "",
    ".",
    "..",
    "rice.",
    "nul.v2",
    "a/b",
    "a\\b",
    "a:b",
    "a\x00",
    "a*b",
    "a?b",
    "a<b",
    "Tomato-Egg",
    "tomato egg",
    "tomato_egg",
    "-tomato",
    "番茄炒蛋",
    "tomato\u2010egg",
    "\uff54omato-egg",
    "tomato-egg\u200b",
    "a>b",
    'a"b',
    "a\x7cb",
    "a\x01b",
    "a\x1f",
    "a\t",
    "a\x7f",
    "tomato-egg ",
    " tomato-egg",
    "tomato\u3000egg",
    "tOMATO",
    "-",
    "tomato\u2011egg",
    "\ufefftomato-egg",
    "\u212aale",
    "\u017fcallion",
    "caf\u00e9",
    "cafe\u0301",
    "a\u00b2",
    "\u0661",
    "\uff11",
    "\ud800",
)


def test_f04_t06_names_that_follow_the_rules_are_recipe_ids() -> None:
    """The rules set no length."""
    for text in ACCEPTED:
        assert is_recipe_id(text) is True, text


def test_f04_t07_names_that_break_rules_1_to_3_are_not_recipe_ids() -> None:
    """Forbidden characters, whitespace, capitals, and look-alike characters give False."""
    for text in REJECTED:
        assert is_recipe_id(text) is False, text


def test_f04_t08_windows_device_names_are_not_recipe_ids() -> None:
    """A name that only starts like a device name is an ID. Capitals fail by rule 2."""
    devices = ("con", "prn", "aux", "nul", "com0", "com1", "com9", "lpt0", "lpt1", "lpt9")
    for text in (*devices, "NUL", "Con", "COM1"):
        assert is_recipe_id(text) is False, text
    for text in ("com10", "lpt10", "console", "conn", "auxiliary", "nul-1", "com", "lpt"):
        assert is_recipe_id(text) is True, text


def test_f04_t09_the_example_data_gives_its_seven_ids_and_the_folder_problems(
    example_folder: DataFolder,
) -> None:
    """A capital ending, a name that is no ID, and a missing folder give their problems."""
    assert list_recipe_ids(example_folder) == (EXAMPLE_IDS, ())
    write(example_folder.recipes / "notes.txt", "Ideas\n")
    touch(example_folder.recipes, "pancakes.TOML", "Rice Bowl.toml")
    ids, problems = list_recipe_ids(example_folder)
    assert ids == EXAMPLE_IDS
    check_problems(
        problems,
        [
            err(None, M_TOML_ENDING, "recipes/pancakes.TOML"),
            err(None, M_NOT_A_RECIPE_ID, "recipes/Rice Bowl.toml"),
        ],
    )
    shutil.rmtree(example_folder.recipes)
    ids, problems = list_recipe_ids(example_folder)
    assert ids == ()
    check_problems(problems, [err(None, M_FOLDER_MISSING, "recipes")])


def test_f04_t10_ids_sort_by_code_point_and_no_file_is_read(folder: DataFolder) -> None:
    """``-`` comes before digits and digits before letters, and a folder counts."""
    put_bytes(folder.recipes / "b.toml", b"\xff")
    names = ("a9", "a10", "a", "a-b", "aa", "0-a", "a0")
    touch(folder.recipes, *(f"{name}.toml" for name in names))
    (folder.recipes / "c.toml").mkdir()
    ids, problems = list_recipe_ids(folder)
    assert ids == ("0-a", "a", "a-b", "a0", "a10", "a9", "aa", "b", "c")
    assert problems == ()


def test_f04_t11_names_that_break_the_rule_give_not_a_recipe_id(folder: DataFolder) -> None:
    """The problems come in the code point order of the names, after the ending problems."""
    names = (
        "tomato-egg.toml",
        "Tomato-Eggs.toml",
        "tomato egg.toml",
        "tomato_egg.toml",
        "-tomato.toml",
        "rice..toml",
        ".toml",
        "番茄炒蛋.toml",
        "tomato-egg\u200b.toml",
        "rice.Toml",
        "notes.txt",
        "rice.toml.bak",
        "toml",
    )
    touch(folder.recipes, *names)
    write(folder.recipes / "drafts" / "stew.toml", "")
    ids, problems = list_recipe_ids(folder)
    assert ids == ("tomato-egg",)
    bad = (
        ".toml",
        "-tomato.toml",
        "Tomato-Eggs.toml",
        "rice..toml",
        "tomato egg.toml",
        "tomato-egg\u200b.toml",
        "tomato_egg.toml",
        "番茄炒蛋.toml",
    )
    expected = [err(None, M_TOML_ENDING, "recipes/rice.Toml")]
    expected += [err(None, M_NOT_A_RECIPE_ID, f"recipes/{name}") for name in bad]
    check_problems(problems, expected)


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows may open the console device for con.toml, and a folder there cannot hold "
    "CON.toml and con.toml side by side. CI runs this case on Linux.",
)
def test_f04_t12_a_device_name_gives_reserved_recipe_id(folder: DataFolder) -> None:
    """Only a name that is exactly a device name of rule 4 gets RESERVED_RECIPE_ID."""
    names = (
        "con",
        "CON",
        "prn",
        "aux",
        "nul",
        "nul.v2",
        "com0",
        "com9",
        "lpt1",
        "com10",
        "console",
    )
    touch(folder.recipes, *(f"{name}.toml" for name in names))
    ids, problems = list_recipe_ids(folder)
    assert ids == ("com10", "console")
    expected = [
        err(None, M_NOT_A_RECIPE_ID, "recipes/CON.toml"),
        *(err(None, M_RESERVED_ID, f"recipes/{n}.toml") for n in ("aux", "com0", "com9", "con")),
        err(None, M_RESERVED_ID, "recipes/lpt1.toml"),
        err(None, M_RESERVED_ID, "recipes/nul.toml"),
        err(None, M_NOT_A_RECIPE_ID, "recipes/nul.v2.toml"),
        err(None, M_RESERVED_ID, "recipes/prn.toml"),
    ]
    check_problems(problems, expected)


def test_f04_t13_a_folder_that_cannot_be_listed_gives_one_problem(
    folder: DataFolder, tmp_path: Path
) -> None:
    """A missing folder, a file, and a folder below a file give the problem of the listing."""
    ids, problems = list_recipe_ids(folder)
    assert ids == ()
    check_problems(problems, [err(None, M_FOLDER_MISSING, "recipes")], 1)
    write(folder.recipes, dish_text())
    ids, problems = list_recipe_ids(folder)
    assert ids == ()
    check_problems(problems, [err(None, M_FOLDER_IS_FILE, "recipes")], 2)
    write(tmp_path / "data.txt", "x\n")
    ids, problems = list_recipe_ids(DataFolder(tmp_path / "data.txt"))
    assert ids == ()
    check_problems(problems, [err(None, M_FOLDER_MISSING, "recipes")], 3)
