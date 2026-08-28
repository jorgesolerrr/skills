---
name: deepen-ticket
description: "Run improve-codebase on the modules the current ticket branch touched and file its deepening candidates as a report in the repo. Third of three sessions, after `review-ticket`."
disable-model-invocation: true
---

Deepen the modules the ticket branch you are on has touched. The ticket id comes from the commit message (`#123`) or the branch name.

## Process

1. **Scope.** Record `git merge-base HEAD <default-branch>` once; the modules in scope are those owning the files in `git diff --name-only <sha>...HEAD`. Done when the list is non-empty.

2. **Delegate deepening.** Dispatch one `general-purpose` agent with two instructions: invoke the `improve-codebase` skill scoped to those modules, and write its candidates to `docs/reports/<ticket-id>.md` in the current directory. It replies with the path only. Done when the path is on disk; reply to the user with the path and a one-line summary of each candidate.
