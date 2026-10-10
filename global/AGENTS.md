# Global rules

Loaded in every session, in every repo. A project's own `AGENTS.md` or `CLAUDE.md` adds to these.

## Browser

Browser testing runs in Playwright's bundled Chromium with its own profile; keep sign-ins as saved storage state. My own Chrome stays untouched: end only the processes you started, by their PID, and use the Claude in Chrome tools only when I ask for them.

## Logins and secrets

Interactive logins (`gh auth login`, `claude setup-token`, OAuth and device-code flows) are mine to run: print the exact command and wait for me. When a secret is needed, ask me to put it in the right `.env` or secret store, then let the program load it (its settings module, `uv run --env-file`, `dotenv run`); never read `.env` yourself. Variable names live in the repo's `.env.example`.

## Checks

A check (tests, lint, format, typecheck) counts only by its exit code. When its output goes through `tail`, `head` or `Select-Object`, run it with `set -o pipefail` in bash, or test `$LASTEXITCODE` in PowerShell, before calling it green.

## Shell

Write multi-line content (files, scripts, issue and PR bodies) with Write or Edit; to run a script, Write it to the scratchpad and run the file. Bash heredocs fail on this machine when the body holds a quote.

Read diffs by `git diff --stat` first, then per file. Read GitHub data with `--json <fields> -q`.

Wait on CI with `gh pr checks <n> --watch --fail-fast` or `gh run watch <id> --exit-status`, run in the background.

## Git

In repos whose `origin` owner is `jorgesolerrr`, commit docs-only changes straight to main and push; any other change goes on a branch with a PR. Work repos always take a branch and a PR: the `pb-cec` and `Fideltour` orgs, and the PB-CEC project repos under `jorgesolerrr` (`PB-CEC-*`, `CEC-*`).

## Subagents

"Use subagents" means fan out: several fresh subagents in parallel, one per independent piece, each with a self-contained prompt. The main conversation coordinates and keeps only their results.
