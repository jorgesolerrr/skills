---
name: to-blueprint
description: "Turn a finished grilling session into a blueprint: a visual, forever design doc for one feature (decisions, flows at two altitudes, module map, file map). No interview, just synthesis."
disable-model-invocation: true
---

A **blueprint** is the durable design doc for one feature, written for an agent that will build it and for a human who learns by looking. It is built from the decisions already made in the conversation (usually a grilling session). Do NOT interview the user. Synthesize what you already know; anything not decided goes in **Open questions**, never invented.

Layout, one folder per feature:

```
docs/blueprints/<feature-slug>/
  BLUEPRINT.md          the doc
  diagrams/<name>.html  diagram source, drawn with the diagram-design skill
  diagrams/<name>.svg   export of the source, embedded in BLUEPRINT.md
```

## Process

1. **Harvest the decisions.** Walk the conversation and list every decision the user settled: what was chosen, what was rejected, and why. This list is the spine of the blueprint. A decision the user did not settle is an open question. Done when every ❓ question from the grilling maps to either a decision row or an open question.

2. **Ground it in the repo.** Facts are your job, never the user's. Explore the codebase (dispatch a sub-agent for broad sweeps) to find the real modules, symbols, and paths the feature touches. Use the project's domain glossary and respect ADRs in the area. Done when every module and file you will name exists, or is marked `new`.

3. **Sketch the seams.** Pick where the feature will be tested. Prefer existing seams; place new ones as high as possible; the ideal count is one. If the grilling did not settle the seams, show them to the user with the file map before writing the full doc. Otherwise proceed.

4. **Write `BLUEPRINT.md`** from [`references/template.md`](references/template.md). Fill every section in order. Write the two altitudes as separate sections: **bird's-eye** (one diagram, the whole feature end to end, boxes are modules) then **ground level** (one diagram per flow, boxes are functions and data shapes). Leave each diagram slot as an image reference to the `.svg` you will produce in step 5.

5. **Draw and export the diagrams** following [`references/diagrams.md`](references/diagrams.md): draw each one as HTML with the `diagram-design` skill, then run its SVG export into `diagrams/`. One question per diagram, type chosen from the table there, node count within budget, every label a real symbol name. Done when every image reference in `BLUEPRINT.md` resolves to a file that renders.

6. **Edit the prose** against [`references/prose.md`](references/prose.md). Then run the completion check below.

## Completion check

The blueprint is done when all of these hold:

- Every settled decision from the conversation appears in the **Decision log**, with its rejected alternatives and reason.
- Every unsettled point appears under **Open questions**. Nothing is silently assumed.
- Every diagram has both its `.html` source and its `.svg` export in `diagrams/`, the `.svg` is referenced from the doc, and each stays within the node budget.
- Every path in the **File map** exists at the stamped commit or is marked `new`. Every symbol in the doc is real.
- Each section is one Diátaxis mode: the decision log explains, the flows and maps describe.
- The doc reads top-down: a reader who stops after **At a glance** still knows what is being built and why.

Report the path of the folder, the diagram count, and the open-question count.
