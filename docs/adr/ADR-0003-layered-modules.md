---
troy-doc: "ADR-0003"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "ADR-0003-layered-modules.zh-CN.md"
---

# ADR-0003: Layered modules, each a folder with one interface file

## 1. Status

Accepted. Troy accepted it on 2026-11-10 by approving `docs/architecture.md`.

## 2. Context

R07 checks imports against the module table of the architecture, so each module needs exact path patterns and one set of interface files. The 16 features are built one at a time in topological order, and each designer sees only the features before it. A file may hold at most 500 lines (R06), and a source PR may change at most 5 files (R03). Tests need a fixed date, a data folder of their own, and string streams in place of the console.

## 3. Decision

- The package `recipe_menu` has five layers: base (`lang`, `units`, `text`, `datafile`), domain (`catalog`, `recipes`, `settings`, `menus`, `shopping`), application (`app`), commands (one module for each command feature, under `commands/`), and entry (`cli`). A module depends only on lower layers and on the modules of its own layer that the architecture names.
- Every module is a folder. Its `__init__.py` is the only file that other modules import, and every other file in the folder is internal.
- Only `cli` reads the command line, the environment, the date, and the console. It passes them down through `Context`.
- Each command module defines its `Command` values, and `cli` keeps the list of commands. A command feature adds its entry to that list in its mock PR.
- `shopping` reads no file, so the shopping rules can be tested on values alone.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| A folder per module, with `__init__.py` as the interface | R07 catches any import of a module's internal file. A module can split into more files without a change to the table. | Each module needs an `__init__.py` that lists its public names. |
| A single file per module, such as `units.py` | Fewer files. | When a file passes 500 lines (R06), splitting it changes the paths in the table, and that is an architecture change for Troy to approve. |
| A flat package with no module table | Nothing to keep up to date. | R07 can check nothing, and any file may import any other. |
| Commands that read the environment themselves | Less to pass around. | Tests would need to patch the clock, the environment, and the console. |

## 5. Consequences

- R07 fails a PR that imports another module's internal file, that imports upward, or that adds a cycle.
- The layers hold for v0.2. `suggest`, `add`, and `edit` fit as command modules with no change to the table.
- Two features use a module that an earlier feature created, beyond the requirements' graph: F02 uses `lang` from F01, and F05 uses `datafile` from F03.
- Every command feature changes one line in `cli`, which F05 owns. That line is the only coupling between a command and the entry point.
- Command modules may depend on every domain module. The design review checks that a command uses only what it needs.

## 6. Related

- Features: F01 to F16
- Rules: R03, R06, R07
