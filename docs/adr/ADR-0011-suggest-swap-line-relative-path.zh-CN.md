---
troy-doc: "ADR-0011"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-17"
status: "Troy 已于 2026-11-17 批准"
mirror-of: "ADR-0011-suggest-swap-line-relative-path.md"
---

# ADR-0011：menu suggest 的换菜提示用相对于数据文件夹的路径写出它的文件

## 1. 状态

已接受。Troy 于 2026-11-17 接受了这个决定，即 F14 设计里 D 点的做法 1。

## 2. 背景

架构 6 说，问题里的文件路径相对于数据文件夹，使用系统的分隔符；其他提示用完整路径写出文件或文件夹。ADR-0009 和 ADR-0010 允许 `init`、`menu new` 和 `shop` 用完整路径写出它们没能写入的文件。ADR-0009 的第 5 节要求以后的每种情况另外修改架构 6。

F14 的 `menu suggest` 在两行里写到这一周的菜单文件（F14 设计，选择 8 和 9）：

- 换菜提示，它出现在第一次填写的输出末尾，以及没有空餐的那一周的输出里。Troy 批准的 F14 原型把它写成 `To swap a dish, empty its meal in menus\2026-W48.toml, then run "recipe-menu menu suggest 2026-W48" again.`。这一行不是问题，所以按架构 6 它要写完整路径。
- 保存失败时的第一行，它写出 `replace_file` 给出的 `Problem`。架构 6 本来就让它像问题保存的那样，写相对于数据文件夹的路径。

所以按原来的架构 6，`menu suggest` 会用两种方式写出它的菜单文件：换菜提示里用完整路径，这也会改掉原型里的那一行；保存失败后用相对于数据文件夹的路径。

第三行 `LEFT_BEHIND` 写出 `replace_file` 没能删除的临时文件 `menus/<week>.toml.tmp`。它也不是问题，而 `shop` 用完整路径写出它的临时文件。

## 3. 决定

- `menu suggest` 的换菜提示像问题那样写出这一周的菜单文件：相对于数据文件夹，使用系统的分隔符，即 `str(context.folder.relative(path))`。在 Windows 上是 `menus\2026-W48.toml`，在 Linux 上是 `menus/2026-W48.toml`。
- `menu suggest` 保存失败时，第一行按问题保存的样子写出文件，比如在 `  The file cannot be written: access is denied.` 上面写出 `menus\2026-W48.toml`。架构 6 对问题本来就是这样规定的，所以这里不需要新的情况。`CANNOT_FILL` 的第一行也不需要，因为它也是问题。
- `LEFT_BEHIND` 用完整路径写出临时文件，比如 `C:\Users\Troy\recipe-menu\menus\2026-W48.toml.tmp`，这是架构 6 对不是问题的提示的规定。
- `init`（ADR-0009）、`menu new`（ADR-0010）和 `shop` 的情况保持不变。

## 4. 考虑过的方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 做法 1：换菜提示和保存失败都用相对于数据文件夹的路径写出菜单文件。已选。 | 保留了 Troy 批准的 F14 原型里的那一行。`menu suggest` 写到菜单文件的每一行都用同一种方式。数据文件夹是你每天在用的那个，所以架构 6 让问题里的文件路径相对于它。保存失败不需要新的情况。 | 架构 6 为换菜提示多了一种情况。`menu new` 创建同一个菜单文件时写的是完整路径。换菜提示不说明文件在哪个数据文件夹里，只有你用 `--data` 或 `RECIPE_MENU_DATA` 使用别的数据文件夹时，这一点才有影响。 |
| 做法 2：两行都写完整路径，比如 `C:\Users\Troy\recipe-menu\menus\2026-W48.toml`。 | 这两行写菜单文件的方式和 `menu new`、`shop` 写它们的文件一样。 | F14 原型里的换菜提示要走需求变更流程修改，架构 6 还要加上 `menu suggest` 保存失败的情况，两者都要在 F14 测试计划之前完成。选择 8 和 9、设计 2.2 及其示例都要在 mock PR 之前修改。 |

## 5. 影响

- 架构 6 在 4.1 版写明这种情况。架构 5.2 里的 `Problem` 仍然保存相对于数据文件夹的文件，架构 5.3 不变，ADR-0009 和 ADR-0010 保持 Troy 接受时的样子。
- F03 的 `DataFolder.relative`、F05 的 `problem_lines` 和 `stop_at_error`，以及 F13 的 `replace_file` 都不变。
- F14 的设计和测试计划保持 Troy 在 1.0 版批准的样子。选择 8 和 9、设计 2.2，以及换菜提示、保存失败和 `LEFT_BEHIND` 的用例，本来就按做法 1。不改任何需求、原型或场景：v0.2-S03 本来就预期换菜提示里写 `menus\2026-W48.toml`。之前功能的测试和代码都不变。
- 测试用 `str(Path("menus", "<week>.toml"))` 预期换菜提示里的文件，所以在 Linux 和 Windows 上都成立（架构 10）。
- 以后的命令如果要用架构 6 没有给它的方式写出文件，比如 F15 的 `add` 用完整路径写出它没能写入的文件，仍然需要再改一次架构 6，就像 ADR-0009 说的那样。

## 6. 相关

- 功能：F03、F05、F08、F11、F13、F14、F15
- 规则：无
