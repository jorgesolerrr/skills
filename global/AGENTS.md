# Global rules

Loaded in every session, in every repo. A project's own `AGENTS.md` or `CLAUDE.md` adds to these.

## Language

- Reply in the language of my last message.
- Code, identifiers, commit messages, PR titles and PR bodies are in English, in every repo.

## Dictation

I dictate many prompts by voice, so names arrive garbled. Read them as:

| Heard | Meant |
|---|---|
| "open a pr ready for review", "the DPR", "TBR" (standing for a PR) | PR |
| "greeting session" | grilling session |
| "season" | session |
| "Group Tile", "Reptile" / "Rabbit" | Greptile / CodeRabbit |
| "Cloud", "Cloud Fable" | Claude, Claude Fable |
| "Sec", "PBSEC", "checkbacking" | CEC, PB-CEC, CEC-Backend |
| "skin-by" | kinby |
| "Fidetur", "Fijetu", "Fivetune" | Fideltour |
| "Royback", "Roy Back", "rollback" naming an integration | Roiback |
| "Senit" / "Safiro" | Zenit / Zafiro |

"Fidelity" is also a real HDH integration. When a dictated prompt says Fidelity and the Fidelity integration is not what the work is about, ask whether I meant Fideltour before acting. Ask the same whenever a garbled name could be two real things.

## Browser

Browser testing runs in Playwright's bundled Chromium with its own profile; keep sign-ins as saved storage state. My own Chrome stays untouched: end only the processes you started, by their PID.

## Logins and secrets

Interactive logins (`gh auth login`, `claude setup-token`, OAuth and device-code flows) are mine to run: print the exact command and wait for me. When a secret is needed, ask me to put it in the right `.env` or secret store, then read it from there.

## Checks

A check (tests, lint, format, typecheck) counts only by its exit code. When its output goes through `tail`, `head` or `Select-Object`, run it with `set -o pipefail` in bash, or test `$LASTEXITCODE` in PowerShell, before calling it green.

## Subagents

"Use subagents" means fan out: several fresh subagents in parallel, one per independent piece, each with a self-contained prompt. The main conversation coordinates and keeps only their results.

## Skills

graphify runs only when I ask for it by name.
