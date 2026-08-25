# Prose rules for blueprints

Condensed from the `technical-writing` skill for the sections a blueprint has. A tired engineer, or an agent, must understand each sentence on the first read.

## One mode per section

- **Explanation** sections (At a glance, Problem, Solution, Decision log) carry the why. A view is allowed: say what you make of a trade-off, not just the two sides.
- **Reference** sections (everything else) describe. No instruction, no persuasion, no hedging. Complete and dry.

## Sentences

- Talk to the reader as "you", present tense. Say who does what: "the reducer rejects", not "is rejected".
- One thought per sentence. Split anything past about 25 words.
- Condition before the action: "When the token expires, the client refreshes it."
- Keep "the" and "a". Keep "that" when it fixes the parse.
- "Only" and "not" sit next to the word they change.
- Every "it", "this", and "they" points at one noun. Repeat the noun when in doubt.
- Periods, not semicolons. A new sentence, not an em dash.
- No slashes: "a, b, or both".

## Words

- The codebase is the word list. Write the real symbol, path, flag, or command in code font.
- One name per thing across the doc, matching the glossary.
- Short everyday words: use, help, do. Cut "in order to", "it is important to note", "simply", "easy".
- Named patterns are fine once defined. Invented metaphors are not.
- Be specific over sterile: "a column rename fails the build", not "schema changes can cause issues".

## Lists and tables

- Numbered lists for sequences, bullets for everything else. Items parallel.
- Tables for anything with two or more attributes per row. Every cell filled or marked `—`.
- Headings carry the point, in sentence case.

## Checklist before finishing

1. Is each section one mode?
2. Does any sentence carry two thoughts? Split it.
3. Can any word go without losing meaning? Cut it.
4. Is every symbol, path, and count real at the stamped commit?
5. Does each thing have exactly one name across the doc and its diagrams?
6. Would a developer say these words out loud?
