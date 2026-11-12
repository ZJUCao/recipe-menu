---
troy-doc: "ADR-0008"
lang: "en"
version: "1.0"
updated: "2026-11-12"
status: "Approved by Troy on 2026-11-12"
mirror: "ADR-0008-f05-error-handling.zh-CN.md"
---

# ADR-0008: Usage hints, the data folder check, and the other exceptions of tomllib

## 1. Status

Accepted. Troy accepted the decision on 2026-11-12, as decisions A to C of the F05 design.

## 2. Context

Three rows of architecture 6 did not fit the F05 design.

- **A usage error.** Architecture 6 said that an error with exit code 2 shows the message and then a line that points to `recipe-menu --help`. The F11 prototype "A week without a menu" shows `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` with no such line, and v0.1-S15 expects that output. The help also does not list the options of a command, such as `--tag`, so a line that points to the help does not help with `--tag needs a value.`.
- **A missing data folder.** Architecture 6 said that the command checks it. But `cli` already looks at the data folder at start, because it reads the settings before it reports a mistake on the command line (F05 design, choice 5). If each command checked the folder, the seven commands of v0.1 that need it would repeat one check and one message.
- **A syntax mistake.** Architecture 6 and ADR-0002 named `tomllib.TOMLDecodeError` and `UnicodeDecodeError`. `tomllib` also raises a plain `ValueError` for a decimal integer of more than 4,300 digits and a `RecursionError` for nesting that is too deep. F03's `read_toml` catches both (F03 design 2.3), and the F03 design review left this wording open.

## 3. Decision

- **A.** A `UsageError` names the line that follows its message: `RUN_HELP_FOR_COMMANDS` or `RUN_HELP_FOR_OPTIONS` of F02, or `None`. An error whose message already says what to write can name no line, as F11's wrong week does. `cli` writes the message, then the line when the error names one, and exits with 2. Architecture 5.2 and 6 say so.
- **B.** `cli` checks a missing data folder before it runs each command whose `FolderUse` asks for it. It writes the message of the F05 prototype "No data folder yet" and exits with 1. `init` creates the folder, so `cli` does not check the folder for it (F05 design 2.5). A command still checks a missing menu or recipe itself.
- **C.** Architecture 6 and ADR-0002 name the plain `ValueError` and `RecursionError` that `read_toml` catches, beside `tomllib.TOMLDecodeError` and `UnicodeDecodeError`. Only the wording changes.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| A: each usage error names its line, or none. Chosen. | No line repeats what the message already says. The F11 prototype and v0.1-S15 stay as they are. One row of architecture 6 changes, and no requirement. | Each `UsageError` takes one more argument, and each design names the line of each of its usage errors. |
| A: every usage error ends with a line that points to `--help`. | One rule with no exceptions, as architecture 6 said. | The line repeats a message that already says what to write, and it points to a help that does not list the options of a command. The F11 prototype and v0.1-S15 would change. |
| B: `cli` checks the data folder, as `FolderUse` asks. Chosen. | One check and one message for every command that needs the folder. `cli` already looks at the folder to read the settings. | `Command` gains a field, and `cli` handles three kinds of folder use. |
| B: each command checks the data folder. | Architecture 6 stays as it is. Each command owns all of its checks. | The seven commands of v0.1 that need the folder repeat the check and the message, and each needs its own tests of them. |
| C: name the two exceptions. Chosen. | The documents name every exception that `read_toml` catches. The change is wording only. | None |
| C: keep the wording. | No document changes. | Architecture 6 says that an `except` clause names what it catches, and the documents would leave out two of those exceptions. |

## 5. Consequences

- `cli` writes a usage error, and its line when it names one, to stderr and exits with 2. Each command feature's design names the line of each of its usage errors. F11 names none for a wrong week.
- A command whose `FolderUse` is `READ` or `CHECK` never runs without its data folder, so its feature needs no check of a missing folder. `init` (F08) also runs when the folder is missing.
- A missing menu or recipe stays the command's own check, with the messages of its prototype, such as F11 "A week without a menu".
- Decision C changes no code. F03's `read_toml` already catches the two exceptions.
- No requirement, prototype, or scenario changes for A to C. Decision D of the F05 design adds a third line to the F05 prototype "A broken settings file", and the Product Manager makes that change.

## 6. Related

- Features: F03, F05, F07, F08, F09, F10, F11, F13, F14, F15, F16
- Rules: None
