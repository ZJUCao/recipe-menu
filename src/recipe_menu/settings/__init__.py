"""The settings of a data folder: language, meals of each day, servings, and dishes of each meal."""

from recipe_menu.settings._meal import Meal
from recipe_menu.settings._read import read_settings
from recipe_menu.settings._settings import Settings

__all__ = ["Meal", "Settings", "read_settings"]
