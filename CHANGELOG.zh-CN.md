---
troy-doc: "changelog"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-16"
status: "已更新到 v0.1.0。"
mirror-of: "CHANGELOG.md"
---

# 更新日志

## v0.1.0 (2026-11-16)

### 新增

- F01：菜谱里的数量可以用中文或英文的单位来写，也可以写“适量”；工具会把质量换算成克、体积换算成毫升，按份数换算、相加，并为购物清单取整。
- F02：每条提示都有英文和中文。语言先看 `--lang`，再看设置，最后用英文；菜谱名缺少所选语言时显示另一种语言。中文在表格里能对齐。
- F03：从数据文件夹读取目录（购物分类、食材和标签，以及它们的中英文名称）和常备清单，并报告其中的错误。
- F04：读取 `recipes/` 里的菜谱文件，包括名称、份数、标签、食材和步骤，并报告每个错误及其文件和位置；缺少一种语言是警告。
- F05：`recipe-menu` 命令，带 `--lang`、`--data`、`--help` 和 `--version`。它找到你的数据文件夹（先看 `--data`，再看 `RECIPE_MENU_DATA`，最后用主文件夹里的 `recipe-menu`），读取设置，并以退出码 0、1 或 2 结束。
- F06：读取 `menus/` 里的周菜单文件，包括各天、各餐、各道菜和份数；`this` 和 `next` 表示某一周。
- F07：`recipe-menu check` 读取每个数据文件，列出错误和警告及其位置。
- F08：`recipe-menu init` 创建数据文件夹，里面有设置、目录、常备清单、一个示例菜谱，以及空文件夹 `menus/` 和 `shopping/`。
- F09：`recipe-menu list` 列出你的菜谱，`--tag` 只保留一个标签；`recipe-menu show ID` 打印一个菜谱，可用 `--servings N` 换算份数。
- F10：`recipe-menu search WORD...` 按菜谱名、食材或标签查找菜谱，中英文都可以。
- F11：`recipe-menu menu new [WEEK]` 创建一周的空菜单文件，`recipe-menu menu show [WEEK]` 把这一周打印成按天和餐排列的表。
- F12：根据一周的菜单生成购物清单：换算、合并、相加、去掉常备食材、按分类分组、取整。
- F13：`recipe-menu shop [WEEK]` 用所选语言打印这一周的购物清单，并保存为勾选清单 `shopping/<week>.md`，可以在手机上打勾。

### 修改

无

### 修复

无
