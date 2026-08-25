# Diagram rules for walkthroughs

The render path (draw with `diagram-design`, export to SVG, embed as an image), the budgets, the label rules, and the layout rules are the ones in [`../../to-blueprint/references/diagrams.md`](../../to-blueprint/references/diagrams.md). This file adds only what a walkthrough needs on top.

## The four diagrams

| Diagram | Question it answers | diagram-design type | File |
|---|---|---|---|
| Change map | Which modules did this touch, and what is added, changed, removed? | dependency graph | `change-map` |
| Flow after | How does the feature work now, end to end? | data flow | `flow-after` |
| Flow before and after | What did this flow do before, and what does it do now? | sequence, one file each | `flow-<slug>-before`, `flow-<slug>-after` |
| Blast radius | Who outside the diff depends on what changed? | dependency graph | `blast-radius` |

Draw a before-and-after pair only for a flow whose behavior changed. A new flow gets the after only. A flow the diff touched without changing behavior (a rename, a move) gets a line in the change map table and no diagram.

## Marking the change

- Use the style guide's semantic roles for three states, and put all three in the legend strip: **added**, **changed**, **removed**. Every node in the change map and blast radius carries one of them or the neutral role for untouched context nodes.
- In a before-and-after pair, keep the same participants in the same order in both diagrams so the eye can diff them. Mark the messages that differ with the **changed** role.
- Blast radius: changed symbols in the center, their callers around them, arrows from caller to callee. Callers outside the diff use the neutral role. Past 12 callers, group by directory and say so under the diagram.

## Budget additions

- Change map: at most 12 modules. Past that, collapse untouched context into one node per layer.
- Before-and-after: at most 7 participants and 12 messages each, so the pair fits side by side.
