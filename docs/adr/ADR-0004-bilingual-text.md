---
troy-doc: "ADR-0004"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "ADR-0004-bilingual-text.zh-CN.md"
---

# ADR-0004: Messages, display width, and the console

## 1. Status

Accepted. Troy accepted it on 2026-11-10 by approving `docs/architecture.md`.

## 2. Context

Every message exists in English and in Chinese (requirements 7), and F02 "holds every message of the tool in English and Chinese". The prototypes show dozens of messages, spread over 16 features, and the designs will add more. One file for all of them would grow with every feature toward the 500-line limit (R06), and every feature after F02 would have to change F02's file. Tables must line up with Chinese text, and Chinese must show correctly in Windows Terminal whatever the console code page is, without a change to a Windows setting.

## 3. Decision

- **Messages.** A message is a `Message` value from `text`, with an English and a Chinese template that have the same `{name}` placeholders. Creating one without both languages, or with different placeholders, fails at once, so any test that imports the module catches it. Each module keeps its own messages in its `messages.py`. `text` holds the shared ones, such as the hint to run `--help`. This is how the architecture reads F02's "holds every message": every message is a value of F02's type, and that type cannot exist in one language only.
- **Names of values.** A value's names in both languages live beside its type: unit names in `units`, meal names in `settings`, and day and month names in `menus`. `units` keeps its names as plain data, because it comes before `text`.
- **Width.** A character whose East Asian width is W (wide) or F (fullwidth) takes two columns. A combining mark takes none. Every other character takes one, including the ambiguous ones such as `“` and `×`, because Windows Terminal draws those one column wide. Only `text` measures width.
- **Console.** At start, `cli` asks `text` to set stdout and stderr to UTF-8. On a Windows console, Python writes through the console's Unicode interface, so the code page does not matter. Redirected output is UTF-8.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| `Message` constants in each module's `messages.py` | Each feature adds only its own messages. A missing language fails in that feature's tests. mypy checks every message name. | The messages of the tool are spread over many files. |
| One message file in `text` | One place to read every message. | It grows toward R06's limit. Every later feature changes F02's file, which F02 has already implemented. |
| gettext with `.po` files | The standard approach for translations. | Needs a compile step and its tools. The English text is the key, so changing a word breaks the translation. Nothing stops a missing translation at import time. |
| TOML message files | Messages outside the code. | Names are strings, so a typo shows only at run time. A loader is more code. |

## 5. Consequences

- Each feature's test plan can cover its messages in both languages with no help from F02.
- Table columns line up in Windows Terminal. Another terminal that draws ambiguous characters two columns wide would misalign the lines that hold them.
- When PowerShell pipes or redirects the output, it decodes the UTF-8 bytes with `[Console]::OutputEncoding`, so Chinese survives a pipe only when that encoding is UTF-8. Output in the terminal and the saved shopping list do not depend on this.

## 6. Related

- Features: F01, F02, F05, and every feature that shows text
- Rules: R06
