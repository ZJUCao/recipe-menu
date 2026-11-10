---
troy-doc: "ADR-0002"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "ADR-0002-toml-data-files.zh-CN.md"
---

# ADR-0002: TOML data files read with tomllib

## 1. Status

Accepted. Troy accepted it on 2026-11-10 by approving `docs/architecture.md`.

## 2. Context

Requirements section 3 leaves the format of the data files to the architecture, and the prototypes show TOML. Troy writes the files by hand in Notepad or VS Code, in Chinese and English. A syntax mistake must show its line, and a wrong value must show its field. The tool must never change a file that Troy wrote, except that v0.2's `menu suggest` fills the empty meals of a menu. `check`, `list`, and `search` read up to 1,000 recipe files and must finish within 1 second (PT01).

## 3. Decision

- Every data file is TOML 1.0, in the layout of `docs/prototypes/example-data.md`, with the extension `.toml`. Architecture section 5.1 lists the files.
- `datafile` reads a file as bytes, decodes it as UTF-8 with or without a byte order mark, and parses it with `tomllib`. A syntax mistake gives the line: from the `lineno` attribute of `tomllib.TOMLDecodeError` where Python has it (3.14), and from the "(at line N, column M)" at the end of its message on Python 3.13.
- A wrong value names its field, such as "ingredient 3", because `tomllib` gives no positions for values. This is what requirements section 3 asks for.
- Commands that create a file write text that the code builds from a template. The tool has no TOML writer.
- How v0.2's `menu suggest` changes an existing menu file is decided in F14's design. It either rewrites only the lines of empty meals, or uses a library that keeps a file's layout, such as tomlkit, which would be a new dependency under R16.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| TOML, read with `tomllib` | In the standard library. Comments, Unicode strings, and no meaningful indentation. The prototypes and `init`'s files already use it. Syntax errors carry a line. | No writer in the standard library. Pure-Python parsing. Values carry no position. |
| YAML | Short to write, and lists read well. | Needs PyYAML, a dependency. Indentation errors are easy to make in Notepad, and a bare `no` becomes false. |
| JSON | In the standard library, and fast to parse. | No comments. Quotes and commas everywhere make it hard to write by hand. |
| A line format of our own | Could be the shortest to type. | Needs its own parser, its own syntax errors in two languages, and documentation. Troy would have one more format to learn. |

## 5. Consequences

- `init` writes exactly the files of the prototypes, and every editor can open them.
- Parsing all recipes is the largest cost of `list`, `search`, and `check`. The first PT01 measurement on Troy's PC, in the PR 5 of F07 or F09, shows how much margin is left.
- If PT01 fails, a cache of parsed recipes would write a file that v0.1 does not allow ("Your files stay as you wrote them"), so it would need a requirement change and an architecture change first.
- A change to an existing file needs care in F14's design, because rewriting a whole file would drop Troy's comments.

## 6. Related

- Features: F03, F04, F05, F06, F07, F08, F11, F14, F15
- Rules: R16
