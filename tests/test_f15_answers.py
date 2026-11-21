"""Tests of F15 for the answers to the ID, the names, the servings, and the tags (T10 to T13)."""

from pathlib import Path

from f05_support import make_home
from f05_texts import lines_text
from f07_texts import Prob
from f09_support import folder_x, no_tags, one_tag
from f13_support import pristine
from f14_texts import no_tags_text, no_tags_text_zh, one_tag_text, one_tag_text_zh, tags, tags_zh
from f15_blocks import BASE_FILE, BASE_NAME_LINE
from f15_support import add, answers, fresh, listing, recipe_names
from f15_texts import (
    EN_NAME_PROMPT,
    ID_PROMPT,
    NAME_NEEDED,
    SERVINGS_WRONG,
    TAGS_PROMPT,
    ZH_NAME_PROMPT,
    base_out,
    block,
    id_exists,
    no_en_name,
    no_zh_name,
    not_an_id,
    pick,
    recipe_path,
    rounds,
    saved_with_problems,
    servings_prompt,
)
from recipe_menu.datafile import DataFolder

WRONG_IDS = [
    "Tomato-Egg",
    "TOMATO-EGG",
    "tomato egg",
    "tomato_egg",
    "-tomato",
    "rice.",
    "a/b",
    "a\\b",
    "a:b",
    "番茄炒蛋",
    "\uff54omato-egg",
    "con",
    "nul",
    "lpt9",
]
WRONG_SERVINGS = [
    "0",
    "00",
    "101",
    "two",
    "2.5",
    "-1",
    "+3",
    "3 份",
    "\uff13",
    "\u0663",
    "1_0",
    "1e2",
    "1" * 5000,
]


def _read(folder: DataFolder, recipe_id: str = "new-dish") -> bytes:
    """Reads the file of a recipe."""
    return folder.recipe_file(recipe_id).read_bytes()


def test_f15_t10_a_wrong_id_is_asked_again_and_a_right_id_goes_on(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Four lines: wrong IDs, the Chinese message, a folder, and a right ID after a wrong one."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    result = add(home, example_folder, [*WRONG_IDS, ""])
    lines = rounds(ID_PROMPT[0], *((value, not_an_id(value)[0]) for value in WRONG_IDS))
    assert result == (0, lines_text(*lines, ID_PROMPT[0]), "")
    assert recipe_names(example_folder) == listing()
    zh = add(home, fresh(source, tmp_path, "zh"), ["Tomato-Egg", ""], "--lang", "zh")
    wrong = not_an_id("Tomato-Egg")[1]
    assert zh == (0, lines_text(ID_PROMPT[1] + "Tomato-Egg", wrong, ID_PROMPT[1]), "")
    crowded = fresh(source, tmp_path, "crowded", folder_x)
    result = add(home, crowded, ["x", ""])
    lines = [ID_PROMPT[0] + "x", id_exists("x")[0], ID_PROMPT[0]]
    assert result == (0, lines_text(*lines), "")
    assert list((crowded.root / "recipes" / "x.toml").iterdir()) == []
    after = fresh(source, tmp_path, "after")
    result = add(home, after, ["Tomato-Egg", *answers("tomato-egg-2")])
    lines = [ID_PROMPT[0] + "Tomato-Egg", not_an_id("Tomato-Egg")[0]]
    lines += base_out(after, recipe_id="tomato-egg-2")
    assert result == (0, lines_text(*lines), "")
    assert _read(after, "tomato-egg-2") == BASE_FILE.encode("utf-8")
    assert _read(after, "tomato-egg") == _read(source, "tomato-egg")


def _problem_tail(folder: DataFolder, zh: bool, *problems: Prob) -> list[str]:
    """Gives the line after saving with one warning, and its block, for a recipe."""
    path = recipe_path(folder)
    return [pick(saved_with_problems(path, 0, 1), zh), *block(zh, *problems)]


def test_f15_t11_either_name_may_stay_empty_when_the_other_has_text(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Five lines: no Chinese name, no English name, an empty name asked again, and spaces."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    zh_less = BASE_FILE.replace(BASE_NAME_LINE, 'name = { en = "New dish" }').encode("utf-8")
    first = fresh(source, tmp_path, "first")
    expected = base_out(
        first,
        zh_name=[ZH_NAME_PROMPT[0]],
        tail=_problem_tail(first, False, no_zh_name()),
    )
    result = add(home, first, answers(zh_name=""))
    assert result == (0, lines_text(*expected), "")
    assert _read(first) == zh_less
    second = fresh(source, tmp_path, "second")
    expected = base_out(
        second,
        en_name=[EN_NAME_PROMPT[0]],
        tail=_problem_tail(second, False, no_en_name()),
    )
    assert add(home, second, answers(en_name="")) == (0, lines_text(*expected), "")
    assert _read(second) == BASE_FILE.replace(BASE_NAME_LINE, 'name = { zh = "新菜" }').encode()
    for zh, name in ((False, "third"), (True, "fourth")):
        folder = fresh(source, tmp_path, name)
        asked = rounds(
            EN_NAME_PROMPT[zh],
            ("", NAME_NEEDED[zh]),
            ("\u3000", NAME_NEEDED[zh]),
            "New dish",
        )
        expected = base_out(
            folder,
            zh,
            zh_name=[ZH_NAME_PROMPT[zh]],
            en_name=asked,
            tail=_problem_tail(folder, zh, no_zh_name()),
        )
        extra = ("--lang", "zh") if zh else ()
        result = add(home, folder, answers(zh_name="", en_name=["", "\u3000", "New dish"]), *extra)
        assert result == (0, lines_text(*expected), "")
        assert _read(folder) == zh_less
    spaced = fresh(source, tmp_path, "spaced")
    names = {"zh_name": "\u3000新菜 ", "en_name": " New  dish\t"}
    expected = base_out(
        spaced,
        zh_name=[ZH_NAME_PROMPT[0] + names["zh_name"]],
        en_name=[EN_NAME_PROMPT[0] + names["en_name"]],
    )
    assert add(home, spaced, answers(**names)) == (0, lines_text(*expected), "")
    spaced_name = 'name = { zh = "新菜", en = "New  dish" }'
    assert _read(spaced) == BASE_FILE.replace(BASE_NAME_LINE, spaced_name).encode("utf-8")


def test_f15_t12_the_servings_are_whole_numbers_from_1_to_100(
    example_folder: DataFolder, tmp_path: Path, default_int_limit: None
) -> None:
    """Three lines: every wrong answer, an empty answer, and the right answers at the ends."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    first = fresh(source, tmp_path, "first")
    prompt = servings_prompt()[0]
    asked = rounds(prompt, *((value, SERVINGS_WRONG[0]) for value in WRONG_SERVINGS), "03")
    expected = base_out(first, servings=asked)
    result = add(home, first, answers(servings=[*WRONG_SERVINGS, "03"]))
    assert result == (0, lines_text(*expected), "")
    assert _read(first) == BASE_FILE.replace("servings = 2", "servings = 3").encode("utf-8")
    second = fresh(source, tmp_path, "second")
    asked = rounds(servings_prompt()[1], ("two", SERVINGS_WRONG[1]), "")
    expected = base_out(second, True, servings=asked)
    result = add(home, second, answers(servings=["two", ""]), "--lang", "zh")
    assert result == (0, lines_text(*expected), "")
    assert _read(second) == BASE_FILE.encode("utf-8")
    third = fresh(source, tmp_path, "third")
    runs = (("d-1", "1", 1), ("d-100", "100", 100), ("d-0100", "0100", 100), ("d-7", " 7\t", 7))
    for recipe_id, typed, servings in runs:
        code, out, error = add(home, third, answers(recipe_id, servings=typed))
        assert (code, error) == (0, "")
        assert out.split("\n")[-2:-1] == base_out(third, recipe_id=recipe_id)[-1:]
        data = BASE_FILE.replace("servings = 2", f"servings = {servings}").encode("utf-8")
        assert _read(third, recipe_id) == data


def _tags_run(
    home: Path,
    folder: DataFolder,
    typed: str | list[str],
    shown: list[str],
    tags_line: str,
    *,
    zh: bool = False,
    recipe_id: str = "new-dish",
) -> None:
    """Runs ``add`` with BASE and tags, and checks the output, the error stream, and the file."""
    extra = ("--lang", "zh") if zh else ()
    result = add(home, folder, answers(recipe_id, tags=typed), *extra)
    expected = base_out(folder, zh, recipe_id, tags=shown)
    assert result == (0, lines_text(*expected), "")
    data = BASE_FILE.replace('tags = ["quick"]', tags_line).encode("utf-8")
    assert _read(folder, recipe_id) == data


def test_f15_t13_the_tags_are_split_found_by_either_name_and_kept_once(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Eight lines: the commas, the spaces, the case, the empty answers, and the messages."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    first = fresh(source, tmp_path, "first")
    prompt = TAGS_PROMPT[0]
    for number, typed in enumerate(("快手, 素", "快手，素", "快手、素"), 1):
        shown = rounds(prompt, typed)
        _tags_run(home, first, typed, shown, 'tags = ["快手", "素"]', recipe_id=f"t-{number}")
    spaced = " quick ,vegetarian, "
    second = fresh(source, tmp_path, "second")
    _tags_run(home, second, spaced, [prompt + spaced], 'tags = ["quick", "vegetarian"]')
    mixed = "QUICK, 快手, quick, Vegetarian"
    third = fresh(source, tmp_path, "third")
    _tags_run(home, third, mixed, [prompt + mixed], 'tags = ["QUICK", "Vegetarian"]')
    fourth = fresh(source, tmp_path, "fourth")
    _tags_run(home, fourth, "", [prompt], "tags = []", recipe_id="t-4")
    _tags_run(home, fourth, " , ，、", [prompt + " , ，、"], "tags = []", recipe_id="t-5")
    fifth = fresh(source, tmp_path, "fifth")
    pairs = [
        ("breakfast", tags("breakfast")),
        ("quick, breakfast, lunch", tags("breakfast")),
        ("快手; 素", tags("快手; 素")),
        ("home style", tags("home style")),
    ]
    shown = rounds(prompt, *pairs, "quick")
    typed = [*(value for value, _ in pairs), "quick"]
    _tags_run(home, fifth, typed, shown, 'tags = ["quick"]')
    sixth = fresh(source, tmp_path, "sixth")
    shown = rounds(TAGS_PROMPT[1], ("breakfast", tags_zh("breakfast")), "素")
    _tags_run(home, sixth, ["breakfast", "素"], shown, 'tags = ["素"]', zh=True)
    _check_one_and_no_tags(home, source, tmp_path)


def _check_one_and_no_tags(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Lines 7 and 8: a catalog with one tag, and a catalog with no tags."""
    for name, change, answers_typed, messages, line in (
        ("one", one_tag, ["素", "quick"], (one_tag_text("素"), one_tag_text_zh("素")), None),
        ("none", no_tags, ["quick", ""], (no_tags_text("quick"), no_tags_text_zh("quick")), "[]"),
    ):
        for zh in (False, True):
            folder = fresh(source, tmp_path, f"{name}-{zh}", change)
            first, last = answers_typed
            shown = rounds(TAGS_PROMPT[zh], (first, messages[zh]), last)
            tags_line = 'tags = ["quick"]' if line is None else "tags = []"
            _tags_run(home, folder, answers_typed, shown, tags_line, zh=zh)
