"""Tests of F02 for use_utf8 (F02-T67 to F02-T70)."""

import io
import os
import subprocess
import sys

from recipe_menu.text import use_utf8

SURROGATES = "番茄 \udcff \ud800 \U0001f600"
ESCAPED = "番茄 \\udcff \\ud800 \U0001f600"


def test_f02_t67_text_wrapper_writes_utf8_after_the_call() -> None:
    """A ``TextIOWrapper`` writes UTF-8 and a lone surrogate as an escape."""
    for encoding in ("cp1252", "cp437", "gbk", "ascii", "utf-8"):
        raw = io.BytesIO()
        stream = io.TextIOWrapper(raw, encoding=encoding)
        assert use_utf8(stream) is None
        stream.write(SURROGATES)
        assert use_utf8(stream) is None
        stream.flush()
        assert stream.encoding == "utf-8"
        assert stream.errors == "backslashreplace"
        assert raw.getvalue() == ESCAPED.encode()


def test_f02_t68_text_held_before_the_call_is_flushed_in_the_old_encoding() -> None:
    """What the stream holds before the call is written in the old encoding."""
    raw = io.BytesIO()
    stream = io.TextIOWrapper(raw, encoding="cp1252")
    stream.write("café ")
    use_utf8(stream)
    assert raw.getvalue() == "café ".encode("cp1252")
    stream.write("番茄")
    stream.flush()
    assert raw.getvalue() == "café ".encode("cp1252") + "番茄".encode()


class RecordingStringIO(io.StringIO):
    """A ``StringIO`` with a ``reconfigure`` method that records each call."""

    def __init__(self) -> None:
        """Creates the stream with no calls recorded."""
        super().__init__()
        self.calls: list[dict[str, object]] = []

    def reconfigure(self, **options: object) -> None:
        """Records a call.

        Args:
            **options: The options of the call.
        """
        self.calls.append(options)


def test_f02_t69_other_streams_stay_as_they_are() -> None:
    """A stream that is not a ``TextIOWrapper`` stays as it is."""
    plain = io.StringIO()
    recording = RecordingStringIO()
    for stream in (plain, recording):
        stream.write("abc")
        assert use_utf8(stream) is None
        assert stream.getvalue() == "abc"
        stream.write("番茄 \udcff")
        assert stream.getvalue() == "abc番茄 \udcff"
    assert recording.calls == []


CHILD_CODE = (
    "import sys\n"
    "from recipe_menu.text import use_utf8\n"
    "use_utf8(sys.stdout)\n"
    "use_utf8(sys.stderr)\n"
    'text = "\\u756a\\u8304 " + chr(0xDCFF)\n'
    "sys.stdout.write(text)\n"
    "sys.stderr.write(text)\n"
)


def test_f02_t70_standard_streams_of_a_child_write_utf8_through_pipes() -> None:
    """The standard streams of a child write UTF-8 through a pipe."""
    assert CHILD_CODE.isascii()
    for encoding in ("cp437", "cp1252", "gbk"):
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = encoding
        done = subprocess.run(  # noqa: S603
            [sys.executable, "-c", CHILD_CODE], env=env, capture_output=True, check=False
        )
        assert done.returncode == 0, done.stderr
        assert done.stdout == "番茄 \\udcff".encode()
        assert done.stderr == "番茄 \\udcff".encode()
