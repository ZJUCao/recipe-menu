"""Tests of F03 for read_toml and the files it reads (F03-T12 to F03-T20)."""

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from f03_support import (
    M_ACCESS_DENIED,
    M_FILE_IS_FOLDER,
    M_FILE_MISSING,
    M_MISSING_BRACKET,
    M_NOT_UTF8,
    at_line,
    check_toml,
    m_system_error,
    put_bytes,
    write,
)
from recipe_menu.datafile import DataFolder, read_toml

PANTRY = {"pantry": ["食用油", "盐", "糖", "生抽", "花椒"]}


@contextmanager
def denied(path: Path) -> Iterator[None]:
    """Makes reading ``path`` fail with ``PermissionError``, and undoes it afterwards."""
    if sys.platform == "win32":
        import msvcrt  # noqa: PLC0415

        size = path.stat().st_size
        with path.open("r+b") as handle:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, size)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, size)
    else:
        path.chmod(0)
        try:
            yield
        finally:
            path.chmod(0o644)


def test_f03_t12_read_toml_gives_the_table_of_each_example_file(example_folder: DataFolder) -> None:
    """The tables are as ``tomllib`` reads the four files of the example."""
    folder = example_folder
    pantry = read_toml(folder, folder.pantry)
    settings = read_toml(folder, folder.settings)
    catalog = read_toml(folder, folder.catalog)
    recipe = read_toml(folder, folder.recipe_file("tomato-egg"))
    for table in (pantry, settings, catalog, recipe):
        assert isinstance(table, dict)
    assert pantry == PANTRY
    assert settings == {"language": "en", "meals": ["lunch", "dinner"], "servings": 2}
    assert list(catalog) == ["categories", "ingredients", "tags"]
    assert [len(catalog[key]) for key in catalog] == [6, 22, 5]
    assert catalog["ingredients"][3] == {
        "zh": "葱",
        "en": "Scallion",
        "category": "produce",
        "unit": "根",
    }
    assert recipe["servings"] == 2
    assert recipe["name"] == {"zh": "番茄炒蛋", "en": "Tomato and egg stir-fry"}


def test_f03_t13_a_byte_order_mark_and_crlf_do_not_change_the_table(
    example_folder: DataFolder,
) -> None:
    """The BOM and CRLF are no part of the table, and a file with no keys gives ``{}``."""
    folder = example_folder
    data = folder.pantry.read_bytes()
    variants = [
        b"\xef\xbb\xbf" + data,
        data.replace(b"\n", b"\r\n"),
        b"\xef\xbb\xbf" + data.replace(b"\n", b"\r\n"),
    ]
    for variant in variants:
        put_bytes(folder.pantry, variant)
        assert read_toml(folder, folder.pantry) == PANTRY
    for empty in (b"\xef\xbb\xbf", b"", b"# only a comment\n"):
        put_bytes(folder.pantry, empty)
        assert read_toml(folder, folder.pantry) == {}


def test_f03_t14_a_missing_comma_gives_the_line_whatever_the_line_ends(folder: DataFolder) -> None:
    """A BOM and CRLF do not change the line of the mistake."""
    text = '# The pantry.\npantry = ["食用油", "盐" "糖"]\n'
    variants = [
        text.encode("utf-8"),
        text.replace("\n", "\r\n").encode("utf-8"),
        b"\xef\xbb\xbf" + text.encode("utf-8"),
    ]
    for variant in variants:
        put_bytes(folder.pantry, variant)
        result = read_toml(folder, folder.pantry)
        check_toml(result, Path("pantry.toml"), at_line(2), M_MISSING_BRACKET)


def test_f03_t15_a_missing_file_a_missing_folder_or_a_file_for_a_folder(tmp_path: Path) -> None:
    """Each gives ``FILE_MISSING`` with no place, and nothing raises."""
    folder = DataFolder(tmp_path)
    check_toml(read_toml(folder, folder.settings), Path("settings.toml"), None, M_FILE_MISSING)
    result = read_toml(folder, folder.recipe_file("tomato-egg"))
    check_toml(result, Path("recipes", "tomato-egg.toml"), None, M_FILE_MISSING)
    nowhere = DataFolder(tmp_path / "nowhere")
    check_toml(read_toml(nowhere, nowhere.catalog), Path("catalog.toml"), None, M_FILE_MISSING)
    write(tmp_path / "data.txt", "x")
    on_file = DataFolder(tmp_path / "data.txt")
    check_toml(read_toml(on_file, on_file.catalog), Path("catalog.toml"), None, M_FILE_MISSING)


def test_f03_t16_a_folder_in_the_place_of_the_file_gives_file_is_folder(tmp_path: Path) -> None:
    """The folder comes before ``ACCESS_DENIED``, which Windows gives for a folder."""
    folder = DataFolder(tmp_path)
    folder.catalog.mkdir()
    folder.recipe_file("tomato-egg").mkdir(parents=True)
    check_toml(read_toml(folder, folder.catalog), Path("catalog.toml"), None, M_FILE_IS_FOLDER)
    result = read_toml(folder, folder.recipe_file("tomato-egg"))
    check_toml(result, Path("recipes", "tomato-egg.toml"), None, M_FILE_IS_FOLDER)


def test_f03_t17_a_file_that_the_user_may_not_read_gives_access_denied(folder: DataFolder) -> None:
    """A file with no permissions, or a locked file on Windows, gives ``ACCESS_DENIED``."""
    write(folder.pantry, 'pantry = ["盐"]\n')
    with denied(folder.pantry):
        with pytest.raises(PermissionError):
            folder.pantry.read_bytes()
        result = read_toml(folder, folder.pantry)
    check_toml(result, Path("pantry.toml"), None, M_ACCESS_DENIED)


def test_f03_t18_any_other_oserror_gives_system_error_with_its_reason(tmp_path: Path) -> None:
    """A real ``OSError`` gives the error's ``strerror`` as the reason, and nothing raises."""
    folder = DataFolder(tmp_path)
    if sys.platform == "win32":
        name, reason = "a?b.toml", "Invalid argument"
    else:
        name, reason = "a" * 256 + ".toml", "File name too long"
    result = read_toml(folder, tmp_path / name)
    check_toml(result, Path(name), None, m_system_error(reason))


def test_f03_t19_a_file_that_is_not_utf8_gives_the_line_of_the_first_bad_byte(
    folder: DataFolder,
) -> None:
    """The line is one more than the LF bytes before the byte, counted after a BOM."""
    cases = [
        (b"tags = []\n# caf\xe9\n", 2),
        (b"\xef\xbb\xbftags = []\n\xff\n", 2),
        (b"\xef\xbb\xbfa\n\xff", 2),
        (b"\xff", 1),
        (b"a = 1\r\nb = 2\r\n\xff", 3),
        (b"a = 1\r\xff", 1),
        (b"\xff\xfe" + "tags = []\n".encode("utf-16-le"), 1),
        ('zh = "番茄"\n'.encode("gbk"), 1),
        (b'a = 1\nzh = "\xe7\x95', 2),
        (b"a = \n\xff\n", 2),
    ]
    for data, line in cases:
        put_bytes(folder.pantry, data)
        result = read_toml(folder, folder.pantry)
        check_toml(result, Path("pantry.toml"), at_line(line), M_NOT_UTF8)


def test_f03_t20_a_path_outside_the_data_folder_is_a_wrong_call(tmp_path: Path) -> None:
    """``read_toml`` raises ``ValueError`` before it reads."""
    root = tmp_path / "recipe-menu"
    root.mkdir()
    folder = DataFolder(root)
    write(tmp_path / "recipe-menu2" / "catalog.toml", "tags = []\n")
    outside = [
        tmp_path / "other" / "catalog.toml",
        tmp_path / "recipe-menu2" / "catalog.toml",
        Path("catalog.toml"),
        Path("D:/other/catalog.toml"),
    ]
    for path in outside:
        with pytest.raises(ValueError):
            read_toml(folder, path)
