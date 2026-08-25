# Skills registry

Single source of truth for skills shared across agents (Claude Code, Codex, Cursor, etc.).

Layout: one folder per skill under `skills/`, each containing a `SKILL.md`.

```
skills/
  <skill-name>/
    SKILL.md
```

To expose a skill to Claude Code, link it into (junctions need no admin rights on Windows; symlinks do) `~/.claude/skills/`:

## Sources

### mattpocock/skills

Copied raw from [mattpocock/skills](https://github.com/mattpocock/skills) at commit `6654f6b` so they can
be modified locally. Not installed as a plugin — edits here are intentional forks.
License: MIT (see `LICENSE-mattpocock`).

- `skills/engineering/`: ask-matt, code-review, codebase-design, diagnosing-bugs, domain-modeling,
  grill-with-docs, implement, improve-codebase-architecture, prototype, research,
  resolving-merge-conflicts, setup-matt-pocock-skills, tdd, to-spec, to-tickets, triage, wayfinder, wizard.
- `skills/productivity/`: grill-me, grilling, handoff, teach, to-questionnaire, wait-what, writing-for-agents.
- `skills/in-progress/`: retro (depends on `writing-for-agents`).

### cathrynlavery/diagram-design

Copied raw from the `skills/diagram-design/` folder of
[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) at commit `648c2a5`
(skill version 2.6). Includes `assets/`, `references/` and `scripts/` alongside `SKILL.md`.
License: MIT (see `LICENSE-diagram-design`).

Skills: diagram-design.

### cursor/plugins (pstack)

Copied raw from the `pstack/skills/` folder of [cursor/plugins](https://github.com/cursor/plugins) at
commit `4612556`. License: MIT, © Lauren Tan (see `LICENSE-cursor-pstack`).

Skills: technical-writing, unslop.
