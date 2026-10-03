---
name: merge-train
description: "Merge a set of PRs: address each PR's review in a fresh subagent, squash-merge stacks bottom-up with children retargeted to the default branch, hand conflicts to a fresh subagent, and delete only branches of merged PRs."
disable-model-invocation: true
---

Get a **train** of PRs merged. The user names it: PR numbers, an issue or spec whose tickets the PRs close, or nothing (every open, non-draft PR in the repo).

You are the dispatcher. Subagents do the reviews and the conflict work, each in its own worktree, so this conversation holds only the train's state: which PR is where, and why.

## Process

### 1. Load the train

List the PRs with `gh pr list --state open --limit 200 --json number,title,headRefName,baseRefName,isDraft,mergeable,url,closingIssuesReferences`. For a spec or issue, keep the PRs whose `closingIssuesReferences` include one of its tickets.

Build the **stacks**: a PR whose base is another PR's head branch is that PR's child. Order the train with each stack as a unit, parent before child, and stacks and lone PRs by number.

Show the user the ordered train (stacks drawn as `#12 → #13 → #14`) and wait for their go. This is the only gate.

Done when the user has approved the order.

### 2. Address every review

Add `.worktrees/` to `.git/info/exclude` if it is not there. Then launch one fresh subagent per lone PR and one per stack, all in parallel. Each prompt carries:

- the absolute path of [`../address-review/SKILL.md`](../address-review/SKILL.md), to follow as written;
- the PR number; for a stack, the top PR's number plus `stack`;
- to work in a worktree per PR at `.worktrees/pr-<n>`;
- to return: one line per thread (verdict and action), the final head sha of each PR, the check status, and any **decision** threads verbatim.

Done when every subagent has reported. A PR with failing checks or open **decision** threads leaves the train, and takes every descendant in its stack with it: record why.

### 3. Merge in order

For each PR still on the train, in order:

1. `gh pr checks <n> --watch`: the PR's checks are green.
2. Its review threads are all resolved (re-run the query from address-review step 3).
3. Record its head sha, `gh pr view <n> --json headRefOid`: its children rebase off it.
4. For a PR with children, retarget each direct child first: `gh pr edit <child> --base <default-branch>`.
5. `gh pr merge <n> --squash --delete-branch`, then confirm `gh pr view <n> --json state` reads `MERGED`. The state decides, not the exit code: `--delete-branch` can exit non-zero when a worktree holds the branch.
6. For each child, drop the parent's commits that the squash replaced, in the child's worktree: `git fetch origin && git rebase --onto origin/<default-branch> <parent-head-sha>`, then `git push --force-with-lease`.

Red checks in 1, or a merge that leaves the PR open in 5: record the PR as stopped with the output, drop its descendants with it, and move to the next PR.

When the rebase in 6 stops, `git rebase --abort`. Then, as whenever a PR becomes `CONFLICTING` (a sibling's merge moved the default branch), launch a fresh subagent with the PR number and its worktree path. In that worktree it runs `git merge origin/<default-branch>`, resolves with the `resolving-merge-conflicts` skill, runs the repo's checks (AGENTS.md or CLAUDE.md names them; otherwise the commands CI runs), pushes, and returns the new head sha. Then continue with 1.

Done when every PR on the train is merged or recorded as stopped with its reason.

### 4. Clean up

Delete a branch only when `gh pr list --state merged --head <branch>` returns its PR. For each such branch: remove its `.worktrees/pr-<n>` worktree, then the local branch, then the remote branch if `--delete-branch` left it. Leave every other branch and worktree as it was. Then check out the default branch and pull.

Done when every deleted branch maps to a merged PR and `git worktree list` shows no `.worktrees/pr-<n>` worktree for a merged PR.

### 5. Report

A table: PR, outcome (merged with the squash sha, or stopped with the reason), threads fixed (`legit`) and answered `wrong`. List the branches deleted and any **decision** threads waiting for the user.
