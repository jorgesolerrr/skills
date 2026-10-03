---
name: to-blueprint
description: "Turn a finished grilling session into a blueprint: a visual, forever design doc for one feature (decisions, flows at two altitudes, module map, data shapes, file map) as one self-contained HTML page with SVG figures. No interview, just synthesis."
disable-model-invocation: true
---

A **blueprint** is the durable design doc for one feature, written for an agent that will build it and for a human who learns by looking. It is built from the decisions already made in the conversation (usually a grilling session). Synthesize from those decisions; the one checkpoint with the user is step 3. Anything still unsettled goes in **Open questions**, never invented.

Output is one file, `docs/blueprints/<feature-slug>/BLUEPRINT.html`, self-contained: prose and tables in HTML, figures as inline SVG, no script, no external asset beyond the font link.

## Process

1. **Harvest the decisions.** Walk the conversation and list every decision the user settled: what was chosen, what was rejected, and why. This list is the spine of the blueprint. A decision the user did not settle is an open question. Done when every ❓ question from the grilling maps to either a decision row or an open question.

2. **Ground it in the repo.** Facts are your job, never the user's. Explore the codebase (dispatch a sub-agent for broad sweeps) to find the real modules, symbols, and paths the feature touches. Use the project's domain glossary and respect ADRs in the area. Note whether the repo declares design tokens (CSS custom properties, a Tailwind theme, a `.diagram-design` marker). Done when every module and file you will name exists, or is marked `new`.

3. **Sketch the seams.** Pick where the feature will be tested. Prefer existing seams; place new ones as high as possible; the ideal count is one. If the grilling did not settle the seams, post the proposed seams and file map in one message and wait for a yes or a correction. Done when the seams are settled by the grilling or by that reply.

4. **Write `BLUEPRINT.html`** from [`references/template.html`](references/template.html). Map the `:root` tokens onto the repo's design tokens when step 2 found any; otherwise keep the defaults. Fill every section in order. Write the two altitudes as separate sections: **bird's-eye** (one figure, the whole feature end to end, boxes are modules) then **ground level** (one figure per flow, boxes are functions and data shapes). Draw each figure in place per [`references/diagrams.md`](references/diagrams.md): one question per figure, type from the table there, within budget, every label a real symbol, drawn per [`references/svg/base.md`](references/svg/base.md) and the type's file. Done when every section is filled and `python <skill-dir>/scripts/self_check.py <file>` prints `OK <file>`; it fails while any template placeholder is left.

5. **Edit the prose** against [`references/prose.md`](references/prose.md). Then run the completion check below.

## Completion check

The blueprint is done when all of these hold:

- Every settled decision from the conversation appears in the **Decision log**, with its rejected alternatives and reason.
- Every unsettled point appears under **Open questions**. Nothing is silently assumed.
- Every figure is an inline SVG that follows [`references/diagrams.md`](references/diagrams.md), with a `Figure:` caption, and every type the feature adds or changes is a box in **Data shapes**.
- `self_check.py` passes on the file.
- Every **File map** row has Action `add`, `modify`, or `delete`. Every `modify` and `delete` path exists at the stamped commit; `add` paths are exempt. Every symbol in the doc is real.
- Each section is one Diátaxis mode: the decision log explains, the flows and maps describe.
- The doc reads top-down: a reader who stops after **At a glance** still knows what is being built and why.

Report the path of the file, the figure count, and the open-question count.
