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

### mattpocock/skills (engineering)

Copied raw from the `skills/engineering/` folder of
[mattpocock/skills](https://github.com/mattpocock/skills) at commit `6654f6b` so they can be
modified locally. Not installed as a plugin — edits here are intentional forks.
License: MIT (see `LICENSE-mattpocock`).

Skills: ask-matt, code-review, codebase-design, diagnosing-bugs, domain-modeling, grill-with-docs,
implement, improve-codebase-architecture, prototype, research, resolving-merge-conflicts,
setup-matt-pocock-skills, tdd, to-spec, to-tickets, triage, wayfinder, wizard.

### cathrynlavery/diagram-design

Copied raw from the `skills/diagram-design/` folder of
[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) at commit `648c2a5`
(skill version 2.6). Includes `assets/`, `references/` and `scripts/` alongside `SKILL.md`.
License: MIT (see `LICENSE-diagram-design`).

Skills: diagram-design.

