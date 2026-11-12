"""The data folder, TOML files, and the problems that data files cause."""

from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._listing import list_toml_files
from recipe_menu.datafile._problem import Problem, Severity
from recipe_menu.datafile._shape import (
    Report,
    read_list,
    read_table,
    read_text,
    report_unknown_keys,
)
from recipe_menu.datafile._toml import read_toml
from recipe_menu.datafile.messages import (
    EMPTY_ITEM,
    EMPTY_TEXT,
    ITEM_NOT_A_TEXT,
    MISSING_KEY,
    NOT_A_LIST,
    NOT_A_TABLE,
    NOT_A_TEXT,
    UNKNOWN_KEY,
)

__all__ = [
    "EMPTY_ITEM",
    "EMPTY_TEXT",
    "ITEM_NOT_A_TEXT",
    "MISSING_KEY",
    "NOT_A_LIST",
    "NOT_A_TABLE",
    "NOT_A_TEXT",
    "UNKNOWN_KEY",
    "DataFolder",
    "Problem",
    "Report",
    "Severity",
    "list_toml_files",
    "read_list",
    "read_table",
    "read_text",
    "read_toml",
    "report_unknown_keys",
]
