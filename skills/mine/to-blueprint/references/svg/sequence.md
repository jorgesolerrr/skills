# Sequence: the ground-level figure

Answers: in what order do calls happen, and what crosses each hop?

## Layout

- Participants are function or module boxes (160 x 40) in a row at `y=24`, 200px between centres, in the order they first act. A new participant takes the `new` stroke.
- A **lifeline** drops from each box to the bottom: `<line stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 3"/>`.
- Messages are horizontal arrows between lifelines, top to bottom in time, 32px apart on the grid. An arrow pointing up reverses time and is a hard fail.
- An **activation bar** (8px wide, `fill="var(--ink)" fill-opacity="0.06" stroke="var(--muted)" stroke-width="0.8"`) sits on the lifeline while that participant holds control. Nest by offsetting 4px. Every bar closes.
- A self-call is a short U to the right of the lifeline, label to its right.
- Every message label is the call with its data shape: `place(draft: OrderDraft)`. Returns name the shape that comes back.

## Message kinds

| Kind | Stroke | Marker |
|---|---|---|
| Sync call | solid `--muted`, or `--link` across a boundary | `#arrow` |
| Return | dashed `5 4`, `--muted` | `#arrow` (filled, never open) |
| Async, event | dashed, `--muted` | `#arrow-open` |
| Headline success (1, at most 2) | solid `--accent` | `#arrow-accent` |
| Failure | dashed, ends on an `x`: two 8px `--muted` lines crossed at the target lifeline | none |

## Fragments

A branch, an optional step, or a retry is a **frame**, never two loose clusters of arrows.

```svg
<rect x="X" y="Y" width="W" height="H" rx="4" fill="var(--ink)" fill-opacity="0.02"
      stroke="var(--rule)" stroke-width="1"/>
<rect x="X" y="Y" width="40" height="16" rx="2" fill="var(--paper)" stroke="var(--rule)"/>
<text x="X+20" y="Y+12" font-size="8" font-family="var(--font-mono)" fill="var(--muted)"
      text-anchor="middle" letter-spacing="0.12em">ALT</text>
<text x="X+12" y="Y+32" font-size="8" font-family="var(--font-mono)" fill="var(--muted)">[token valid]</text>
```

| Operator | Regions | Divider |
|---|---|---|
| `OPT` | 1, guard under the tab | none |
| `ALT` | 2, a guard on each | dashed `--rule` line across the frame, 16px clear of messages |
| `LOOP` | 1, `[retry <= 3]` under the tab | none |

The frame spans only the lifelines that take part, inset 12px past their centres. One fragment per figure by default, no nesting. Accent stays on one message across both branches.

## Budget

At most 7 participants, 15 messages, 1 fragment, 2 accent elements. Past that, split the flow at the seam: happy path in one figure, failure or refresh in the next.
