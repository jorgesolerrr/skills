# Skills registry

Single source of truth for skills shared across agents (Claude Code, Codex, Cursor, etc.).

Layout: one folder per source under `skills/`, one folder per skill inside it, each with a `SKILL.md`.

```
skills/
  mattpocock/<skill-name>/SKILL.md     forks of mattpocock/skills
  cathrynlavery/diagram-design/        fork of cathrynlavery/diagram-design
  pstack/<skill-name>/SKILL.md         forks of cursor/plugins (pstack)
  mine/<skill-name>/SKILL.md           skills authored in this registry
```

## Loading skills into Claude Code

Claude Code discovers skills only at `~/.claude/skills/<skill-name>/SKILL.md`, one level deep. The source
subfolders here are for organization; they are flattened by linking each skill folder directly into
`~/.claude/skills/` with a junction (no admin rights needed; symlinks need them). Relative references
between skills (for example `../retro/SKILL.md`) resolve through the junctions, since every linked skill
is a sibling in `~/.claude/skills/`.

Link every skill from PowerShell:

```powershell
$root = "$PWD\skills"; $dst = "$env:USERPROFILE\.claude\skills"
Get-ChildItem $root -Directory | Get-ChildItem -Directory | ForEach-Object {
  if (-not (Test-Path "$dst\$($_.Name)")) { cmd /c mklink /J "$dst\$($_.Name)" $_.FullName }
}
```

Skill names must stay unique across all source folders, because they share one flat namespace in
`~/.claude/skills/`. Restart Claude Code after linking.

## Loading skills into Cursor and Codex

Same flattening, different target folders: Cursor reads `~/.cursor/skills/` (and also `~/.claude/skills/`),
Codex reads `~/.codex/skills/`. Junctions work for both; change `$dst` in the script above to
`$env:USERPROFILE\.cursor\skills` or `$env:USERPROFILE\.codex\skills` and re-run it.

If a skill folder is moved inside this repo (for example when a new source subfolder is added), the
links keep pointing at the old path and the agent silently drops the skill. Find dangling links with:

```powershell
foreach ($d in "$env:USERPROFILE\.claude\skills","$env:USERPROFILE\.cursor\skills","$env:USERPROFILE\.codex\skills") {
  Get-ChildItem $d -Force | Where-Object { -not (Test-Path "$($_.FullName)\SKILL.md") } | ForEach-Object { "DEAD $d\$($_.Name)" }
}
```

Remove dead links with `cmd /c rmdir <link>` (never `Remove-Item -Recurse`, which follows the link into
the repo), then re-run the link script.

## Sources

### mattpocock/skills

Copied raw from [mattpocock/skills](https://github.com/mattpocock/skills) at commit `6654f6b` so they can
be modified locally. Not installed as a plugin — edits here are intentional forks.
License: MIT (see `LICENSE-mattpocock`).

- `skills/mattpocock/`: ask-matt, code-review, codebase-design, diagnosing-bugs, domain-modeling,
  grill-with-docs, implement, improve-codebase-architecture, prototype, research,
  resolving-merge-conflicts, setup-matt-pocock-skills, tdd, to-spec, to-tickets, triage, wayfinder, wizard.
  grill-me, grilling, handoff, teach, to-questionnaire, wait-what, writing-for-agents.
  retro (depends on `writing-for-agents`).

### cathrynlavery/diagram-design

Copied raw from the `skills/diagram-design/` folder of
[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) at commit `648c2a5`
(skill version 2.6). Includes `assets/`, `references/` and `scripts/` alongside `SKILL.md`.
License: MIT (see `LICENSE-diagram-design`).

Skills: `skills/cathrynlavery/diagram-design`.

### cursor/plugins (pstack)

Copied raw from the `pstack/skills/` folder of [cursor/plugins](https://github.com/cursor/plugins) at
commit `4612556`. License: MIT, © Lauren Tan (see `LICENSE-cursor-pstack`).

Skills: `skills/pstack/`: technical-writing, unslop.

### Local (this registry)

Skills authored here, not copied from an upstream source.

- `skills/mine/to-blueprint/`: to-blueprint. Turns a finished grilling session into a visual, forever design
  doc for one feature (`docs/blueprints/<slug>/BLUEPRINT.md`): decision log, bird's-eye and ground-level
  diagrams as inline Mermaid, data shapes as class diagrams, file map, testing seams, open questions.
  Rules condensed from `technical-writing`. No external diagram skill needed.
- `skills/mine/pr-walkthrough/`: pr-walkthrough. Visual walkthrough of a PR or branch
  (`.walkthroughs/<slug>/`, self-ignored): change map, flow after the change, before-and-after flows, blast
  radius, changed data types, spec-match table against the linked issue's spec or blueprint, reading order,
  and a retrospective produced by following `retro` as-is. Shares diagram and prose rules with
  `to-blueprint`.
- `skills/mine/implement-ticket/`: implement-ticket. Session 1 of 3: builds one ticket from the repo's issue
  tracker with `tdd` (a ticket naming the public interface counts as seam confirmation), settles every design
  decision against the repo's coding standards, and commits with the ticket id. Fork of mattpocock `implement`.
- `skills/mine/review-ticket/`: review-ticket. Session 2 of 3: loops `adversarial-review` on the ticket branch
  against the merge base until no `[hard]` findings remain (max five rounds), fixing or justifying each; the
  reviewer's `[suggestion]` findings are handed to the user to accept or drop.
- `skills/mine/deepen-ticket/`: deepen-ticket. Session 3 of 3: runs `improve-codebase` on the modules the
  branch touched and files the candidates as `docs/reports/<ticket-id>.md`.
- `skills/mine/adversarial-review/`: adversarial-review. Matt's two-axis review (Standards + Spec) with the
  reviewers run in the other model's CLI: `codex exec -m gpt-5.6-sol` when the caller is Claude,
  `claude -p --model claude-fable-5` when the caller is Codex. Fixed point optional (defaults to the merge base).
  Findings are tagged `[hard]` (documented-standard breach, any spec mismatch) or `[suggestion]`; ends with
  `Clean` / `Not clean` on hard findings only, so a loop can stop on it. Smell baseline lives in `references/smells.md`.
- `skills/mine/improve-codebase/`: improve-codebase. Matt's `improve-codebase-architecture` with the HTML report
  replaced by inline Markdown cards and Mermaid before/after fences (`references/report.md`); same explore and
  grilling steps, and accepts a scope from a calling skill.
