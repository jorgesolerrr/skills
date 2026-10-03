---
name: deepen-ticket
description: "Run improve-codebase on the modules the current ticket branch touched and file its deepening candidates as a report in the repo. Third of three sessions, after `review-ticket`."
disable-model-invocation: true
---

Deepen the modules the ticket branch you are on has touched. The ticket id comes from the commit message (its tracker id, `#123` or `ABC-123`) or the branch name.

## Process

1. **Scope.** Record `git merge-base HEAD <default-branch>` once, the default branch coming from `git symbolic-ref refs/remotes/origin/HEAD`; the modules in scope are those owning the files in `git diff --name-only <sha>...HEAD`. When that list is empty, tell the user the branch has no diff against the default branch and stop. Done when the list is non-empty.

2. **Delegate deepening.** Create `docs/reports/` if it is missing. Dispatch one subagent (general-purpose in Claude Code) with two instructions: run the `improve-codebase` skill through its **Called by another skill** branch, scoped to those modules; and write its candidates to `docs/reports/<ticket-id>.md` in the current directory. It replies with the path only. Done when the path is on disk.

3. **Report.** Read the report, then reply to the user with its path and a one-line summary of each candidate. Tell them the report is left uncommitted, for them to place.
