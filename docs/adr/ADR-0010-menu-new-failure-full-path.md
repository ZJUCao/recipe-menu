---
troy-doc: "ADR-0010"
lang: "en"
version: "1.0"
updated: "2026-11-14"
status: "Approved by Troy on 2026-11-14"
mirror: "ADR-0010-menu-new-failure-full-path.zh-CN.md"
---

# ADR-0010: A failure of menu new names its file or folder by its full path

## 1. Status

Accepted. Troy accepted the decision on 2026-11-14, as option 1 of point C of the F11 design.

## 2. Context

Architecture 6 says that a problem names its file relative to the data folder, and that other messages name a file or a folder by its full path. ADR-0009 made a failure of `init` an exception to the first rule. It also let F11's `menu new` and F13's `shop` name a file that they could not write by its full path, and its section 5 asks any other case for its own change to architecture 6.

F11's `menu new` writes the week's menu file through `create_file`, which F11 adds to `datafile` (F11 design 3.3). `create_file` first lists the file's folder, `menus\`, so that it refuses a name that differs only in case on both systems. When that listing fails, such as when `menus\` is missing or is a file, the result's `Problem` has the file `menus`, relative to the data folder. Its message is the one that `list_menu_weeks` and `check` give for the folder, such as `The folder is missing.` (F11 design 3.3, step 2). `menu new` writes that problem as the first two lines of a failure (F11 design 2.2).

ADR-0009 covers that first line only when the line names a file that `menu new` could not write. So a failed listing would show `menus`, while a failed open, write, or close shows the full path of the menu file. The other lines of `menu new` that name a file already give its full path: the line of a new menu and the refusal of an existing menu (F11 design 2.2, F11 prototype).

## 3. Decision

- The first line of every failure of `menu new` names its file or folder by its full path, `str(context.folder.root / problem.file)`. For a failed open, write, or close, that is the menu file, such as `C:\Users\Troy\recipe-menu\menus\2026-W47.toml`. For a failed listing, that is the folder `menus\`, such as `C:\Users\Troy\recipe-menu\menus` above `  The folder is missing.`.
- The `Problem` still holds its file relative to the data folder (architecture 5.2 and 5.3, F11 design 3.3). Only the line that `menu new` writes gives the full path.
- Every problem that a reader or a check reports keeps the relative path of architecture 6. So `check` and `menu show` still name a missing `menus` folder as `menus`.
- The case of `init` (ADR-0009) and the case of F13's `shop`, a file that it could not write, stay as they are.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| Option 1: the full path of the file or the folder. Chosen. | You see where on the disk `menu new` failed, whatever the cause. The first line names paths the way the other lines of `menu new` and a failure of `init` do. The `Problem`, `create_file`, and every reader stay as they are. | Architecture 6 gains a case. A missing `menus\` shows a full path in `menu new`, but `menus` in `check` and `menu show`. |
| Option 2: the folder relative to the data folder, as `check` and `list_menu_weeks` name it, and the full path only for a file that `menu new` could not write. | Architecture 6 stays as it is. A missing `menus\` shows `menus` in `menu new`, `menu show`, and `check`. | The first line of a failure is a relative path for one cause and a full path for another. F11 design choice 4, the failure lines of 2.2, and the last run of its example change before the mock PR. |

## 5. Consequences

- Architecture 6 names the case in version 3.1. Architecture 5.2 and 5.3 do not change, and ADR-0009 stays as Troy accepted it.
- F05's `problem_lines` and `stop_at_error`, F06's `list_menu_weeks`, and F11's `create_file` do not change. `menu new` writes its failure without `problem_lines` and `stop_at_error`, as `init` does, because its last line is `CHANGED_NOTHING` or `LEFT_BEHIND`, not `RUN_CHECK` (F11 design 2.2).
- F11 design choice 4, the failure lines of 2.2, and the last run of its example stay as Troy approved them in version 1.0. No requirement, prototype, or scenario changes, and no test or code of an earlier feature changes. F11's test plan can check the full path of a failed listing, as the last run of the example of F11 design 2.2 does.
- F13's `shop` keeps the case that architecture 6 gives it, a file that it could not write. `shop` replaces the file of its week, so it cannot write through `create_file`, which refuses an entry that is already there. Its write goes through a temporary file in the same folder (architecture 6), which needs no listing. So `create_file` does not bring `shop` the case of a folder that it could not list.
- A later write, such as F15's `add` in v0.2, still needs its own change to architecture 6 to name its file or folder by its full path, as ADR-0009 says. That holds also when the write goes through `create_file` (F11 design, section 2).

## 6. Related

- Features: F05, F06, F08, F11, F13, F15
- Rules: None
