---
troy-doc: "ADR-0012"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-21"
status: "Troy 已于 2026-11-21 批准"
mirror-of: "ADR-0012-edit-first-line-relative-path.md"
---

# ADR-0012：edit 的第一行用相对于数据文件夹的路径写出菜谱文件

## 1. 状态

已接受。Troy 于 2026-11-21 接受了这个决定，即 F16 设计里 B 点的做法 1。

## 2. 背景

架构 6 说，问题里的文件路径相对于数据文件夹，使用系统的分隔符；其他提示用完整路径写出文件或文件夹。ADR-0009 和 ADR-0010 允许 `init`、`menu new` 和 `shop` 用完整路径写出它们没能写入的文件，ADR-0011 允许 `menu suggest` 的换菜提示用相对于数据文件夹的路径写出它的菜单文件。ADR-0009 的第 5 节要求以后的每种情况另外修改架构 6。

编辑器启动后，F16 的 `edit` 写出第一行，说明它用哪个编辑器打开了哪个文件（F16 设计，选择 4 和 8）。Troy 批准的 F16 原型把它写成 `Opened recipes\mapo-tofu.toml in Notepad. Close Notepad when you are done.`。这一行不是问题，所以按原来的架构 6，它要写完整路径，比如 `Opened C:\Users\Troy\recipe-menu\recipes\mapo-tofu.toml in Notepad. …`。

它后面的几行像问题那样，用相对于数据文件夹的路径写出同一个文件：编辑器之后的检查报告，以及列出 `recipes/` 出错时 `stop_at_error` 的三行。`edit` 的其他行都不写文件。`UNKNOWN_ID`、`GONE`、`EDIT_AGAIN` 和计数行写的是 ID，讲编辑器的几行写的是设置里写的程序。

## 3. 决定

- `edit` 的第一行，即 `OPENED_IN_NOTEPAD` 或 `OPENED_IN_EDITOR`，像问题那样写出菜谱文件：相对于数据文件夹，使用系统的分隔符，即 `str(context.folder.relative(path))`。在 Windows 上是 `recipes\mapo-tofu.toml`，在 Linux 上是 `recipes/mapo-tofu.toml`。
- 编辑器拿到文件的完整路径 `context.folder.recipe_file(recipe_id)`，作为它的最后一个参数，所以不管当前文件夹是哪个，它都打开正确的文件。
- 检查报告和 `stop_at_error` 的几行都是问题，所以它们保持相对路径，这是架构 6 本来就规定的。它们不需要新的情况。
- `init`（ADR-0009）、`menu new`（ADR-0010）、`shop` 和 `menu suggest`（ADR-0011）的情况保持不变。

## 4. 考虑过的方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 做法 1：第一行像原型那样，用相对于数据文件夹的路径写出菜谱文件。已选。 | 保留了 Troy 批准的 F16 原型里的那一行。第一行写文件的方式和下面检查的几行一样，所以运行一次 `edit`，菜谱只有一种写法。数据文件夹是你每天在用的那个，所以架构 6 让问题里的文件路径相对于它。 | 架构 6 为这一行多了一种情况。设计没有列出的两个缺点：这一行不说明文件在哪个数据文件夹里，只有你用 `--data` 或 `RECIPE_MENU_DATA` 使用别的数据文件夹时，这一点才有影响。而且路径相对于数据文件夹，而不是当前文件夹，所以只有当前文件夹就是数据文件夹时，在 PowerShell 里用这个路径才能打开文件。 |
| 做法 2：第一行写完整路径，比如 `C:\Users\Troy\recipe-menu\recipes\mapo-tofu.toml`，这是架构 6 对不是问题的提示的规定。 | 架构 6 不用改。这一行说明文件在哪个数据文件夹里，路径在任何文件夹里都能用。 | F16 原型两节的第一行要走需求变更流程修改，在 F16 测试计划之前完成；选择 8、设计 2.2 及其示例要在 mock PR 之前修改。第一行和下面的检查用两种方式写出同一个文件。 |

## 5. 影响

- 架构 6 在 5.2 版写明这种情况。架构 5.2 里的 `Problem` 仍然保存相对于数据文件夹的文件，架构 5.3 不变，ADR-0009、ADR-0010 和 ADR-0011 保持 Troy 接受时的样子。
- F03 的 `DataFolder.relative` 和 `DataFolder.recipe_file`、F05 的 `problem_lines` 和 `stop_at_error`，以及 F15 的 `problem_block` 都不变。
- F16 的设计和测试计划保持 Troy 在 1.0 版批准的样子。选择 8、设计 2.2 的占位符 `file`，以及第一行的用例，本来就按做法 1。不改任何需求、原型或场景：v0.2 里 `edit` 的场景本来就预期第一行写 `recipes\<id>.toml`。之前功能的测试和代码都不变。
- 测试用 `str(Path("recipes", "<id>.toml"))` 预期第一行里的文件，所以在 Linux 和 Windows 上都成立（架构 10）。
- 以后的提示如果要用架构 6 没有给它的方式写出文件，仍然需要再改一次架构 6，就像 ADR-0009 说的那样。

## 6. 相关

- 功能：F03、F05、F15、F16
- 规则：无
