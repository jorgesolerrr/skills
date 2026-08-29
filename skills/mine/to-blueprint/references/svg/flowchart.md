# Flowchart: the bird's-eye figure

Answers: what are the parts, and how does work move between them?

## Layout

- Left to right in the order data moves. Entry at `x=40`, exit at the right edge. One row when possible; a second row only for a branch or a store.
- Nodes are modules or systems from the module map, 160 x 56, 40px apart. A store hangs below the module that owns it, 48px down, joined by a straight vertical arrow.
- One zone per owner (bounded context, process, external vendor) when ownership is part of the story. At most one level.
- Every arrow carries the data shape or event that crosses it. When a decision picked the route, its id leads the label: `D2 OrderCreated`.
- A branch is a diamond with at most three exits, each labelled with its condition. A rejoin is a filled dot `r="4"`.
- Failure paths are dashed and leave from the bottom edge.
- Accent on the happy path's headline arrow, or on the one node the feature is about. One, at most two.

## Grammar

| Thing | Drawn as |
|---|---|
| Module, function | rectangle `rx="6"` |
| Store, queue | rectangle with the cylinder top |
| External system | rectangle with the external treatment |
| Decision | diamond, `Yes` right, `No` down |
| Start, end | filled dot, ringed dot |

## Budget

At most 9 nodes. Past that the feature has two stories: split into two blueprints, or collapse a subsystem into one node and say so in the caption.
