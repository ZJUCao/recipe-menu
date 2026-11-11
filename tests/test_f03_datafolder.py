"""Tests of F03 for DataFolder (F03-T01 to F03-T04)."""

from pathlib import Path

import pytest

from recipe_menu.datafile import DataFolder

NAME_METHODS = ("recipe_file", "menu_file", "shopping_file")


def test_f03_t01_each_property_gives_its_path_and_looks_at_nothing(tmp_path: Path) -> None:
    """Each property and method gives the path of design 2.1, and the root need not exist."""
    root = tmp_path / "recipe-menu"
    folder = DataFolder(root)
    results = [
        folder.settings,
        folder.catalog,
        folder.pantry,
        folder.recipes,
        folder.menus,
        folder.shopping,
        folder.recipe_file("tomato-egg"),
        folder.menu_file("2026-W47"),
        folder.shopping_file("2026-W47"),
    ]
    expected = [
        root / "settings.toml",
        root / "catalog.toml",
        root / "pantry.toml",
        root / "recipes",
        root / "menus",
        root / "shopping",
        root / "recipes" / "tomato-egg.toml",
        root / "menus" / "2026-W47.toml",
        root / "shopping" / "2026-W47.md",
    ]
    assert results == expected
    assert all(isinstance(result, Path) for result in results)
    assert folder.root == root
    assert not root.exists()


def test_f03_t02_a_name_that_is_not_rejected_is_used_as_it_is(tmp_path: Path) -> None:
    """A name with dots, spaces, or Chinese characters goes into the file name unchanged."""
    folder = DataFolder(tmp_path)
    names = ["tomato-egg", "番茄炒蛋", "2026-W47", "...", ".a", "a..b", "a b"]
    for name in names:
        assert folder.recipe_file(name) == tmp_path / "recipes" / (name + ".toml")
        assert folder.menu_file(name) == tmp_path / "menus" / (name + ".toml")
        assert folder.shopping_file(name) == tmp_path / "shopping" / (name + ".md")


def test_f03_t03_a_name_that_could_reach_another_file_is_a_wrong_call(tmp_path: Path) -> None:
    """An empty name, ``.``, ``..``, and a name with a separator or a colon raise."""
    folder = DataFolder(tmp_path)
    names = [
        "",
        ".",
        "..",
        "../catalog",
        "..\\catalog",
        "C:catalog",
        "a/b",
        "a\\b",
        "a:b",
        "a\x00b",
        "\x00",
        "/",
        "\\",
    ]
    for method in NAME_METHODS:
        for name in names:
            with pytest.raises(ValueError):
                getattr(folder, method)(name)


def test_f03_t04_relative_gives_a_path_inside_the_root_and_rejects_others(tmp_path: Path) -> None:
    """``relative`` strips the root, and a path outside the root is a wrong call."""
    root = tmp_path / "recipe-menu"
    folder = DataFolder(root)
    assert folder.relative(folder.catalog) == Path("catalog.toml")
    assert folder.relative(folder.recipe_file("mapo-tofu")) == Path("recipes", "mapo-tofu.toml")
    assert folder.relative(folder.menu_file("2026-W47")) == Path("menus", "2026-W47.toml")
    assert folder.relative(folder.shopping_file("2026-W47")) == Path("shopping", "2026-W47.md")
    outside = [
        tmp_path / "other" / "catalog.toml",
        tmp_path / "recipe-menu2" / "catalog.toml",
        tmp_path,
        Path("catalog.toml"),
    ]
    for path in outside:
        with pytest.raises(ValueError):
            folder.relative(path)
