# Diagram rules for walkthroughs

The render path (Mermaid fences in place, one `Figure:` line under each), the budgets, the label rules, and the layout rules are the ones in [`../../to-blueprint/references/diagrams.md`](../../to-blueprint/references/diagrams.md); the syntax per type is in [`../../to-blueprint/references/mermaid.md`](../../to-blueprint/references/mermaid.md). This file adds only what a walkthrough needs on top.

## The five diagrams

| Diagram | Question it answers | Mermaid |
|---|---|---|
| Change map | Which modules did this touch, and what is added, changed, removed? | `flowchart TB` |
| Flow after | How does the feature work now, end to end? | `flowchart LR` |
| Flow before and after | What did this flow do before, and what does it do now? | `sequenceDiagram`, one fence each |
| Blast radius | Who outside the diff depends on what changed? | `flowchart TB` |
| Data types changed | What shape do the changed types have now? | `classDiagram`, or `erDiagram` for a schema |

Draw a before-and-after pair only for a flow whose behavior changed. A new flow gets the after only. A flow the diff touched without changing behavior (a rename, a move) gets a line in the change map table and no diagram.

## Marking the change

Declare the three classes once per fence and tag every touched node; untouched context nodes stay unstyled:

```
classDef added stroke:#2e7d32,stroke-width:2px
classDef changed stroke:#e65100,stroke-width:2px
classDef removed stroke:#b71c1c,stroke-width:2px,stroke-dasharray:5 3
class OrderQueue added
class Checkout,Billing changed
class LegacyCart removed
```

- Before-and-after pair: same participants in the same order in both fences so the eye can diff them. Prefix each message that differs with `[changed]`, `[added]`, or `[removed]`.
- Blast radius: changed symbols in the top row, their callers below, arrows from caller to callee. Past 12 callers, group by directory and say so under the diagram.
- Data types: tag the class with its state. In a `changed` class list only the fields that moved, with the move after the type: `+retries: int added`, `-legacy_id: str removed`.

## Budget additions

- Change map: at most 12 modules. Past that, collapse untouched context into one node per layer.
- Before-and-after: at most 7 participants and 12 messages each.
