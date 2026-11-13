"""The named changes of the F07 test plan, which make the mistakes of the cases in a folder.

Each function takes the root of a data folder, or a file, and changes the files in it. Nothing
here calls an interface of ``check`` when the module is imported.
"""

from pathlib import Path

from f03_support import edit_ingredients, ing, write
from f05_support import copy_example
from f06_support import mistakes, typo
from recipe_menu.datafile import DataFolder


def edit(path: Path, old: str, new: str) -> None:
    """Replaces the first ``old`` of a file by ``new``, and checks that the file holds ``old``."""
    text = path.read_text(encoding="utf-8")
    assert old in text, (path, old)
    write(path, text.replace(old, new, 1))


def append(path: Path, text: str) -> None:
    """Adds the text at the end of a file."""
    write(path, path.read_text(encoding="utf-8") + text)


def menu_path(root: Path, week: str = "2026-W47") -> Path:
    """Gives the path of a menu file of a data folder."""
    return root / "menus" / f"{week}.toml"


def make_init(source: DataFolder, target: Path) -> Path:
    """Makes the init folder at ``target`` from a copy of the example folder ``source``.

    It has no recipe other than ``tomato-egg`` and no menu file, and it has the empty folders
    ``menus/`` and ``shopping/``.
    """
    copy_example(source, target)
    for path in (target / "recipes").glob("*.toml"):
        if path.stem != "tomato-egg":
            path.unlink()
    menu_path(target).unlink()
    (target / "shopping").mkdir()
    return target


def mapo_mistake(root: Path) -> None:
    """Cuts the name of ingredient 3 of ``mapo-tofu`` to a name that the catalog lacks."""
    edit(root / "recipes" / "mapo-tofu.toml", "郫县", "")


def the_typo(root: Path) -> None:
    """Writes ``tomato-eggs`` in Monday dinner."""
    typo(DataFolder(root))


def undo_two(root: Path, source: DataFolder) -> None:
    """Writes the two files of the two mistakes back as they are in ``source``."""
    for relative in (Path("recipes", "mapo-tofu.toml"), menu_path(Path())):
        write(root / relative, (source.root / relative).read_text(encoding="utf-8"))


def pork_in_english(root: Path) -> None:
    """Adds English steps to ``red-braised-pork``, which removes its warning."""
    append(root / "recipes" / "red-braised-pork.toml", 'en = ["Braise the pork."]\n')


def the_comma(root: Path) -> None:
    """Deletes the comma between salt and sugar in the pantry."""
    edit(root / "pantry.toml", '"盐", "糖"', '"盐" "糖"')


def broken_settings(root: Path) -> None:
    """Writes settings with the unknown meal ``supper``."""
    write(root / "settings.toml", 'meals = ["lunch", "supper"]\n')


def catalog_brace(root: Path) -> None:
    """Deletes the comma after the Chinese name of ingredient 1, as in F03-T81."""
    edit(
        root / "catalog.toml",
        '{ zh = "番茄", en = "Tomato", category = "produce" }',
        '{ zh = "番茄" en = "Tomato", category = "produce" }',
    )


def catalog_two(root: Path) -> None:
    """Makes the two catalog mistakes of F03-T50: a second Rice, and the category ``meats``."""
    catalog = root / "catalog.toml"
    edit(
        catalog,
        '{ zh = "葱", en = "Scallion", category = "produce", unit = "根" }',
        '{ zh = "米", en = "Rice", category = "staples" }',
    )
    edit(
        catalog,
        '{ zh = "五花肉", en = "Pork belly", category = "meat" }',
        '{ zh = "五花肉", en = "Pork belly", category = "meats" }',
    )


def catalog_s07(root: Path) -> None:
    """Adds ingredients 23 and 24 of the S07 mistakes to the catalog."""
    adds = [ing("芥兰", "Broccoli"), ing("香菜", "Coriander", "meats")]
    edit_ingredients(DataFolder(root), added=adds)


def pantry_sesame(root: Path) -> None:
    """Replaces sugar in the pantry by ``sesame oil``."""
    edit(root / "pantry.toml", '"糖"', '"sesame oil"')


def pantry_not_text(root: Path) -> None:
    """Replaces sugar in the pantry by the number 3."""
    edit(root / "pantry.toml", '"糖"', "3")


def servings_zero(root: Path, recipe: str) -> None:
    """Replaces the servings of a recipe by 0."""
    edit(root / "recipes" / f"{recipe}.toml", "servings = 2", "servings = 0")


def s07_mistakes(root: Path) -> None:
    """Makes the 9 mistakes of v0.1-S07."""
    catalog_s07(root)
    pantry_sesame(root)
    rice = root / "recipes" / "rice.toml"
    edit(rice, "servings = 2", "servings = 0")
    edit(rice, '["主食"]', '["breakfast"]')
    edit(rice, '"160 g"', '"1 cups"')
    mistakes(DataFolder(root))


def add_friday_key(path: Path) -> None:
    """Adds ``supper = []`` to Friday of a menu file."""
    edit(path, "[friday]\n", "[friday]\nsupper = []\n")


def add_monday_breakfast(path: Path) -> None:
    """Adds ``breakfast = ["rice"]`` to Monday of a menu file."""
    edit(path, "[monday]\n", '[monday]\nbreakfast = ["rice"]\n')


def menu_copy(root: Path, week: str) -> Path:
    """Writes the example menu as the menu of another week, and gives its path."""
    source = menu_path(root).read_text(encoding="utf-8")
    path = menu_path(root, week)
    write(path, source.replace('week = "2026-W47"', f'week = "{week}"', 1))
    return path
