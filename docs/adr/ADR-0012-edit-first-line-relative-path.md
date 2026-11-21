---
troy-doc: "ADR-0012"
lang: "en"
version: "1.0"
updated: "2026-11-21"
status: "Approved by Troy on 2026-11-21"
mirror: "ADR-0012-edit-first-line-relative-path.zh-CN.md"
---

# ADR-0012: The first line of edit names the recipe's file relative to the data folder

## 1. Status

Accepted. Troy accepted the decision on 2026-11-21, as option 1 of point B of the F16 design.

## 2. Context

Architecture 6 says that a problem names its file relative to the data folder, with the system's separator, and that other messages name a file or a folder by its full path. ADR-0009 and ADR-0010 let `init`, `menu new`, and `shop` name a file that they could not write by its full path, and ADR-0011 lets the swap line of `menu suggest` name its menu file relative to the data folder. Section 5 of ADR-0009 asks every later case for its own change to architecture 6.

Once the editor has started, F16's `edit` writes a first line that says which file it opened in which editor (F16 design, choices 4 and 8). The F16 prototype, which Troy approved, writes it as `Opened recipes\mapo-tofu.toml in Notepad. Close Notepad when you are done.`. The line is not a problem, so under architecture 6 as it stood it would name the full path, such as `Opened C:\Users\Troy\recipe-menu\recipes\mapo-tofu.toml in Notepad. …`.

The lines that follow it name the same file as problems do, relative to the data folder: the report of the check after the editor, and the three lines of `stop_at_error` when a listing of `recipes/` has an error. No other line of `edit` names a file. `UNKNOWN_ID`, `GONE`, `EDIT_AGAIN`, and the count lines name the ID, and the lines about the editor name the program as the settings write it.

## 3. Decision

- The first line of `edit`, `OPENED_IN_NOTEPAD` or `OPENED_IN_EDITOR`, names the recipe's file as a problem names its file: relative to the data folder, with the system's separator, `str(context.folder.relative(path))`. That is `recipes\mapo-tofu.toml` on Windows and `recipes/mapo-tofu.toml` on Linux.
- The editor gets the full path of the file, `context.folder.recipe_file(recipe_id)`, as its last argument, so it opens the right file whatever the current folder is.
- The report of the check and the lines of `stop_at_error` are problems, so they keep the relative path, as architecture 6 already says. They need no new case.
- The cases of `init` (ADR-0009), `menu new` (ADR-0010), `shop`, and `menu suggest` (ADR-0011) stay as they are.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| Option 1: the first line names the recipe's file relative to the data folder, as the prototype writes it. Chosen. | It keeps the line of the F16 prototype that Troy approved. The first line names the file as the lines of the check below it do, so one run of `edit` names the recipe one way. The data folder is the one that you use every day, which is why architecture 6 names the file of a problem relative to it. | Architecture 6 gains a case for the line. Two drawbacks that the design did not list: the line does not say which data folder holds the file, which counts only when you use another data folder with `--data` or `RECIPE_MENU_DATA`. And the path is relative to the data folder, not to the current folder, so it opens the file from PowerShell only when the data folder is the current folder. |
| Option 2: the first line names the full path, such as `C:\Users\Troy\recipe-menu\recipes\mapo-tofu.toml`, as architecture 6 gives a message that is not a problem. | Architecture 6 needs no change. The line says which data folder holds the file, and the path works from any folder. | The first lines of both sections of the F16 prototype change through the requirement change flow before the F16 test plan, and choice 8, design 2.2, and the examples change before the mock PR. The first line names the file one way and the check below it another way. |

## 5. Consequences

- Architecture 6 names the case in version 5.2. The `Problem` of architecture 5.2 still holds its file relative to the data folder, architecture 5.3 does not change, and ADR-0009, ADR-0010, and ADR-0011 stay as Troy accepted them.
- F03's `DataFolder.relative` and `DataFolder.recipe_file`, F05's `problem_lines` and `stop_at_error`, and F15's `problem_block` do not change.
- The F16 design and test plan stay as Troy approved them in version 1.0. Choice 8, the placeholder `file` of design 2.2, and the cases of the first line already follow option 1. No requirement, prototype, or scenario changes: the v0.2 scenarios of `edit` already expect `recipes\<id>.toml` in the first line. No test or code of an earlier feature changes.
- The tests expect the first line with `str(Path("recipes", "<id>.toml"))`, so they hold on Linux and on Windows (architecture 10).
- A later message that names a file in a way that architecture 6 does not give it still needs its own change to architecture 6, as ADR-0009 says.

## 6. Related

- Features: F03, F05, F15, F16
- Rules: None
