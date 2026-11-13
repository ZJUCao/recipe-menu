---
troy-doc: "ADR-0009"
lang: "en"
version: "1.0"
updated: "2026-11-13"
status: "Approved by Troy on 2026-11-13"
mirror: "ADR-0009-init-failure-full-path.zh-CN.md"
---

# ADR-0009: A failure of init names its file by its full path

## 1. Status

Accepted. Troy accepted the decision on 2026-11-13, as option 1 of open question D of the F08 design.

## 2. Context

Architecture 6 says: "A problem names its file relative to the data folder, with the system's separator, such as `recipes\mapo-tofu.toml` on Windows. Other messages name a file or a folder by its full path." The rule fits the problems that readers and `check` report, because they concern a data folder that you use every day.

F08's `create_data_folder` turns the first `OSError` that stops it into a `Problem`, whose file is relative to the data folder (F08 design 3.2). `init` writes that problem as the first line of a failure, and two things make the relative path a poor fit there:

- The data folder is the one that you just asked `init` to create, often with `--data`, and `init` may also have created the folders above it. A failure has to say where on the disk it happened.
- A failure at the data folder itself, or at a folder above it, has the file `Path(".")`, which shows as `.`.

The other lines of `init`, the first line of a new folder and the two refusals, already name the data folder by its full path (F08 design 2.2).

## 3. Decision

- The first line of a failure of `init` names the folder or file that `init` could not create by its full path, `str(context.folder.root / problem.file)`. For the file `Path(".")`, which a failure at the data folder or at a folder above it has, that line names the data folder.
- The `Problem` still holds its file relative to the data folder (architecture 5.2 and 5.3, F08 design 3.2). Only the line that `init` writes gives the full path.
- Every problem that a reader or a check reports keeps the relative path of architecture 6.
- F11's `menu new` and F13's `shop` may also name a file that they could not write by its full path. Their prototypes already name the file that they write by its full path: the line of a new menu, the refusal of an existing menu, and the line of a saved list. Each design decides whether it uses the case, and the Architect reviews it.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| Option 1: the full path. Chosen. | You see where on the disk `init` failed, and a failure at the data folder shows the folder, not `.`. The line names paths the way the other lines of `init` do. The `Problem` and every reader stay as they are. | Architecture 6 gains a case. `init` cannot use F05's `problem_lines` for the first line, so it writes that line itself. |
| Option 2: the path relative to the data folder, as architecture 6 said. | Architecture 6 stays as it is. | A failure at `recipes` shows `recipes`, and a failure at the data folder or at a folder above it shows `.`, which says nothing about where. The first line of a failure in F08 design 2.2 and its example change. |

## 5. Consequences

- Architecture 6 names the case in version 2.1. Architecture 5.2 and 5.3 do not change.
- F05's `problem_lines` and `stop_at_error` do not change. They keep the relative path for the problems of readers. `init` writes its failure without them, because its last line is `CHANGED_NOTHING` or `LEFT_BEHIND`, not `RUN_CHECK`.
- F08 design 2.2 and its example stay as Troy approved them in version 1.0. No requirement, prototype, scenario, or test changes, and no code changes, because F08 has no code yet.
- A design of F11 or F13 that uses the case says so and points to this record. A design that does not use it keeps the relative path.
- A later write, such as F15's `add` in v0.2, needs its own change to architecture 6 to use the case.

## 6. Related

- Features: F05, F08, F11, F13
- Rules: None
