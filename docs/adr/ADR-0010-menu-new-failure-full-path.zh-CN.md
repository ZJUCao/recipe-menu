---
troy-doc: "ADR-0010"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-14"
status: "Troy 已于 2026-11-14 批准"
mirror-of: "ADR-0010-menu-new-failure-full-path.md"
---

# ADR-0010：menu new 失败时用完整路径写出它的文件或文件夹

## 1. 状态

已接受。Troy 于 2026-11-14 接受了这个决定，即 F11 设计里 C 点的做法 1。

## 2. 背景

架构 6 说，问题里的文件路径相对于数据文件夹，其他提示用完整路径写出文件或文件夹。ADR-0009 让 `init` 的失败成为第一条规则的例外。它还允许 F11 的 `menu new` 和 F13 的 `shop` 用完整路径写出它们没能写入的文件，而它的第 5 节要求其他情况另外修改架构 6。

F11 的 `menu new` 通过 `create_file` 写出这一周的菜单文件，`create_file` 是 F11 加进 `datafile` 的（F11 设计 3.3）。`create_file` 先列出文件所在的文件夹 `menus\`，这样在两个系统上都拒绝只有大小写不同的名字。这次列出失败时，比如 `menus\` 不存在或者是一个文件，结果里的 `Problem` 的文件是相对于数据文件夹的 `menus`。它的提示就是 `list_menu_weeks` 和 `check` 对这个文件夹给出的提示，比如 `The folder is missing.`（F11 设计 3.3，第 2 步）。`menu new` 把这个问题写成失败时的前两行（F11 设计 2.2）。

ADR-0009 只在第一行写的是 `menu new` 没能写入的文件时涵盖这一行。所以列出失败时会显示 `menus`，而打开、写入或关闭失败时显示菜单文件的完整路径。`menu new` 的其他各行里，写到文件的那几行已经给出完整路径：新建菜单的那一行，以及菜单已存在时的拒绝提示（F11 设计 2.2，F11 原型）。

## 3. 决定

- `menu new` 每次失败时，第一行都用完整路径 `str(context.folder.root / problem.file)` 写出它的文件或文件夹。打开、写入或关闭失败时，那就是菜单文件，比如 `C:\Users\Troy\recipe-menu\menus\2026-W47.toml`。列出失败时，那就是文件夹 `menus\`，比如在 `  The folder is missing.` 上面写出 `C:\Users\Troy\recipe-menu\menus`。
- `Problem` 仍然保存相对于数据文件夹的文件（架构 5.2 和 5.3，F11 设计 3.3）。只有 `menu new` 写出的那一行给出完整路径。
- 读取函数或检查报告的每个问题，仍然按架构 6 写相对路径。所以 `check` 和 `menu show` 仍然把缺少的 `menus` 文件夹写成 `menus`。
- `init` 的情况（ADR-0009）和 F13 的 `shop` 的情况（它没能写入的文件）保持不变。

## 4. 考虑过的方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 做法 1：文件或文件夹的完整路径。已选。 | 无论什么原因，你都能看到 `menu new` 在磁盘上的哪里失败。第一行写路径的方式和 `menu new` 的其他各行以及 `init` 的失败一样。`Problem`、`create_file` 和每个读取函数都保持不变。 | 架构 6 多了一种情况。缺少 `menus\` 时，`menu new` 显示完整路径，而 `check` 和 `menu show` 显示 `menus`。 |
| 做法 2：像 `check` 和 `list_menu_weeks` 那样，用相对于数据文件夹的路径写出文件夹，只有 `menu new` 没能写入的文件才用完整路径。 | 架构 6 保持不变。缺少 `menus\` 时，`menu new`、`menu show` 和 `check` 都显示 `menus`。 | 失败的第一行会因为一种原因是相对路径，因为另一种原因是完整路径。F11 设计的选择 4、2.2 里失败时的各行，以及 2.2 示例的最后一次运行，都要在 mock PR 之前修改。 |

## 5. 影响

- 架构 6 在 3.1 版写明这种情况。架构 5.2 和 5.3 不变，ADR-0009 保持 Troy 接受时的样子。
- F05 的 `problem_lines` 和 `stop_at_error`、F06 的 `list_menu_weeks`，以及 F11 的 `create_file` 都不变。`menu new` 和 `init` 一样不用 `problem_lines` 和 `stop_at_error` 写出失败，因为失败的最后一行是 `CHANGED_NOTHING` 或 `LEFT_BEHIND`，而不是 `RUN_CHECK`（F11 设计 2.2）。
- F11 设计的选择 4、2.2 里失败时的各行，以及 2.2 示例的最后一次运行，都保持 Troy 在 1.0 版批准的样子。不改任何需求、原型或场景，也不改之前功能的任何测试或代码。F11 的测试计划可以检查列出失败时的完整路径，就像 F11 设计 2.2 示例的最后一次运行那样。
- F13 的 `shop` 保持架构 6 给它的情况，即它没能写入的文件。`shop` 替换它那一周的文件，所以不能通过 `create_file` 写入，因为 `create_file` 拒绝已经存在的条目。它的写入经过同一文件夹里的临时文件（架构 6），不需要列出文件夹。所以 `create_file` 不会让 `shop` 遇到没能列出文件夹的情况。
- 以后的写文件功能，比如 v0.2 里 F15 的 `add`，要用完整路径写出它的文件或文件夹，仍然需要再改一次架构 6，就像 ADR-0009 说的那样。写入通过 `create_file` 进行时也是这样（F11 设计第 2 节）。

## 6. 相关

- 功能：F05、F06、F08、F11、F13、F15
- 规则：无
