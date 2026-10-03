---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads. If you are already a subagent, do the research yourself.

The job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it; mark a claim with no primary source as **unverified**.
2. Write the findings to a single Markdown file, linking each claim's source.
3. Save it where the repo already keeps such notes; with no convention, use `docs/research/<slug>.md`. When the caller names a branch, commit it there.

Done when the file exists and every claim carries a source link or the unverified mark. Report the file path and a three-line summary.
