---
name: pr-walkthrough
description: "Visual walkthrough of a PR or branch: what changed, how the code flows now, what it impacts, how it matches the linked spec, plus a retrospective of the coding session."
disable-model-invocation: true
---

A **walkthrough** is the reading guide for one change: it teaches a human what the code does and how it lands on the project, and it audits the change against the spec it came from. The user passes a PR number or URL, a branch, or a fixed point (`main`, a sha). Produce it from the diff and the repo; ask the user only for the fixed point when none can be resolved.

Layout, one folder per change:

```
docs/walkthroughs/<pr-slug>/
  WALKTHROUGH.md        the doc
  diagrams/<name>.html  diagram source, drawn with the diagram-design skill
  diagrams/<name>.svg   export of the source, embedded in WALKTHROUGH.md
```

## Process

1. **Pin the change.** Resolve the fixed point and capture `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`. For a PR, use `gh pr view <n> --json number,title,body,baseRefName,headRefName,commits` and check it out. Done when the ref resolves and the diff is non-empty.

2. **Follow the link chain.** PR body and commit messages → issue (`#123`, `Closes #45`, tracker URL; fetch per `docs/agents/issue-tracker.md` when present) → spec. A spec is a blueprint under `docs/blueprints/`, a file under `docs/` or `specs/` matching the branch or feature, or a spec section in the issue body. Record each hop found. Done when every hop is either resolved to a path or URL, or marked `none`. A missing spec removes the **Spec match** section; it never blocks the rest.

3. **Read the change as modules, not hunks.** Group the diff by module. For each module: what it did before, what it does now, and which other modules call it (`grep` the symbols the diff touches to find dependents). Facts are your job; dispatch a sub-agent for the dependents sweep on a large diff. Done when every changed file sits under one module and every changed public symbol has its callers listed.

4. **Write `WALKTHROUGH.md`** from [`references/template.md`](references/template.md). Fill every section in order. When a spec was found, fill **Spec match** by walking the spec's decision log and user stories one by one and grading each with the status vocabulary in the template, citing `path:line` evidence from the diff.

5. **Draw and export the diagrams** per [`references/diagrams.md`](references/diagrams.md): change map, flow after the change, blast radius, and a before-and-after pair for each flow whose behavior changed. Done when every image reference in the doc resolves to a rendered `.svg`.

6. **Run the retrospective.** Read `../retro/SKILL.md` (the `retro` skill, unchanged) and follow it against the session that produced this change: the current session, or the session logs the user names. Place its candidates, in severity order, under **Retrospective**. Do the writing per `../to-blueprint/references/prose.md`.

7. **Edit the prose** against [`../to-blueprint/references/prose.md`](../to-blueprint/references/prose.md), then run the completion check.

## Completion check

- Every file in the diff appears in the **Change map** under exactly one module.
- Every changed public symbol appears in **Impact** with its callers, or is marked `no callers`.
- When a spec exists: every decision and user story in it has a status row with evidence, and every hunk not traceable to the spec is listed under **Not in the spec**.
- Every diagram has its `.html` source and `.svg` export in `diagrams/` and is within budget.
- **Reading order** lists every changed file once, in the order a newcomer should open them.
- **Retrospective** holds the `retro` output, or the line `No session logs available` when there were none.

Report the folder path, the spec-match totals (done, partial, missing, deviated), and the retro candidate count.
