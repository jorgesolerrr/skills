# Diagram rules for blueprints

Every diagram answers one question a reader could not answer faster from a paragraph. If a paragraph wins, write the paragraph.

## Render path

Diagrams are Mermaid fences inline in `BLUEPRINT.md`. GitHub and the editor render them. The fence is the source: no `diagrams/` folder, no export. Under each fence, one line: `Figure: <the one sentence the diagram answers>`.

When `mmdc` is on `PATH`, validate each fence once: paste it into a scratch `.mmd` and run `mmdc -i x.mmd -o x.svg`. A `Could not find Chrome` error is setup, not syntax; skip validation.

## Pick the type by the question

| The reader asks | Mermaid |
|---|---|
| What are the parts and how does work move between them? | `flowchart LR` |
| Which module depends on which, and what is new? | `flowchart TB`, one `subgraph` per layer, callers above callees |
| In what order do calls happen, and what crosses each hop? | `sequenceDiagram` |
| What states can this thing be in, and what moves it? | `stateDiagram-v2` |
| What fields does this type carry, and what does it hold or point to? | `classDiagram` |
| What tables exist and how do they relate? | `erDiagram` |
| Who owns which step? | `flowchart` with one `subgraph` per owner |

Bird's-eye uses `flowchart LR`. Module map uses `flowchart TB`. Ground level uses `sequenceDiagram` by default, `stateDiagram-v2` when the flow is a lifecycle. **Data shapes are drawn, never pasted**: every type the feature adds or changes (dataclass, record, DTO, interface, event, config object) is a `classDiagram` node with its fields, and a table change is an `erDiagram`. A code snippet appears only when it encodes a decision a diagram cannot (a reducer, a guard expression), trimmed to that part.

## Budget

- **Bird's-eye**: at most 9 nodes. Past that, the feature has more than one story; split into two blueprints or collapse a subsystem into one node.
- **Module map**: at most 12 nodes.
- **Ground level**: at most 7 participants and 15 messages per sequence diagram. Past that, split the flow at the seam.
- **Data shapes**: at most 8 classes per diagram, fields that matter to a decision only.

Budget is a legibility rule. A diagram over budget gets split, never squeezed.

## Labels

- Every node is a real symbol, module, or system name from the repo. No "Service", "Handler", "Logic" placeholders.
- Every arrow carries what crosses it: a data shape, an event, or a call. `A -- "OrderCreated" --> B`, `A->>B: place(draft: OrderDraft)`. An unlabeled arrow is a missing decision.
- When a decision chose the route, write its id on the arrow: `D3: retry via queue`.
- One name per thing across the whole doc. The node label, the interface list, and the file map use the same identifier.

## Marking new things

Declare once per fence that needs it, then tag nodes:

```
classDef new stroke:#2e7d32,stroke-width:2px,stroke-dasharray:5 3
class OrderQueue,RetryWorker new
```

Sequence diagrams have no `classDef`: write `new` in the participant alias, `participant Q as OrderQueue (new)`.

## Layout

- Read direction matches time or data direction: `LR` for flows, `TB` for dependency.
- Group by ownership with `subgraph`, at most one level deep.
- Failure paths are dashed: `-.->` in a flowchart, `-x` in a sequence.
- Declare `participant`s in the order they first act.

## Syntax

Before drawing a type, read its section in [`mermaid.md`](mermaid.md): node shapes, arrow kinds, fragments, relations, cardinality. The one rule that bites everywhere: quote a label holding `:`, `(`, `[`, `|`, or `/`.
