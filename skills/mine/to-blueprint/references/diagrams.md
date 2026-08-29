# Diagram rules for blueprints

Every diagram answers one question a reader could not answer faster from a paragraph. If a paragraph wins, write the paragraph.

## Render path

Diagrams are inline `<svg>` figures in `BLUEPRINT.html`, hand-laid per [`svg/base.md`](svg/base.md) and the type file below. The HTML is the source: no `diagrams/` folder, no export, no script. Each `<figure>` ends with a `<figcaption>`: `Figure: <the one sentence the diagram answers>`.

Validate the finished file once: `python <skill-dir>/scripts/self_check.py docs/blueprints/<slug>/BLUEPRINT.html`. It checks the accessible-SVG contract and that the page loads nothing remote beyond Google Fonts.

## Pick the type by the question

| The reader asks | Type | Read |
|---|---|---|
| What are the parts and how does work move between them? | flowchart, left to right | [`svg/flowchart.md`](svg/flowchart.md) |
| Which module depends on which, and what is new? | ranked dependency graph, top to bottom | [`svg/module-map.md`](svg/module-map.md) |
| In what order do calls happen, and what crosses each hop? | sequence | [`svg/sequence.md`](svg/sequence.md) |
| What states can this thing be in, and what moves it? | state machine | [`svg/state.md`](svg/state.md) |
| What fields does this type carry, and what does it hold or point to? | class diagram | [`svg/class.md`](svg/class.md) |
| What tables exist and how do they relate? | ER diagram | [`svg/er.md`](svg/er.md) |
| Who owns which step? | flowchart with one zone per owner | [`svg/flowchart.md`](svg/flowchart.md) |

Bird's-eye is the flowchart. Module map is the dependency graph. Ground level is a sequence by default, a state machine when the flow is a lifecycle. **Data shapes are drawn, never pasted**: every type the feature adds or changes (dataclass, record, DTO, interface, event, config object) is a class-diagram box with its fields, and a table change is an ER diagram. A code snippet appears only when it encodes a decision a diagram cannot (a reducer, a guard expression), trimmed to that part.

## Budget

- **Bird's-eye**: at most 9 nodes. Past that, the feature has more than one story; split into two blueprints or collapse a subsystem into one node.
- **Module map**: at most 12 nodes.
- **Ground level**: at most 7 participants and 15 messages per sequence. Past that, split the flow at the seam.
- **Data shapes**: at most 8 classes per diagram, fields that matter to a decision only.

Budget is a legibility rule. A diagram over budget gets split, never squeezed.

## Labels

- Every node is a real symbol, module, or system name from the repo. No "Service", "Handler", "Logic" placeholders.
- Every arrow carries what crosses it: a data shape, an event, or a call. `OrderCreated`, `place(draft: OrderDraft)`. An unlabeled arrow is a missing decision.
- When a decision chose the route, its id leads the label: `D3 retry via queue`.
- One name per thing across the whole doc. The node label, the interface list, and the file map use the same identifier.

## Marking new things

A node the feature adds takes the `new` treatment from `svg/base.md` (green dashed stroke, `NEW` tag). A sequence participant the feature adds takes the same stroke on its box. Every figure that uses it carries the legend item.

## Layout

- Read direction matches time or data direction: left to right for flows, top to bottom for dependency.
- Group by ownership with a zone, at most one level deep.
- Failure paths are dashed.
- Sequence participants appear in the order they first act.
- Accent on at most two elements per figure. The rest is ink and muted.
