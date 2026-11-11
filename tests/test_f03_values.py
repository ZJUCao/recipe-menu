"""Tests of F03 for Category, Ingredient, Tag, and the lookups of Catalog (F03-T36 to F03-T47)."""

from collections.abc import Callable, Sequence

import pytest

from f03_support import (
    EN,
    choy_sum,
    find_catalog,
    fruit,
    greens,
    jalapeno,
    kale,
    meat,
    pork,
    produce,
    puree,
    quick,
    scallion,
    tomato,
    tomato_again,
    xo_sauce,
)
from recipe_menu.catalog import Catalog, Category, Ingredient, Tag
from recipe_menu.lang import BiText
from recipe_menu.units import Unit


def check_finds(
    find: Callable[[str], object], names: Sequence[str], wanted: Sequence[object]
) -> None:
    """Checks that each name finds the wanted object, by ``is``, or ``None``."""
    assert len(names) == len(wanted)
    for name, want in zip(names, wanted, strict=True):
        assert find(name) is want, name


def test_f03_t36_a_category_needs_a_key_and_a_name() -> None:
    """Each part that is set holds more than whitespace, and one language may be missing."""
    Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
    Category("other", BiText(zh="其他"))
    Category("other", BiText(en="Other"))
    Category(" produce ", BiText(" Vegetables ", "蔬菜"))
    assert Category("other", BiText(zh="其他")).name.get(EN) == "其他"
    for key in ["", " ", "\u3000", "\t\n"]:
        with pytest.raises(ValueError):
            Category(key, BiText("Other", "其他"))
    names = [
        BiText("", "其他"),
        BiText("Other", ""),
        BiText(" ", "其他"),
        BiText("Other", "\u3000"),
        BiText(en=""),
        BiText(zh="\t"),
    ]
    for name in names:
        with pytest.raises(ValueError):
            Category("other", name)


def test_f03_t37_an_ingredient_needs_both_names() -> None:
    """Each name holds more than whitespace, and the unit is ``None`` unless given."""
    stalk = Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK)
    plain = Ingredient(BiText("Tomato", "番茄"), produce)
    Ingredient(BiText("Tofu", "tofu"), produce)
    Ingredient(BiText("Cola", "可乐"), Category("other", BiText(zh="其他")))
    assert stalk.category is produce
    assert stalk.unit is Unit.STALK
    assert plain.unit is None
    names = [
        BiText(zh="葱"),
        BiText(en="Scallion"),
        BiText("", "葱"),
        BiText("Scallion", ""),
        BiText(" ", "葱"),
        BiText("Scallion", "\u3000"),
        BiText("\t", "\n"),
    ]
    for name in names:
        with pytest.raises(ValueError):
            Ingredient(name, produce)


def test_f03_t38_a_tag_needs_both_names() -> None:
    """Each name holds more than whitespace."""
    Tag(BiText("quick", "快手"))
    Tag(BiText("BBQ", "bbq"))
    assert Tag(BiText("quick", "快手")) == Tag(BiText("quick", "快手"))
    names = [
        BiText("quick", " "),
        BiText(zh="快手"),
        BiText(en="quick"),
        BiText("", "快手"),
        BiText("\u3000", "快手"),
    ]
    for name in names:
        with pytest.raises(ValueError):
            Tag(name)


def test_f03_t39_a_catalog_keeps_its_tuples_finds_by_name_and_compares_by_tuples() -> None:
    """Lookups change neither the equality nor the hash, and two categories may share a name."""
    c1 = Catalog((produce, meat), (tomato, pork), (quick,))
    c2 = Catalog((produce, meat), (tomato, pork), (quick,))
    assert c1.find_ingredient("五花肉") is pork
    assert c1.categories == (produce, meat)
    assert c1.ingredients == (tomato, pork)
    assert c1.tags == (quick,)
    assert c1 == c2
    assert hash(c1) == hash(c2)
    assert c1 != Catalog((produce, meat), (tomato,), (quick,))
    assert Catalog((produce, greens), (), ()).categories == (produce, greens)
    empty = Catalog((), (), ())
    assert empty.find_ingredient("番茄") is None
    assert empty.find_tag("quick") is None


def test_f03_t40_a_catalog_that_breaks_its_rules_is_a_wrong_call() -> None:
    """Matching keys, an unknown category, and matching names raise."""
    cherry = Ingredient(BiText("Cherry tomato", " 番茄 "), produce)
    sauce = Ingredient(BiText("番茄", "西红柿"), produce)
    spaced = Category(" produce\u3000", BiText("Fruit", "水果"))
    calls = [
        lambda: Catalog((produce,), (tomato, pork), ()),
        lambda: Catalog((), (tomato,), ()),
        lambda: Catalog((produce, fruit), (), ()),
        lambda: Catalog((produce, spaced), (), ()),
        lambda: Catalog((produce, meat), (tomato, tomato_again), ()),
        lambda: Catalog((produce,), (tomato, cherry), ()),
        lambda: Catalog((produce,), (tomato, sauce), ()),
        lambda: Catalog((), (), (quick, Tag(BiText("Quick", "快")))),
        lambda: Catalog((), (), (quick, Tag(BiText("快手", "快速")))),
    ]
    for call in calls:
        with pytest.raises(ValueError):
            call()


def test_f03_t41_whitespace_at_both_ends_does_not_count() -> None:
    """``str.strip()`` decides, so U+3000 and U+00A0 count as whitespace and U+200B does not."""
    names = [
        "葱",
        " SCALLION\t",
        "\u3000葱",
        "\u00a0葱\u00a0",
        "\n葱\r\n",
        "葱\u200b",
        "\u200b葱",
        "\ufeff葱",
    ]
    check_finds(find_catalog.find_ingredient, names, [scallion] * 5 + [None] * 3)
    assert find_catalog.find_tag(" quick\u3000") is quick
    ginger = Ingredient(BiText(" Ginger\t", "\u3000姜"), produce)
    catalog = Catalog((produce,), (ginger,), ())
    assert catalog.find_ingredient("ginger") is ginger
    assert catalog.find_ingredient("姜") is ginger


def test_f03_t42_whitespace_inside_a_name_counts_as_written() -> None:
    """Two spaces, a no-break space, a tab, or no space is another name."""
    names = [
        "Choy sum",
        "choy sum",
        "Choy  sum",
        "Choy\u00a0sum",
        "Choy\tsum",
        "Choysum",
        "Scal lion",
    ]
    check_finds(find_catalog.find_ingredient, names, [choy_sum] * 2 + [None] * 5)


def test_f03_t43_case_counts_only_for_the_letters_a_to_z() -> None:
    """The case of A to Z is ignored in a name of either language, and no other case is."""
    names = [
        "SCALLION",
        "scallion",
        "sCaLlIoN",
        "jalape\u00f1o",
        "JALAPE\u00f1O",
        "JALAPE\u00d1O",
        "xo酱",
        "Xo酱",
        "xo sauce",
        "XO SAUCE",
    ]
    wanted = [scallion] * 3 + [jalapeno] * 2 + [None] + [xo_sauce] * 4
    check_finds(find_catalog.find_ingredient, names, wanted)
    assert find_catalog.find_tag("QUICK") is quick


def test_f03_t44_look_alike_letters_stay_as_they_are() -> None:
    """Neither ``str.lower()`` nor ``str.casefold()`` is used."""
    names = ["\u212aale", "\u017fcallion", "\uff33callion", "\uff2bale", "kale", "KALE"]
    check_finds(find_catalog.find_ingredient, names, [None] * 4 + [kale] * 2)


def test_f03_t45_no_text_is_normalized() -> None:
    """A precomposed letter and a letter with a combining mark are not the same."""
    names = ["Tomato pur\u00e9e", "TOMATO PUR\u00e9E", "Tomato pure\u0301e", "jalapen\u0303o"]
    check_finds(find_catalog.find_ingredient, names, [puree] * 2 + [None] * 2)
    cafe = Ingredient(BiText("Cafe\u0301", "咖啡"), produce)
    catalog = Catalog((produce,), (cafe,), ())
    assert catalog.find_ingredient("Caf\u00e9") is None
    assert catalog.find_ingredient("CAFE\u0301") is cafe


def test_f03_t46_chinese_characters_compare_exactly_and_an_empty_form_matches_nothing() -> None:
    """A name whose matching form is empty finds nothing."""
    names = ["番茄", "番茄 ", "西红柿", "番 茄"]
    check_finds(find_catalog.find_ingredient, names, [tomato] * 2 + [None] * 2)
    for blank in ["", " ", "\u3000", "\t\n"]:
        assert find_catalog.find_ingredient(blank) is None
        assert find_catalog.find_tag(blank) is None


def test_f03_t47_ingredients_and_tags_are_kept_apart_and_no_string_raises() -> None:
    """A shared name finds each kind, and the two names of one item may match."""
    assert find_catalog.find_tag("葱") is None
    assert find_catalog.find_ingredient("quick") is None
    assert find_catalog.find_ingredient("Scallion") is scallion
    assert find_catalog.find_ingredient("葱") is scallion
    tofu = Ingredient(BiText("Tofu", "豆腐"), produce)
    bbq_sauce = Ingredient(BiText("BBQ sauce", "bbq sauce"), produce)
    tofu_tag = Tag(BiText("tofu", "豆腐"))
    bbq = Tag(BiText("BBQ", "bbq"))
    both = Catalog((produce,), (tofu, bbq_sauce), (tofu_tag, bbq))
    assert both.find_ingredient("豆腐") is tofu
    assert both.find_tag("豆腐") is tofu_tag
    assert both.find_ingredient("Bbq Sauce") is bbq_sauce
    assert both.find_tag("bbq") is bbq
    for odd in ["\ud800", "\x00", "葱" * 10000]:
        assert find_catalog.find_ingredient(odd) is None
        assert find_catalog.find_tag(odd) is None
