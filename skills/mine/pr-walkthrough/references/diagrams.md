# Diagram rules for walkthroughs

Every diagram answers one question a reader could not answer faster from a paragraph. If a paragraph wins, write the paragraph. The syntax per type is in [`mermaid.md`](mermaid.md).

## Render path

Diagrams are Mermaid fences inline in `WALKTHROUGH.md`. GitHub and the editor render them. The fence is the source: no `diagrams/` folder, no export. Under each fence, one line: `Figure: <the one sentence the diagram answers>`.

When `mmdc` is on `PATH`, validate each fence once: paste it into a scratch `.mmd` and run `mmdc -i x.mmd -o x.svg`. A `Could not find Chrome` error is setup, not syntax; skip validation.

## The five diagrams

| Diagram | Question it answers | Mermaid |
|---|---|---|
| Change map | Which modules did this touch, and what is added, changed, removed? | `flowchart TB` |
| Flow after | How does the feature work now, end to end? | `flowchart LR` |
| Flow before and after | What did this flow do before, and what does it do now? | `sequenceDiagram`, one fence each |
| Blast radius | Who outside the diff depends on what changed? | `flowchart TB` |
| Data types changed | What shape do the changed types have now? | `classDiagram`, or `erDiagram` for a schema |

Draw a before-and-after pair only for a flow whose behavior changed. A new flow gets the after only. A flow the diff touched without changing behavior (a rename, a move) gets a line in the change map table and no diagram.

## Budget

Budget is a legibility rule. A diagram over budget gets split, never squeezed.

- **Change map**: at most 12 modules. Past that, collapse untouched context into one node per layer.
- **Flow after**: at most 9 nodes. Past that, collapse a subsystem into one node and say so under the diagram.
- **Before and after**: at most 7 participants and 12 messages each.
- **Blast radius**: at most 12 callers. Past that, group by directory and say so under the diagram.
- **Data types changed**: at most 8 classes per diagram, fields that matter to the change only.

## Labels

- Every node is a real symbol, module, or system name from the repo. No "Service", "Handler", "Logic" placeholders.
- Every arrow carries what crosses it: a data shape, an event, or a call. `OrderCreated`, `place(draft: OrderDraft)`.
- One name per thing across the whole doc. The node label, the tables, and the reading order use the same identifier.

## Layout

- Read direction matches time or data direction: left to right for flows, top to bottom for dependency.
- Group by ownership with a `subgraph`, at most one level deep.
- Failure paths are dashed.
- Sequence participants appear in the order they first act.

## Marking the change

In `flowchart`, `classDiagram`, and `erDiagram` fences, declare the three classes once per fence and tag every touched node; untouched context nodes stay unstyled:

```
classDef added stroke:#2e7d32,stroke-width:2px
classDef changed stroke:#e65100,stroke-width:2px
classDef removed stroke:#b71c1c,stroke-width:2px,stroke-dasharray:5 3
class OrderQueue added
class Checkout,Billing changed
class LegacyCart removed
```

- Before-and-after pair: `sequenceDiagram` takes no classes, so the change rides on the messages. Same participants in the same order in both fences so the eye can diff them. Prefix each message that differs with `[changed]`, `[added]`, or `[removed]`.
- Blast radius: changed symbols in the top row, their callers below, arrows from caller to callee.
- Data types: tag the class with its state. In a `changed` class list only the fields that moved, with the move after the type: `+retries: int added`, `-legacy_id: str removed`.
