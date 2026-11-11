"""The data folder and the path of each file in it."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DataFolder:
    r"""The data folder and the path of each file in it.

    It is the only place that knows the file names. It builds each path from ``root`` and looks
    at nothing on the disk. Two folders are equal when their roots are equal, and a
    ``DataFolder`` is hashable.

    Attributes:
        root: The data folder, such as ``C:\Users\Troy\recipe-menu``. It need not exist.
    """

    root: Path

    @property
    def settings(self) -> Path:
        """Gives the settings file.

        Returns:
            ``root / "settings.toml"``.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    @property
    def catalog(self) -> Path:
        """Gives the catalog file.

        Returns:
            ``root / "catalog.toml"``.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    @property
    def pantry(self) -> Path:
        """Gives the pantry file.

        Returns:
            ``root / "pantry.toml"``.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    @property
    def recipes(self) -> Path:
        """Gives the folder of the recipe files.

        Returns:
            ``root / "recipes"``.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    @property
    def menus(self) -> Path:
        """Gives the folder of the menu files.

        Returns:
            ``root / "menus"``.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    @property
    def shopping(self) -> Path:
        """Gives the folder of the shopping lists.

        Returns:
            ``root / "shopping"``.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    def recipe_file(self, recipe_id: str) -> Path:
        r"""Gives the file of a recipe.

        Args:
            recipe_id: A recipe ID, such as ``tomato-egg``.

        Returns:
            ``root / "recipes" / f"{recipe_id}.toml"``.

        Raises:
            ValueError: ``recipe_id`` is empty, is ``.`` or ``..``, or holds ``/``, ``\``,
                ``:``, or U+0000. Such a name could give the path of another file.
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    def menu_file(self, week: str) -> Path:
        r"""Gives the file of a week's menu.

        Args:
            week: An ISO week as a file name writes it, such as ``2026-W47``.

        Returns:
            ``root / "menus" / f"{week}.toml"``.

        Raises:
            ValueError: ``week`` is empty, is ``.`` or ``..``, or holds ``/``, ``\``, ``:``,
                or U+0000.
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    def shopping_file(self, week: str) -> Path:
        r"""Gives the file of a week's shopping list.

        Args:
            week: An ISO week as a file name writes it, such as ``2026-W47``.

        Returns:
            ``root / "shopping" / f"{week}.md"``.

        Raises:
            ValueError: ``week`` is empty, is ``.`` or ``..``, or holds ``/``, ``\``, ``:``,
                or U+0000.
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    def relative(self, path: Path) -> Path:
        """Gives a path inside the data folder relative to the folder.

        Args:
            path: A path inside ``root``, such as ``folder.catalog``.

        Returns:
            ``path.relative_to(root)``, such as ``Path("recipes", "mapo-tofu.toml")``. A
            ``Problem`` names its file with it.

        Raises:
            ValueError: ``path`` is not inside ``root``.
            NotImplementedError: In the mock.
        """
        raise NotImplementedError
