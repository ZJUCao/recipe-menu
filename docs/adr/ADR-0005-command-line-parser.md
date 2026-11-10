---
troy-doc: "ADR-0005"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "ADR-0005-command-line-parser.zh-CN.md"
---

# ADR-0005: A command-line parser of our own, without argparse

## 1. Status

Accepted. Troy accepted it on 2026-11-10 by approving `docs/architecture.md`.

## 2. Context

The F05 prototype fixes the help text in both languages and the errors for a wrong command line, such as `--lang must be en or zh, not "fr".` and `Unknown command "cook".`, each with exit code 2. `--lang` may come anywhere on the line, as in `recipe-menu --help --lang zh`, and the error must be in that language. The grammar is small: one or two command words, positional arguments, the options `--lang`, `--data`, `--tag`, and `--servings` with a value, and the flags `--help` and `--version`. `argparse` writes its own English usage and error text, such as `error: argument --lang: invalid choice: 'fr'`, and its own help layout.

## 3. Decision

`cli` parses the command line itself. Each `Command` declares its words, its positional arguments, and its options. The parser first looks for `--lang`, so that its own errors come out in the chosen language. It then finds the command, checks the arguments and options against the command's declaration, and raises `UsageError` with a `Message` for anything wrong. The help comes from the commands' help lines, in the layout of the F05 prototype. Options take their value as the next argument. The parser accepts no abbreviations.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| A parser of our own in `cli` | Every message and the help come from `Message` values in both languages. Every command parses options the same way. | F05 writes and tests a few hundred lines, within R04 and R06. |
| `argparse`, with its `error` method overridden and a help text of our own | In the standard library. Handles many option styles. | Its errors reach `error` as finished English text, so turning them into our messages means matching that text, which can change between Python versions. Abbreviations and the help layout need turning off. |
| click or typer | Short command definitions. | A dependency under R16. Their messages are English too, with the same problem as `argparse`. |

## 5. Consequences

- The help and the usage errors look exactly as the F05 prototype shows, in both languages.
- A new option of a command is declared in its `Command`, and the parser handles it with no change to `cli`.
- Forms that `argparse` accepts and the prototypes never show, such as `--lang=zh` or `-l zh`, are not supported unless F05's design adds them.

## 6. Related

- Features: F05, and every command feature
- Rules: R04, R06, R16
