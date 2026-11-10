# Prototype: edit a recipe

Feature: F16, in v0.2. A PowerShell session in Windows Terminal. The data folder holds the example data in `example-data.md`. The settings name no editor, so `edit` uses Notepad. With `editor = "code --wait"` in the settings, it uses VS Code.

## An edit that leaves a mistake

Troy changes ingredient 3 of `mapo-tofu` to 豆瓣酱, saves, and closes Notepad.

```text
PS> recipe-menu edit mapo-tofu
Opened recipes\mapo-tofu.toml in Notepad. Close Notepad when you are done.

Checked mapo-tofu: 1 error.
  recipes\mapo-tofu.toml, ingredient 3
    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.
Run "recipe-menu edit mapo-tofu" to fix it.
PS> $LASTEXITCODE
1
```

## A clean edit, in Chinese

```text
PS> recipe-menu edit mapo-tofu --lang zh
已用记事本打开 recipes\mapo-tofu.toml。改完后关闭记事本。

已检查 mapo-tofu：没有错误。
```

## An unknown ID

```text
PS> recipe-menu edit mapo
No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.
PS> $LASTEXITCODE
1
```
