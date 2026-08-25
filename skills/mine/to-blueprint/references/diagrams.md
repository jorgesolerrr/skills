# Diagram rules for blueprints

Every diagram answers one question a reader could not answer faster from a paragraph. If a paragraph wins, write the paragraph.

## Render path

Each diagram is drawn with the `diagram-design` skill and exported to SVG, then embedded in `BLUEPRINT.md` as an image:

1. Load the `diagram-design` skill. On the first blueprint in a project it runs its style-guide gate (`.diagram-design` marker); follow it once and reuse the profile after.
2. Draw the diagram as `docs/blueprints/<feature-slug>/diagrams/<name>.html`. Use the `diagram-design` visual type from the table below. Size preset: `docs` width, or the skill's default for the type.
3. Export with the SVG procedure in `diagram-design/references/export.md`, writing `diagrams/<name>.svg` next to the source. Invoking `/to-blueprint` is the user's explicit export request, so run it for every blueprint diagram.
4. Embed in the doc: `![<one-sentence description, same as the svg desc>](diagrams/<name>.svg)`, followed by a link to the `.html` source: `Source: [`<name>.html`](diagrams/<name>.html)`.

Names: `birds-eye`, `module-map`, `flow-<flow-slug>`, `data-model`, `state-<thing>`.

**Fallback.** When the `diagram-design` skill is not installed, write the diagram as an inline Mermaid fence using the Mermaid column below, and add a line under it: `Rendered with Mermaid; redraw with diagram-design when available.` Every other rule in this file still applies.

## Pick the type by the question

| The reader asks | diagram-design type | Mermaid fallback |
|---|---|---|
| What are the parts and how does work move between them? | data flow | `flowchart LR` |
| Which module depends on which, and what is new? | dependency graph | `flowchart TB` with `subgraph` per layer |
| In what order do calls happen, and what crosses each hop? | sequence | `sequenceDiagram` |
| What states can this thing be in, and what moves it? | state machine | `stateDiagram-v2` |
| What entities exist and how do they relate? | ER | `erDiagram` |
| What happens when, in a lifecycle or rollout? | timeline | `timeline` |
| Who owns which step? | swimlane | `flowchart` with one `subgraph` per owner |

Bird's-eye uses **data flow**. Module map uses **dependency graph**. Ground level uses **sequence** by default, **state machine** when the flow is a lifecycle, **ER** when a schema changes.

## Budget

- **Bird's-eye**: at most 9 nodes. Past that, the feature has more than one story; split into two blueprints or collapse a subsystem into one node.
- **Module map**: at most 12 nodes.
- **Ground level**: at most 7 participants and 15 messages per sequence diagram. Past that, split the flow at the seam.
- **Any diagram**: at most 3 crossing arrows. Reorder nodes until crossings drop.

Budget is a legibility rule. A diagram over budget gets split, never squeezed. `diagram-design` has its own complexity budget per type; the tighter of the two wins.

## Labels

- Every node is a real symbol, module, or system name from the repo. No "Service", "Handler", "Logic" placeholders.
- Every arrow carries what crosses it: a data shape, an event, or a call. An unlabeled arrow is a missing decision.
- When a decision chose the route, write its id on the arrow: `D3: retry via queue`.
- New things carry the word `new` in the label.
- One name per thing across the whole doc. The node label, the interface list, and the file map use the same identifier.
- The SVG `<title>` is the diagram name; the `<desc>` is the one sentence reused as the image alt text.

## Layout

- Read direction matches time or data direction: left to right for flows, top to bottom for dependency (callers above callees).
- Group by ownership, at most one level deep.
- Failure paths are dashed.
- Add a legend only when a visual convention appears that `diagram-design`'s legend strip does not already define.
