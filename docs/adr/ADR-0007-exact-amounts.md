---
troy-doc: "ADR-0007"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "ADR-0007-exact-amounts.zh-CN.md"
---

# ADR-0007: Exact amounts with fractions

## 1. Status

Accepted. Troy accepted it on 2026-11-10 by approving `docs/architecture.md`.

## 2. Context

The shopping list scales each dish by its servings divided by the recipe's servings, converts 斤, 两, tsp, and tbsp to grams and millilitres, adds the results, and rounds counts, grams, and millilitres up to whole numbers (requirements 3, Q18). Rounding up shows every tiny error: in binary floating point, 0.1 × 3 is 0.30000000000000004, so a sum that should be exactly 450 g can come out a hair above it and round up to 451 g. A recipe may also write a decimal amount, such as "1.5 kg".

## 3. Decision

Every amount is a `fractions.Fraction`. `units` reads "1.5" as exactly 3/2. Scaling, conversion, and adding stay exact, and rounding up uses `math.ceil` on the exact value. `units` turns an amount into text only when it writes it, with at most two decimals. No `float` holds an amount anywhere in the tool.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| `fractions.Fraction` | Exact for every scale factor, such as 4/3, and for every unit conversion. Rounding up is always right. | Slower than `float`, which does not matter for a few hundred lines. |
| `decimal.Decimal` | Exact for decimal amounts. | A scale factor such as 4/3 is not exact, so a sum can land just above a whole number and round up one too many. |
| `float` with a small tolerance before rounding up | Fast and familiar. | The tolerance is a guess. A wrong guess shows up as one extra gram or piece. |
| Whole numbers of milligrams and microlitres | Exact for the units' conversions. | Scaling by 4/3 is still not exact, and counts need another scheme. |

## 5. Consequences

- The shopping list in the F13 prototype adds up exactly as its table shows, such as 菜心 500 g + 500 g × 2 = 1.5 kg.
- Section 8 of the architecture forbids `float` for amounts, and code review checks it.
- Tests compare amounts as exact values, with no tolerance.

## 6. Related

- Features: F01, F04, F09, F12, F13
- Rules: None
