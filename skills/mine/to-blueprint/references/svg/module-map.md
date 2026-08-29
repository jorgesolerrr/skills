# Module map: ranked dependency graph

Answers: which module depends on which, and what is new?

## Layout

- Ranked rows, top to bottom by dependency depth. Rank 0 (entry points nothing depends on) at `y=40`; each deeper rank 120px lower. Callers above callees, so every arrow points down or runs sideways within a rank.
- Nodes are modules (never files), 160 x 56, 40px apart within a rank. Name is the module's real identifier, sublabel its path.
- One zone per layer when the codebase names layers (api, domain, infra). Zones span the full width of their rank.
- Arrows are unlabelled here only when they mean plain "imports". Label when a decision chose the dependency (`D4`) or when the edge is an event rather than a call.
- A **fan-in badge** in each node's top-right corner, 8px mono in an `rx="2"` chip, shows how many modules depend on it (`3 in`). The highest fan-in is the structural story of the figure.
- New modules take the `new` stroke and a `NEW` tag. Modified modules stay in the default treatment; the file map says what changes.
- A back-edge (a cycle) is the only arrow allowed to point up. At most one, drawn in accent, dashed, routed around the outside of the stack, labelled `CYCLE`. That edge is the figure's accent budget.

## Budget

At most 12 nodes, 14 edges, 4 ranks, 1 cycle. Past that, collapse a leaf cluster into one node labelled with its count (`+5 adapters`) and say so in the caption.

## Legend

Always, because `new` is a treatment the reader cannot infer: one item for the `new` dash, one for the fan-in badge.
