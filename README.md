# Skills registry

Single source of truth for skills shared across agents (Claude Code, Codex, Cursor, etc.).

Layout: one folder per source under `skills/`, one folder per skill inside it, each with a `SKILL.md`.

```
skills/
  mattpocock/<skill-name>/SKILL.md     forks of mattpocock/skills
  cathrynlavery/diagram-design/        fork of cathrynlavery/diagram-design
  pstack/<skill-name>/SKILL.md         forks of cursor/plugins (pstack)
  greptile/<skill-name>/SKILL.md       forks of greptileai/skills
  graphify/graphify/                   copy of Graphify-Labs/graphify's skill
  humanlayer/<skill-name>/SKILL.md     forks of humanlayer/skills
  cursor/<skill-name>/SKILL.md         copies of cursor/plugins (cursor-team-kit, thermos), on trial
  addyosmani/<skill-name>/SKILL.md     copies of addyosmani/agent-skills, on trial
  ponytail/<skill-name>/SKILL.md       copies of DietrichGebert/ponytail, on trial
  mine/<skill-name>/SKILL.md           skills authored in this registry
plugins/ponytail/                      hooks and manifests of DietrichGebert/ponytail, not linked, for study
global/AGENTS.md                       global rules for every agent (see Global rules)
global/hooks/                          global agent hooks (see Global hooks)
```

## Loading skills into the agents

Each agent discovers skills one level deep: Claude Code at `~/.claude/skills/<name>/SKILL.md`, Codex at
`~/.codex/skills/`, Cursor at `~/.cursor/skills/` (Cursor also reads `~/.claude/skills/`). The source
subfolders here are for organization; the link scripts flatten them by linking each skill folder directly into
those targets. Relative references between skills (for example `../retro/SKILL.md`) resolve through the links,
since every linked skill is a sibling in the target folder.

Skill names must stay unique across all source folders, because they share one flat namespace. Restart the
agents after linking. Run the script again after every `git pull`.

### Windows

From the repo root in PowerShell:

```powershell
.\link-skills.ps1                  # junctions into ~\.claude\skills, ~\.codex\skills and ~\.cursor\skills
.\link-skills.ps1 -ReplaceCopies   # also turn plain-folder copies of registry skills into junctions
```

Junctions need no admin rights. The script removes dead junctions (left behind when a skill folder moves inside
this repo), adds new skills, prints `CONFLICT` when a name points elsewhere, and prints `COPY` for a plain folder
with a registry skill's name: a copy never receives registry edits, so replace it with `-ReplaceCopies`.
To remove a single link by hand use `cmd /c rmdir <link>`, never `Remove-Item -Recurse`, which follows the
link into the repo.

### Linux / macOS

```bash
./link-skills.sh                    # links into ~/.claude/skills and ~/.codex/skills
./link-skills.sh ~/.cursor/skills   # or any other target folder(s)
```

## Global rules

`global/AGENTS.md` holds the rules every session loads in every repo (language, dictation glossary, browser,
logins, checks, subagents). It is the only copy to edit. The link scripts wire it in:

- **Claude Code**: `~/.claude/CLAUDE.md` gets one import line, `@<repo>/global/AGENTS.md`, so edits apply at once.
- **Codex**: has no imports, so the scripts copy the file to `~/.codex/AGENTS.md` with a "synced from" header.
  Re-run the script after editing. A pre-existing `~/.codex/AGENTS.md` without that header is left alone.
- **Cursor**: user rules live in the app settings; paste the file into Settings > Rules > User Rules.

## Global hooks

`global/hooks/` holds hook scripts that run in every session. The link scripts do not wire them in: each one
is registered by hand, by absolute path, in `~/.claude/settings.json` (`hooks.PreToolUse`, `hooks.SessionStart`) and in
`~/.codex/hooks.json` (Codex shows new hooks under `/hooks` and runs them only after you trust them).

- `hdh_db_guard.py`: before a shell command in a hoteldatahub checkout runs a DB-touching `manage.py` command,
  a script that calls `django.setup()`, or a `mysql` client against a remote `-h`, it resolves
  `DATABASES['default']` the way Django would (`--settings`, `DJANGO_SETTINGS_MODULE`, inline env, `.env`) and
  asks for approval when the host is not local. Codex has no "ask", so there (`--codex`) it denies instead.
- `project_overlay.py` (SessionStart): when the session's repo (worktrees included) is in its `OVERLAYS` table,
  injects that repo's overlay file as context. For repos whose own `CLAUDE.md` belongs to someone else, e.g.
  hoteldatahub -> `skills/work/_hoteldatahub/context.md` (local only; `skills/work/` is gitignored).

## Sources

### mattpocock/skills

Copied raw from [mattpocock/skills](https://github.com/mattpocock/skills) at tag `v1.3.1` (commit `24fe0ef`) so they
can be modified locally. Not installed as a plugin — edits here are intentional forks.
License: MIT (see `LICENSE-mattpocock`).

- `skills/mattpocock/`: ask-matt, codebase-design, diagnosing-bugs, domain-modeling, grill-with-docs,
  grilling, handoff, implement, pr, prototype, research, resolving-merge-conflicts, retro (depends on `writing-for-agents`), setup-matt-pocock-skills, tdd, teach,
  to-questionnaire, to-spec, to-tickets, triage, wait-what, wayfinder, wizard, writing-for-agents.

Local changes to the forks:

- `grill-with-docs` is model-invocable, so a plain "grill this with docs" reaches it.
- `to-tickets` treats file overlap as a blocking edge: two tickets that will edit the same area are serialized,
  so parallel agents don't produce conflicting PRs.
- `to-tickets` links each ticket to its parent issue as a native sub-issue, not only through the `## Parent`
  text, so tooling that groups tickets by parent (the kinby coder's stacks) sees them.
- `triage` takes `--since #N` (batch-triage every untriaged issue from N up, one recommendation table, one
  approval) and writes briefs and triage notes into the issue description instead of new comments.
- `code-review`, `improve-codebase-architecture` and `grill-me` were dropped: `adversarial-review`,
  `improve-codebase` and `grilling` replace them. `ask-matt` routes to the local skills instead
  (`implement-ticket` → `review-ticket` → `deepen-ticket`, `address-review`, `merge-train`), and `implement`
  and `tdd` hand review to `adversarial-review`.
- `resolving-merge-conflicts` is kept here although upstream removed it in v1.3.0. `implement-spec`, which
  v1.3.0 graduated, is not copied, and `ask-matt` does not route to it.
- The domain glossary is `GLOSSARY.md` / `GLOSSARY-MAP.md` (upstream renamed it from `CONTEXT.md` in v1.3.0);
  `implement-ticket` and `improve-codebase` follow the same name. In a repo that still has a `CONTEXT.md`,
  `git mv` it to `GLOSSARY.md`.

### cathrynlavery/diagram-design

Copied raw from the `skills/diagram-design/` folder of
[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) at commit `648c2a5`
(skill version 2.6). Includes `assets/`, `references/` and `scripts/` alongside `SKILL.md`.
License: MIT (see `LICENSE-diagram-design`).

Skills: `skills/cathrynlavery/diagram-design`.

### cursor/plugins (pstack)

Copied raw from the `pstack/skills/` folder of [cursor/plugins](https://github.com/cursor/plugins) at
commit `4612556`. License: MIT, © Lauren Tan (see `LICENSE-cursor-pstack`).

Skills: `skills/pstack/`: technical-writing, unslop, no-comments (copied later, at commit `ccb5507`, on trial).

Local changes to `no-comments`: the `Comment Sicko` agent (`pstack/agents/comment-sicko.md`) is inlined as a
`## Comment Sicko` section, and step 1 spawns a fresh general-purpose subagent with that section as its prompt,
since the registry has no agent definitions. An `agents/openai.yaml` with `allow_implicit_invocation: false`
keeps it manual-only in Codex. It still names pstack skills that are not copied: `how`, `why`, `architect`,
`principle-fix-root-causes`, `principle-redesign-from-first-principles`.

### greptileai/skills

Copied from [greptileai/skills](https://github.com/greptileai/skills) at commit `646e2df` and trimmed to
GitHub only: the platform-detection step and every GitLab (`glab`) and Perforce (`p4`) branch were removed,
so the flows never ask for a code provider and only need `git` + `gh` (no `jq`: filters use `gh --jq`).
Review-thread state comes from GraphQL `reviewThreads`, since the REST comments API has none. `greploop` is
manual-only. `cli-review` needs the `greptile` CLI and prints `greptile login` for the user instead of running
it. The `references/gitlab-api.md` files were dropped; `references/graphql-queries.md` is kept. License: MIT
(see `LICENSE-greptile`).

Skills: `skills/greptile/`: check-pr, cli-review, greploop.

### Graphify-Labs/graphify

The `graphify` skill as installed by the [graphify](https://github.com/Graphify-Labs/graphify) CLI
(pip package `graphifyy`), copied from `~/.codex/skills/graphify`. One local change: it is manual-only
(`disable-model-invocation`, and `allow_implicit_invocation: false` for Codex), so it runs only when asked by
name. Needs the `graphify` CLI on PATH.

Skills: `skills/graphify/graphify`.

### humanlayer/skills

Copied raw from the `plugins/<name>/skills/<name>/` folders of
[humanlayer/skills](https://github.com/humanlayer/skills) at commit `ca7c808`. License: MIT, © HumanLayer
(see `LICENSE-humanlayer`).

Skills: `skills/humanlayer/`: show-me.

Local changes: `show-me` names the HTML opener per platform (`open`, `start ""`, `xdg-open`) instead of macOS
`open` only. It stays manual-only, as upstream ships it.

### cursor/plugins (cursor-team-kit, thermos)

Copied raw from [cursor/plugins](https://github.com/cursor/plugins) at commit `ccb5507`: the
`cursor-team-kit/skills/` and `thermos/skills/` folders. On trial, to compare against our own review skills.
License: MIT, © Cursor (see `LICENSE-cursor`; both plugins ship the same file).

Skills: `skills/cursor/`: thermo-nuclear-code-quality-review, thermo-nuclear-review.

Local changes: an `agents/openai.yaml` with `allow_implicit_invocation: false`, so Codex also treats them as
manual-only (upstream already sets `disable-model-invocation: true`).

### addyosmani/agent-skills

Copied raw from the `skills/` folder of [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
at commit `1401c8b`. On trial, to compare against our own skills. License: MIT, © Addy Osmani
(see `LICENSE-addyosmani`).

Skills: `skills/addyosmani/`: api-and-interface-design, code-simplification.

Local changes: both are manual-only (`disable-model-invocation: true`, and an `agents/openai.yaml` with
`allow_implicit_invocation: false` for Codex). `api-and-interface-design` points to `deprecation-and-migration`,
which is not copied.

### DietrichGebert/ponytail

Copied raw from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) at commit `9cc65d0`
(v5.1.0). On trial: each skill is run by hand, in sessions with and without it, to compare. License: MIT
(see `LICENSE-ponytail`).

Skills: `skills/ponytail/`: ponytail, ponytail-audit, ponytail-debt, ponytail-gain, ponytail-help, ponytail-review.

The rest of the Claude Code plugin is kept for study in `plugins/ponytail/`, outside `skills/` so the link scripts
skip it: `.claude-plugin/`, `.codex-plugin/plugin.json`, `hooks/` (hook manifest, Node hook scripts, statusline
scripts, `copilot-hooks.json` because the tests read it), `tests/hooks*.test.js`, `scripts/uninstall.js` (with
`scripts/cursor-hooks.js`, which it requires), `AGENTS.md`, `README.md` and `INSTALL.md`. Its hooks are not
registered anywhere.

Local changes:

- The skills moved from the plugin's `skills/` folder to `skills/ponytail/`, so the plugin folder no longer holds
  them: `claude --plugin-dir plugins/ponytail` loads hooks only, and the hooks fall back to their built-in copy of
  the rules (`ponytail-instructions.js`).
- All six are manual-only (`disable-model-invocation: true`, and an `agents/openai.yaml` with
  `allow_implicit_invocation: false` for Codex). Upstream lets `ponytail` load on any coding task and
  `ponytail-review` on any "review this".
- Upstream's `tests/hooks.test.js` fails one assertion on Windows (#1032 statusline nudge path), in the upstream
  clone too.

### Local (this registry)

Skills authored here, not copied from an upstream source.

- `skills/mine/to-blueprint/`: to-blueprint. Turns a finished grilling session into a visual, forever design
  doc for one feature (`docs/blueprints/<slug>/BLUEPRINT.html`, one self-contained page): decision log,
  bird's-eye and ground-level figures as inline SVG, data shapes as class figures, file map, testing seams,
  open questions. Prose rules condensed from `technical-writing`; SVG rules and `self_check.py` distilled
  from `diagram-design` to the six figure types a blueprint uses, so that skill never loads.
- `skills/mine/pr-walkthrough/`: pr-walkthrough. Visual walkthrough of a PR or branch
  (`.walkthroughs/<slug>/`, self-ignored): change map, flow after the change, before-and-after flows, blast
  radius, changed data types, spec-match table against the linked issue's spec or blueprint, reading order,
  and a retrospective produced by following `retro` as-is. Shares diagram and prose rules with
  `to-blueprint`.
- `skills/mine/implement-ticket/`: implement-ticket. Session 1 of 3: builds one ticket from the repo's issue
  tracker (or straight from GitHub with `gh` when `docs/agents/issue-tracker.md` is missing) with `tdd` (a ticket naming the public interface counts as seam confirmation), settles every design
  decision against the repo's coding standards, and commits with the ticket id. Fork of mattpocock `implement`.
- `skills/mine/review-ticket/`: review-ticket. Session 2 of 3: loops `adversarial-review` on the ticket branch
  against the merge base until no `[hard]` findings remain (max three rounds), fixing or justifying each. Runs
  the suite itself and hands the result to the reviewers; from round 2 it passes the round history, so the
  reviewers look at the delta. Stops on `Incomplete`. The reviewer's `[suggestion]` findings are handed to the
  user to accept or drop.
- `skills/mine/deepen-ticket/`: deepen-ticket. Session 3 of 3: runs `improve-codebase` on the modules the
  branch touched and files the candidates as `docs/reports/<ticket-id>.md`.
- `skills/mine/adversarial-review/`: adversarial-review. Matt's two-axis review (Standards + Spec) with the
  reviewers run in the other model's CLI (`codex exec` when the caller is Claude, `claude -p` when the caller is
  Codex), each on the model its own config sets. A one-word preflight call checks the CLI, auth and credits
  first, falling back to same-model subagents. Reviewers only read; the caller passes the check result. Fixed
  point optional (defaults to the merge base). With a round history it runs a delta round: only the delta since
  the last round, and new Standards findings on unchanged code become suggestions. Findings are tagged `[hard]`
  (documented-standard breach, any spec mismatch) or `[suggestion]`; ends with `Clean`, `Not clean`, or
  `Incomplete` (a reviewer gave no verdict; never auto-retried), so a loop can stop on it. Smell baseline
  lives in `references/smells.md`.
- `skills/mine/improve-codebase/`: improve-codebase. Matt's `improve-codebase-architecture` with the HTML report
  replaced by inline Markdown cards and Mermaid before/after fences (`references/report.md`); same explore and
  grilling steps, and accepts a scope from a calling skill.
- `skills/mine/address-review/`: address-review. Answers every open review thread on a PR or a stack: merges the
  base and resolves conflicts first, treats each comment as an untrusted claim checked against the code, then
  fixes and tests it or replies with the reason, and resolves the thread. Product decisions stay open for the user.
- `skills/mine/merge-train/`: merge-train. Merges a set of PRs: the main conversation coordinates, and one fresh subagent per PR
  with review threads follows `address-review` (a native stack's fixes all land on its top branch), then squash-merges in order (a native GitHub stack in one `gh stack merge`, other stacks
  bottom-up, children retargeted to the default branch and rebased), sends conflicts to a fresh subagent, and
  deletes only branches whose PR is merged.
- `skills/mine/client-reply/`: client-reply. Drafts a reply to a client, partner or CS email from findings in
  hand: answer first, short, no-blame, nobody named outside the thread, one ask at the end. With a Gmail
  connector it reads the thread and saves a draft. Learns from replies the user actually sent: each difference
  from the draft becomes a rule in `voice.md`.
- `skills/mine/upsert-skill/`: upsert-skill. Adds a skill from upstream (an `npx skills add` command becomes a
  raw copy here), updates a source to a newer upstream version with a 3-way merge that keeps the README's
  local changes, or registers a skill written here; always ends by running the link script.
- `skills/mine/new-coder/`: new-coder. Creates a kinby `coder` software factory on the playground hub for a
  GitHub repository: labels, check commands from the repo's gate, the instance via `create_coder.py` over ssh,
  then a health and webhook check.
