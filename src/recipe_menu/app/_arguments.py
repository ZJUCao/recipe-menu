"""What the command line gives a command."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Arguments:
    """What the command line gives a command: its argument's values and its options' values.

    ``cli`` builds it, and the command's ``run`` gets it. When ``cli`` builds it, no value of an
    option is empty or starts with ``--``. Two values are equal when their two fields are equal,
    and an ``Arguments`` is hashable.

    Attributes:
        values: The values of the argument, in the order of the command line, such as
            ``("tomato", "quick")``. There are as many as the argument allows.
        options: The options of the command that the command line gives, as (name, value) pairs
            such as ``(("--tag", "veg"),)``. The global options are not here. Each name appears
            once. ``Arguments`` sorts the pairs by name, so their order does not matter.

    Raises:
        ValueError: A name appears twice in ``options``.
    """

    values: tuple[str, ...] = ()
    options: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        """Sorts the options by name and checks that each name appears once.

        Raises:
            ValueError: A name appears twice in ``options``.
        """
        names = [name for name, _ in self.options]
        if len(set(names)) != len(names):
            raise ValueError("an option name appears twice")
        object.__setattr__(self, "options", tuple(sorted(self.options)))

    def option(self, name: str) -> str | None:
        """Gives the value of an option.

        Args:
            name: The name of an option, such as ``--tag``.

        Returns:
            The value of the option ``name``, or ``None`` when the command line does not give it.
        """
        for key, value in self.options:
            if key == name:
                return value
        return None
