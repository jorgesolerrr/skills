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
  doc for one feature (`docs/blueprints/<slug>/`): decision log, bird's-eye and ground-level diagrams (diagram-design HTML exported to SVG),
  module map, file map, testing seams. Composed from `to-spec`, `writing-for-agents`,
  `technical-writing`, and `diagram-design`.
- `skills/mine/pr-walkthrough/`: pr-walkthrough. Visual walkthrough of a PR or branch
  (`docs/walkthroughs/<slug>/`): change map, flow after the change, before-and-after flows, blast
  radius, spec-match tables against the linked issue's spec or blueprint, reading order, and a
  retrospective produced by following `retro` as-is. Shares diagram and prose rules with `to-blueprint`.
