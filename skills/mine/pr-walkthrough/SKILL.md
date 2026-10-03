---
name: pr-walkthrough
description: "Visual walkthrough of a PR or branch: what changed, how the code flows now, what it impacts, optionally how it matches a spec, plus a separate retrospective of the coding session. Disposable output, never committed."
disable-model-invocation: true
---

A **walkthrough** is the reading guide for one change: it teaches a human what the code does and how it lands on the project. When the change came from a spec, it also grades the diff against that spec. The user passes a PR number or URL, a branch, or a fixed point (`main`, a sha), and optionally a spec link. Produce it from the diff and the repo.

The output is **disposable**: a reading aid for this review, not a document the repo maintains. It lives in a self-ignoring folder at the repo root and never enters git. The **slug** is `pr-<n>` for a PR, otherwise the branch name (the current branch for a bare fixed point) with `/` replaced by `-`.

```
.walkthroughs/<slug>/
  .gitignore            contains `*`, so the folder ignores itself
  WALKTHROUGH.md        the reading guide, diagrams inline as Mermaid fences
  RETRO.md              the retrospective of the session that produced the change
```

## Process

1. **Pin the change.** Read the change in place; the user's checkout and working tree stay as they are.
   - PR: `gh pr view <n> --json number,title,body,baseRefName,headRefName,headRefOid,commits`, then `git fetch origin <baseRefName> pull/<n>/head`. The fixed point is `origin/<baseRefName>`. Capture `git diff origin/<baseRefName>...<headRefOid>` (same as `gh pr diff <n>`) and `git log origin/<baseRefName>..<headRefOid> --oneline`. Read head files with `git show <headRefOid>:<path>`.
   - Branch: the fixed point is `git merge-base <default-branch> <branch>`. Capture `git diff <fixed-point>...<branch>` and `git log <fixed-point>..<branch> --oneline`.
   - Fixed point: capture `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`.

   Ask the user for the fixed point only when none resolves. Create the output folder with its `.gitignore`. Done when the fixed point resolves, the diff is non-empty, and `git status --ignored --short` shows `!! .walkthroughs/`.

2. **Decide the spec branch.** Three cases:
   - The user passed a spec link: use it, skip the hunt.
   - No link passed: ask the user one question, "Is there a spec or issue this change implements? Give the link, or say none." Hunt only on a yes: PR body and commit messages → issue (`#123`, `Closes #45`, tracker URL; fetch per `docs/agents/issue-tracker.md` when present) → spec (a blueprint under `docs/blueprints/`, a file under `docs/` or `specs/` matching the branch or feature, or a spec section in the issue body). Record each hop.
   - The user says none: mark spec `none` and go straight to step 3.

   Done when the spec resolves to a path or URL, or is marked `none`. Without a spec, **Link chain** and **Spec match** drop from the doc and nothing else changes.

3. **Read the change as modules, not hunks.** Group the diff by module. For each module: what it did before, what it does now, and which other modules call it (`grep` the symbols the diff touches to find dependents). Facts are your job; dispatch a sub-agent for the dependents sweep on a large diff. Done when every changed file sits under one module and every changed public symbol has its callers listed.

4. **Write `WALKTHROUGH.md`** from [`references/template.md`](references/template.md). Fill every section in order. Draw the diagrams in place per [`references/diagrams.md`](references/diagrams.md): change map, flow after the change, blast radius, a before-and-after pair for each flow whose behavior changed, and a class diagram for each data type the diff adds or changes. With a spec, fill **Spec match** by walking the spec's decisions one by one and grading each with the template's status vocabulary, citing `path:line` evidence from the diff. Done when every section is filled and every fence renders.

5. **Write `RETRO.md`.** Find the session that produced the change: the current one only if this conversation wrote the diff; otherwise the logs the user names, or a search of the session logs for the head branch or commit shas. Read `../retro/SKILL.md` (the `retro` skill; its step 2 names the log folders) and follow its steps 1–3 against that session. In place of its step 4, write the candidates, in severity order, into `RETRO.md` in the shape at the end of the template. When no session is found, `RETRO.md` holds the single line `No session logs available`.

6. **Edit the prose** of both docs against [`../to-blueprint/references/prose.md`](../to-blueprint/references/prose.md), then run the completion check.

## Completion check

- `git status --ignored --short` shows `!! .walkthroughs/` and no tracked or untracked file under it.
- Every file in the diff appears in the **Change map** under exactly one module.
- Every changed public symbol appears in **Impact** with its callers, or is marked `no callers`. Every changed data type is a node in **Data types changed**, never pasted code.
- With a spec: every decision in it has a status row with evidence, and every hunk not traceable to the spec is listed under **Not in the spec**.
- Every diagram is a Mermaid fence within budget, with a `Figure:` line.
- **Reading order** lists every changed file once, in the order a newcomer should open them.
- `RETRO.md` exists and holds the `retro` candidates or the no-logs line.

Report the folder path, the spec-match totals (done, partial, missing, deviated, deferred) or `no spec`, and the retro candidate count.
