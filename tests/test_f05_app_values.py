"""Tests of F05 for Command, Arguments, and UsageError (T13 to T17)."""

import pytest

from f05_support import make_command
from f05_texts import EN, OPTIONS_EN, OPTIONS_ZH, ZH
from recipe_menu.app import Argument, Arguments, Command, Context, FolderUse, UsageError
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal
from recipe_menu.text import RUN_HELP_FOR_OPTIONS, Message

HELP = Message("Show one recipe.", "查看一个菜谱。")
LANG_NOT_EN_OR_ZH = Message(
    '--lang must be en or zh, not "{lang}".',
    "--lang 必须是 en 或 zh，不能是“{lang}”。",
)
NOT_A_WEEK = Message('"{week}" is not a week.', "“{week}”不是一个周。")


def run(context: Context, arguments: Arguments) -> int:
    """Stands in for the run of a command."""
    return 0


def test_f05_t13_usage_gives_the_words_and_the_form_of_the_argument() -> None:
    """The usage of each form of an argument, and the folder use of a command."""
    menu_show = make_command("MENU_SHOW", run)
    search = make_command("SEARCH", run)
    init = make_command("INIT", run)
    assert menu_show.usage == BiText("menu show [WEEK]", "menu show [周]")
    assert search.usage == BiText("search WORD...", "search 词...")
    assert init.usage == BiText("init", "init")
    show = Command(("show",), HELP, run, Argument(Message("ID", "ID")), ("--servings",))
    assert show.usage == BiText("show ID", "show ID")
    tag = Argument(Message("TAG", "标签"), required=False, repeats=True)
    assert Command(("tags",), HELP, run, tag).usage == BiText("tags [TAG...]", "tags [标签...]")
    assert Command(("menu", "new"), HELP, run).usage == BiText("menu new", "menu new")
    assert menu_show.folder is FolderUse.READ
    assert init.folder is FolderUse.CREATE


def test_f05_t14_command_checks_its_words_help_argument_and_options() -> None:
    """Good values raise nothing, equal commands have equal hashes, and bad values raise."""
    for words in [("show",), ("menu", "show"), ("a",), ("z",)]:
        Command(words, HELP, run)
    for options in [("--tag",), ("--servings", "--tag"), ("--t",), ("--dry-run",)]:
        Command(("show",), HELP, run, options=options)
    first = Command(("show",), HELP, run, options=("--tag",))
    second = Command(("show",), HELP, run, options=("--tag",))
    assert first == second
    assert hash(first) == hash(second)
    bad_words = [
        (),
        ("menu", "show", "all"),
        ("Show",),
        ("show-all",),
        ("show2",),
        ("",),
        ("sh ow",),
        ("caf\u00e9",),
        ("\uff53how",),
    ]
    for words in bad_words:
        with pytest.raises(ValueError):
            Command(words, HELP, run)
    with pytest.raises(ValueError):
        Command(("show",), Message("Show {id}.", "查看 {id}。"), run)
    with pytest.raises(ValueError):
        Command(("show",), HELP, run, Argument(Message("{name}", "{name}")))
    bad_options = [
        ("-s",),
        ("tag",),
        ("--lang",),
        ("--data",),
        ("--help",),
        ("--version",),
        ("--tag", "--tag"),
        ("--Tag",),
        ("--",),
        ("---tag",),
        ("--1",),
        ("--tag2",),
        ("--tag_name",),
        ("--tag=",),
        ("--t\u00e4g",),
    ]
    for options in bad_options:
        with pytest.raises(ValueError):
            Command(("show",), HELP, run, options=options)


def test_f05_t15_arguments_give_options_sorted_and_reject_a_name_twice() -> None:
    """The design's example: option, the sort of the pairs, and a name given twice."""
    arguments = Arguments(("番茄", "quick"), (("--tag", "素"),))
    assert arguments.values == ("番茄", "quick")
    assert arguments.option("--tag") == "素"
    assert arguments.option("--servings") is None
    both = Arguments((), (("--tag", "素"), ("--servings", "4")))
    assert both.options == (("--servings", "4"), ("--tag", "素"))
    three = Arguments((), (("--week", "next"), ("--tag", "素"), ("--servings", "4")))
    assert three.options == (("--servings", "4"), ("--tag", "素"), ("--week", "next"))
    assert arguments.option("--lang") is None
    assert arguments.option("tag") is None
    assert Arguments() == Arguments((), ())
    with pytest.raises(ValueError):
        Arguments((), (("--tag", "a"), ("--tag", "b")))
    with pytest.raises(ValueError):
        Arguments((), (("--tag", "a"), ("--tag", "a")))


def test_f05_t16_usage_error_keeps_its_message_hint_and_values() -> None:
    """The design's example: text in both languages, str, positional-only names, and values."""
    error = UsageError(LANG_NOT_EN_OR_ZH, RUN_HELP_FOR_OPTIONS, lang="fr")
    assert error.text(EN) == '--lang must be en or zh, not "fr".'
    assert error.text(ZH) == "--lang 必须是 en 或 zh，不能是“fr”。"
    assert error.hint is RUN_HELP_FOR_OPTIONS
    assert error.message is LANG_NOT_EN_OR_ZH
    assert str(error) == '--lang must be en or zh, not "fr".'
    assert RUN_HELP_FOR_OPTIONS.render(EN) == OPTIONS_EN
    assert RUN_HELP_FOR_OPTIONS.render(ZH) == OPTIONS_ZH
    week = UsageError(NOT_A_WEEK, None, week="2026-W99")
    assert week.hint is None
    assert week.values == (("week", "2026-W99"),)
    named = Message("{message}: {hint}", "{message}：{hint}")
    third = UsageError(named, None, message="a", hint="b")
    assert third.text(EN) == "a: b"
    assert third.text(ZH) == "a：b"
    counted = Message("{count} {tag}", "{count} 个“{tag}”")
    fourth = UsageError(counted, None, tag=BiText(zh="素"), count=3)
    assert fourth.values == (("count", 3), ("tag", BiText(zh="素")))
    assert fourth.text(EN) == "3 素"
    assert fourth.text(ZH) == "3 个“素”"
    with pytest.raises(UsageError) as caught:
        raise error
    assert caught.value is error
    assert isinstance(error, Exception)


@pytest.mark.usefixtures("default_int_limit")
def test_f05_t17_usage_error_rejects_wrong_values_when_it_is_made() -> None:
    """Values that do not fit, a long int, and a hint with a placeholder raise ValueError."""
    with pytest.raises(ValueError):
        UsageError(NOT_A_WEEK, None)
    with pytest.raises(ValueError):
        UsageError(NOT_A_WEEK, None, week="2026-W99", year="2026")
    with pytest.raises(ValueError):
        UsageError(NOT_A_WEEK, NOT_A_WEEK, week="2026-W99")
    with pytest.raises(ValueError):
        UsageError(Message("{n}", "{n}"), None, n=10**4300)
    for value in (None, True, 1.5, Lang.ZH, Meal.DINNER):
        with pytest.raises(TypeError):
            UsageError(NOT_A_WEEK, None, week=value)  # type: ignore[arg-type]
