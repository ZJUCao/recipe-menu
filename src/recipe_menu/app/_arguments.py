"""What the command line gives a command."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Arguments:
    """What the command line gives a command: its argument's values and its options' values.

    ``cli`` builds it, and the command's ``run`` gets it. When ``cli`` builds it, no value of an
    option is empty or starts with ``--``. Two values are equal when their two fields are equal,
    and an ``Arguments`` is hashable.

    The mock leaves out the sort and the check below.

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

    def option(self, name: str) -> str | None:
        """Gives the value of an option.

        The mock raises ``NotImplementedError``. The implementation gives the value by the rule
        below.

        Args:
            name: The name of an option, such as ``--tag``.

        Returns:
            The value of the option ``name``, or ``None`` when the command line does not give it.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError
