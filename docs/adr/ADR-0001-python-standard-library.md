---
troy-doc: "ADR-0001"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "ADR-0001-python-standard-library.zh-CN.md"
---

# ADR-0001: Python 3.13 with only the standard library at run time

## 1. Status

Accepted. Troy accepted it on 2026-11-10 by approving `docs/architecture.md`.

## 2. Context

troy-mode has language packs for Python and for C/C++. The tool reads small text files, shows text in two languages, adds up quantities, and works out ISO weeks. It must run on Troy's Windows 11 PC from any folder, pass its tests on Linux in CI, and never use the network. Every new third-party package needs the Architect's review and Troy's decision (R16), and each one adds to the lock that every member of a series shares.

## 3. Decision

The tool is written in Python 3.13 or newer, with troy-mode's Python pack. At run time it uses only the standard library: `tomllib` for the data files, `datetime` for ISO weeks, `fractions` for amounts, `unicodedata` for character widths, `pathlib` for paths, and, in v0.2, `random` for suggestions and `subprocess` for the editor. The build and check tools are the ones the pack brings: hatchling, coverage, mypy, pytest, ruff, and uv. A package that a later feature wants at run time goes through R16.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| Python with only the standard library | Every need above is in the standard library. No run-time package to review, lock, or update. The pack's tools check it on Windows and Linux. | Python starts in tens of milliseconds, and that time counts toward PT01. `tomllib` is pure Python, so parsing is slower than with a C parser (ADR-0002). |
| Python with run-time packages, such as a faster TOML parser, a table library, and a command-line library | Less code to write for tables and the command line. | Each package needs Troy's decision. Their messages are in English, so the bilingual rule still needs our own code (ADR-0005). |
| C++ with the C/C++ pack | Fast start and fast parsing. | Needs a TOML library, which is a dependency. UTF-8 console output, display widths, and dates take much more code. Every feature takes longer to write and to review. |

## 5. Consequences

- `pyproject.toml` lists no run-time dependency, and the lock changes only when the pack's tools change.
- The tool runs wherever Python 3.13 runs, with nothing to install beyond the tool itself (ADR-0006).
- Python's start-up time and `tomllib`'s speed are the costs to watch for PT01 (ADR-0002).

## 6. Related

- Features: F01 to F16
- Rules: R11, R16
