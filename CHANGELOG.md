---
troy-doc: "changelog"
lang: "en"
version: "0.1"
updated: "2026-11-16"
status: "Up to date with v0.1.0."
mirror: "CHANGELOG.zh-CN.md"
---

# Changelog

## v0.1.0 (2026-11-16)

### Added

- F01: Quantities in recipes can be written with a unit in Chinese or English, or as "to taste"; the tool converts mass to grams and volume to millilitres, scales them, adds them up, and rounds them for the shopping list.
- F02: Every message comes in English and Chinese. The language comes from `--lang`, then from the settings, then English, and a recipe name that lacks the chosen language shows the other one. Chinese text lines up in tables.
- F03: The catalog of shopping categories, ingredients, and tags, with their Chinese and English names, and the pantry list are read from your data folder, with their mistakes reported.
- F04: Recipe files in `recipes/` are read with their names, servings, tags, ingredients, and steps, and each mistake is reported with its file and place; a missing language is a warning.
- F05: The `recipe-menu` command with `--lang`, `--data`, `--help`, and `--version`. It finds your data folder (`--data`, then `RECIPE_MENU_DATA`, then `recipe-menu` in your home folder), reads the settings, and ends with exit code 0, 1, or 2.
- F06: Week menu files in `menus/` are read with their days, meals, dishes, and servings, and `this` and `next` name a week.
- F07: `recipe-menu check` reads every data file and lists the errors and warnings with their places.
- F08: `recipe-menu init` creates a data folder with the settings, the catalog, the pantry, an example recipe, and the empty folders `menus/` and `shopping/`.
- F09: `recipe-menu list` lists your recipes, `--tag` keeps one tag, and `recipe-menu show ID` prints one recipe, scaled with `--servings N`.
- F10: `recipe-menu search WORD...` finds recipes by name, ingredient, or tag, in either language.
- F11: `recipe-menu menu new [WEEK]` creates a week's empty menu file, and `recipe-menu menu show [WEEK]` prints the week as a table by day and meal.
- F12: The week's shopping list is built from its menu: scaled, merged, added up, without the pantry items, grouped by category, and rounded.
- F13: `recipe-menu shop [WEEK]` prints the week's shopping list in the chosen language and saves it as the checklist `shopping/<week>.md`, which you can tick off on your phone.

### Changed

None

### Fixed

None
