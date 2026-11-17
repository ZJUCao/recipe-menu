---
troy-doc: "ADR-0011"
lang: "en"
version: "1.0"
updated: "2026-11-17"
status: "Approved by Troy on 2026-11-17"
mirror: "ADR-0011-suggest-swap-line-relative-path.zh-CN.md"
---

# ADR-0011: The swap line of menu suggest names its file relative to the data folder

## 1. Status

Accepted. Troy accepted the decision on 2026-11-17, as option 1 of point D of the F14 design.

## 2. Context

Architecture 6 says that a problem names its file relative to the data folder, with the system's separator, and that other messages name a file or a folder by its full path. ADR-0009 and ADR-0010 let `init`, `menu new`, and `shop` name a file that they could not write by its full path. Section 5 of ADR-0009 asks every later case for its own change to architecture 6.

F14's `menu suggest` names the week's menu file in two lines (F14 design, choices 8 and 9):

- The swap line, which ends a first fill and the output for a week with no empty meal. The F14 prototype, which Troy approved, writes it as `To swap a dish, empty its meal in menus\2026-W48.toml, then run "recipe-menu menu suggest 2026-W48" again.`. The line is not a problem, so architecture 6 would have it name the full path.
- The first line of a failed save, which writes the `Problem` that `replace_file` gives. Architecture 6 already has it name the file relative to the data folder, as the problem holds it.

So under architecture 6 as it stood, `menu suggest` would name its menu file two ways: by its full path in the swap line, which also changes the line of the prototype, and relative to the data folder after a failed save.

A third line, `LEFT_BEHIND`, names the temporary file `menus/<week>.toml.tmp` that `replace_file` could not remove. It is not a problem either, and `shop` names its temporary file by its full path.

## 3. Decision

- The swap line of `menu suggest` names the week's menu file as a problem names its file: relative to the data folder, with the system's separator, `str(context.folder.relative(path))`. That is `menus\2026-W48.toml` on Windows and `menus/2026-W48.toml` on Linux.
- The first line of a failed save of `menu suggest` names the file as its problem holds it, such as `menus\2026-W48.toml` above `  The file cannot be written: access is denied.`. Architecture 6 already says so for a problem, so this needs no new case. Neither does the first line of `CANNOT_FILL`, which is a problem too.
- `LEFT_BEHIND` names the temporary file by its full path, such as `C:\Users\Troy\recipe-menu\menus\2026-W48.toml.tmp`, as architecture 6 says for a message that is not a problem.
- The cases of `init` (ADR-0009), `menu new` (ADR-0010), and `shop` stay as they are.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| Option 1: the swap line and a failed save name the menu file relative to the data folder. Chosen. | It keeps the line of the F14 prototype that Troy approved. `menu suggest` names its menu file one way in every line about it. The data folder is the one that you use every day, which is why architecture 6 names the file of a problem relative to it. A failed save needs no new case. | Architecture 6 gains a case for the swap line. `menu new` names the same menu file by its full path when it creates it. The swap line does not say which data folder holds the file, which counts only when you use another data folder with `--data` or `RECIPE_MENU_DATA`. |
| Option 2: both lines name the full path, such as `C:\Users\Troy\recipe-menu\menus\2026-W48.toml`. | The lines name the menu file as `menu new` and `shop` name their files. | The swap line of the F14 prototype changes through the requirement change flow, and architecture 6 gains the case of a failed save of `menu suggest`, both before the F14 test plan. Choices 8 and 9, design 2.2, and its examples change before the mock PR. |

## 5. Consequences

- Architecture 6 names the case in version 4.1. The `Problem` of architecture 5.2 still holds its file relative to the data folder, architecture 5.3 does not change, and ADR-0009 and ADR-0010 stay as Troy accepted them.
- F03's `DataFolder.relative`, F05's `problem_lines` and `stop_at_error`, and F13's `replace_file` do not change.
- The F14 design and test plan stay as Troy approved them in version 1.0. Choices 8 and 9, design 2.2, and the cases of the swap line, of a failed save, and of `LEFT_BEHIND` already follow option 1. No requirement, prototype, or scenario changes: v0.2-S03 already expects the swap line with `menus\2026-W48.toml`. No test or code of an earlier feature changes.
- The tests expect the swap line with `str(Path("menus", "<week>.toml"))`, so they hold on Linux and on Windows (architecture 10).
- A later command that names a file in a way that architecture 6 does not give it, such as F15's `add` with a file that it could not write by its full path, still needs its own change to architecture 6, as ADR-0009 says.

## 6. Related

- Features: F03, F05, F08, F11, F13, F14, F15
- Rules: None
