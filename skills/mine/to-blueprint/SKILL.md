---
name: to-blueprint
description: "Turn a finished grilling session into a blueprint: a visual, forever design doc for one feature (decisions, flows at two altitudes, module map, data shapes, file map). No interview, just synthesis."
disable-model-invocation: true
---

A **blueprint** is the durable design doc for one feature, written for an agent that will build it and for a human who learns by looking. It is built from the decisions already made in the conversation (usually a grilling session). Do NOT interview the user. Synthesize what you already know; anything not decided goes in **Open questions**, never invented.

Output is one file, `docs/blueprints/<feature-slug>/BLUEPRINT.md`, with its diagrams inline as Mermaid fences.

## Process

1. **Harvest the decisions.** Walk the conversation and list every decision the user settled: what was chosen, what was rejected, and why. This list is the spine of the blueprint. A decision the user did not settle is an open question. Done when every ❓ question from the grilling maps to either a decision row or an open question.

2. **Ground it in the repo.** Facts are your job, never the user's. Explore the codebase (dispatch a sub-agent for broad sweeps) to find the real modules, symbols, and paths the feature touches. Use the project's domain glossary and respect ADRs in the area. Done when every module and file you will name exists, or is marked `new`.

3. **Sketch the seams.** Pick where the feature will be tested. Prefer existing seams; place new ones as high as possible; the ideal count is one. If the grilling did not settle the seams, show them to the user with the file map before writing the full doc. Otherwise proceed.

4. **Write `BLUEPRINT.md`** from [`references/template.md`](references/template.md). Fill every section in order. Write the two altitudes as separate sections: **bird's-eye** (one diagram, the whole feature end to end, boxes are modules) then **ground level** (one diagram per flow, boxes are functions and data shapes). Draw each diagram in place per [`references/diagrams.md`](references/diagrams.md): one question per diagram, type from the table there, within budget, every label a real symbol. Data shapes are drawn as class diagrams, never pasted from the code. Done when every section is filled and every fence renders.

5. **Edit the prose** against [`references/prose.md`](references/prose.md). Then run the completion check below.

## Completion check

The blueprint is done when all of these hold:

- Every settled decision from the conversation appears in the **Decision log**, with its rejected alternatives and reason.
- Every unsettled point appears under **Open questions**. Nothing is silently assumed.
- Every diagram is a Mermaid fence within budget, with a `Figure:` line, and every type the feature adds or changes is a node in **Data shapes**.
- Every path in the **File map** exists at the stamped commit or is marked `new`. Every symbol in the doc is real.
- Each section is one Diátaxis mode: the decision log explains, the flows and maps describe.
- The doc reads top-down: a reader who stops after **At a glance** still knows what is being built and why.

Report the path of the file, the diagram count, and the open-question count.
