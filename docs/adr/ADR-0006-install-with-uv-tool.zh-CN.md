---
troy-doc: "ADR-0006"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-10"
status: "Troy 已于 2026-11-10 批准"
mirror-of: "ADR-0006-install-with-uv-tool.md"
---

# ADR-0006：用 uv tool 安装 recipe-menu

## 1. 状态

已接受。Troy 于 2026-11-10 批准 `docs/architecture.md`，接受了这条记录。

## 2. 背景

在 PowerShell 里，`recipe-menu` 必须能从任何文件夹运行，怎么安装由总体架构说明（需求 7）。troy-mode 的 Python 规定不允许 `.venv` 文件夹，而开发环境是一个 mamba 环境，其中的代码随 Troy 或 troy-mode 切换的每个分支而变。uv 已经在这个环境里。仓库是 `git@github.com:ZJUCao/recipe-menu.git`；Troy 验收一个版本时，troy-mode 会创建带标签（比如 `v0.1.0`）的 GitHub 发布。

## 3. 决定

F05 在 `pyproject.toml` 里声明控制台脚本 `recipe-menu = "recipe_menu.cli:main"`。要安装一个已验收的版本，Troy 在一个能用 uv 的 PowerShell 里（比如激活了开发环境的那个）运行下面的命令，只需一次：

```text
uv tool install --managed-python --python 3.13 "git+ssh://git@github.com/ZJUCao/recipe-menu.git@v0.1.0"
uv tool update-shell
```

第一条命令为工具建立它自己的环境，使用由 uv 管理的 Python，并把 `recipe-menu.exe` 放进 uv 存放工具命令的文件夹。第二条命令把那个文件夹加进 Troy 的 PATH。之后打开的 PowerShell 在任何文件夹都能找到 `recipe-menu`。要换到更新的版本，Troy 用新标签加 `--force` 再运行第一条命令。要在发布前试用 `main`，Troy 在 `main` 的干净检出上运行它，加 `--force`，并用仓库文件夹代替 Git 地址。

## 4. 考虑过的方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 用 `uv tool install` 从发布标签安装 | uv 已经有了。工具有自己的环境和 Python，所以开发环境或分支的变化从不会弄坏已安装的命令。一个标签装的正是 Troy 验收过的内容。 | 第一次安装要下载一个 Python 和构建后端。更新需要一条命令。 |
| 在开发环境里做可编辑安装，再加一个 PowerShell 配置文件里的函数 | 不需要第二个环境。 | 命令运行的是当前检出的分支，包括每个调用都会报错的 mock。只有激活环境后才能用，或者要改配置文件。 |
| pipx | 做这件事的常用工具。 | 还要再装一个工具，而 uv 已经能代替它。 |
| 用 PyInstaller 打包成单个可执行文件 | 完全不需要 Python。 | 新的构建依赖、很大的文件，每次发布都多一个构建步骤。 |

## 5. 影响

- 已安装的命令只有从 Troy 安装的那个版本起，才算“可以在 Troy 的设备上使用”，这和 R13 的状态标签一致。
- 安装时会用一次网络，下载代码、Python 和 hatchling。工具本身从不用网络。
- 版本测试计划包括在 Troy 的电脑上这样安装发布版本，并在 Windows PowerShell 5.1 和 PowerShell 7 里运行 `recipe-menu --version`。

## 6. 相关

- 功能：F05
- 规则：R13
