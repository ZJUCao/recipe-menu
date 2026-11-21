"""Asking one question: the prompt, the echo of the answer, and one line of input."""

from recipe_menu.app import Context


def ask_line(context: Context, prompt: str) -> str | None:
    """Writes a prompt and reads one answer.

    It writes the prompt to ``context.out`` and flushes it, so the prompt shows before the
    answer is read, and then reads one line with ``context.input.readline()``. When the input is
    not a terminal, it writes the line that it read, without the LF at its end, and a line break,
    so a session through a pipe reads like one in a console.

    Args:
        context: The output stream and the input stream.
        prompt: The text of the prompt.

    Returns:
        The line without whitespace at both ends, or ``None`` at the end of the input.
    """
    context.out.write(prompt)
    context.out.flush()
    line = context.input.readline()
    if not context.input.isatty():
        context.out.write(f"{line.removesuffix(chr(10))}\n")
    return line.strip() if line else None


def write_line(context: Context, text: str, indent: str = "") -> None:
    """Writes one line of the session to the output stream.

    Args:
        context: The output stream.
        text: The text of the line, without a line break.
        indent: What comes before the text, such as two spaces.
    """
    context.out.write(f"{indent}{text}\n")
