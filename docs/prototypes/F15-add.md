# Prototype: add a recipe

Feature: F15, in v0.2. A PowerShell session in Windows Terminal. The data folder holds the example data in `example-data.md`. Troy's answers follow each colon. An empty line ends a list. `add` asks for no notes; add notes with `edit`.

## In Chinese, with one wrong answer

```text
PS> recipe-menu add --lang zh
菜谱 ID（也是文件名）：garlic-broccoli
中文名：蒜蓉西兰花
英文名：Garlic broccoli
份数 [2]：
标签，用逗号分隔：快手, 素
食材，每行一个，写“名称 数量”，空行结束：
  西兰花 300 g
  大蒜 4 瓣
  橄榄油 1 tbsp
  目录里没有“橄榄油”。请输入目录里的名称，或先把它加入目录后再运行 add。
  食用油 1 tbsp
  盐 适量

中文步骤，每行一步，空行结束：
  西兰花切小朵，焯水 1 分钟，捞出沥干。
  大蒜切末，热油爆香。
  倒入西兰花翻炒，加盐调味。

英文步骤，每行一步，空行结束（可以不写）：
  Cut the broccoli into florets. Blanch them for 1 minute and drain.
  Mince the garlic, and fry it in the hot oil until fragrant.
  Add the broccoli, stir-fry it, and season with salt.

已保存 C:\Users\Troy\recipe-menu\recipes\garlic-broccoli.toml。检查没有发现问题。
```

## An ID that exists

```text
PS> recipe-menu add
Recipe ID (also the file name): tomato-egg
The recipe tomato-egg already exists. Enter another ID, or run "recipe-menu edit tomato-egg".
Recipe ID (also the file name):
```

An empty answer to the first question ends `add` without writing a file.
