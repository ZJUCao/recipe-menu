---
troy-doc: "ADR-0001"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-10"
status: "Troy 已于 2026-11-10 批准"
mirror-of: "ADR-0001-python-standard-library.md"
---

# ADR-0001：Python 3.13，运行时只用标准库

## 1. 状态

已接受。Troy 于 2026-11-10 批准 `docs/architecture.md`，接受了这条记录。

## 2. 背景

troy-mode 有 Python 和 C/C++ 两个语言包。这个工具读取小的文本文件，用两种语言显示文字，把数量加起来，并计算 ISO 周。它必须在 Troy 的 Windows 11 电脑上从任何文件夹运行，在 CI 的 Linux 上通过测试，并且从不使用网络。每个新的第三方包都要经过架构师审查并由 Troy 决定（R16），而且每个包都会进入同一系列所有成员共用的锁定文件。

## 3. 决定

工具用 Python 3.13 或更新版本编写，使用 troy-mode 的 Python 语言包。运行时只用标准库：`tomllib` 读数据文件，`datetime` 算 ISO 周，`fractions` 表示数量，`unicodedata` 给出字符宽度，`pathlib` 处理路径；v0.2 里再用 `random` 做推荐，用 `subprocess` 打开编辑器。构建和检查工具就是语言包带来的那些：hatchling、coverage、mypy、pytest、ruff 和 uv。以后的功能如果想在运行时用某个包，要走 R16。

## 4. 考虑过的方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| Python，只用标准库 | 上面每项需要标准库里都有。没有要审查、锁定或更新的运行时包。语言包的工具在 Windows 和 Linux 上检查它。 | Python 启动要几十毫秒，这段时间算进 PT01。`tomllib` 是纯 Python 实现，解析比 C 写的解析器慢（ADR-0002）。 |
| Python 加运行时包，比如更快的 TOML 解析器、表格库和命令行库 | 表格和命令行要写的代码更少。 | 每个包都要 Troy 决定。这些包的提示是英文的，所以双语规则仍然需要我们自己的代码（ADR-0005）。 |
| C++，使用 C/C++ 语言包 | 启动快，解析快。 | 需要一个 TOML 库，这是一个依赖。UTF-8 控制台输出、显示宽度和日期都要多写很多代码。每个功能的编写和审查都更费时间。 |

## 5. 影响

- `pyproject.toml` 不列任何运行时依赖，锁定文件只在语言包的工具变化时才变。
- 只要能运行 Python 3.13 的地方，工具就能运行，除了工具本身不需要再装别的（ADR-0006）。
- Python 的启动时间和 `tomllib` 的速度是 PT01 要盯住的开销（ADR-0002）。

## 6. 相关

- 功能：F01 到 F16
- 规则：R11、R16
