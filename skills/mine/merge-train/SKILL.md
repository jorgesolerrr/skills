---
name: merge-train
description: "Merge a set of PRs: address each PR's review in a fresh subagent, squash-merge stacks bottom-up with children retargeted to the default branch, hand conflicts to a fresh subagent, and delete only branches of merged PRs."
disable-model-invocation: true
---

Get a **train** of PRs merged. The user names it: PR numbers, an issue or spec whose tickets the PRs close, or nothing (every open, non-draft PR in the repo).

You are the dispatcher. Subagents do the reviews and the conflict work, each in its own worktree, so this conversation holds only the train's state: which PR is where, and why.

## Process

### 1. Load the train

List the PRs with `gh pr list --state open --json number,title,headRefName,baseRefName,isDraft,mergeable,url`. For a spec or issue, keep the PRs whose body closes one of its tickets.

Build the **stacks**: a PR whose base is another PR's head branch is that PR's child. Order the train with each stack as a unit, parent before child, and stacks and lone PRs by number.

Show the user the ordered train (stacks drawn as `#12 → #13 → #14`) and wait for their go. This is the only gate.

Done when the user has approved the order.

### 2. Address every review

Launch one fresh subagent per lone PR and one per stack, all in parallel. Each prompt carries:

- the absolute path of [`../address-review/SKILL.md`](../address-review/SKILL.md), to follow as written;
- the PR number, plus `stack` for a stack;
- to work in a worktree at `.worktrees/train-<n>`;
- to return: one line per thread (verdict and action), the final head sha, the check status, and any **decision** threads verbatim.

Done when every subagent has reported. A PR with failing checks or open **decision** threads leaves the train: record why.

### 3. Merge in order

For each PR still on the train, in order:

1. `gh pr checks <n> --watch`: the PR's checks are green.
2. Its review threads are all resolved (re-run the query from address-review step 3).
3. For a PR with children, retarget each direct child first: `gh pr edit <child> --base <default-branch>`.
4. `gh pr merge <n> --squash --delete-branch`.
5. For each child, drop the parent's commits that the squash replaced: `git rebase --onto origin/<default-branch> <parent-head-sha> <child-branch>`, then `git push --force-with-lease`. Note the parent's head sha before merging.

When a PR becomes `CONFLICTING` (a sibling's merge moved the default branch, or the rebase in 5 stopped), launch a fresh subagent with the PR number and its worktree path. It resolves with the `resolving-merge-conflicts` skill, runs the repo's checks, pushes, and returns the new head sha. Then continue with 1.

Done when every PR on the train is merged or recorded as stopped with its reason.

### 4. Clean up

Delete a branch only when `gh pr list --state merged --head <branch>` returns its PR. For each such branch: remove its `.worktrees/train-*` worktree, then the local branch, then the remote branch if `--delete-branch` left it. Leave every other branch and worktree as it was. Then check out the default branch and pull.

Done when every deleted branch maps to a merged PR and `git worktree list` shows no `train-` worktree for a merged PR.

### 5. Report

A table: PR, outcome (merged with the squash sha, or stopped with the reason), threads fixed and declined. List the branches deleted and any **decision** threads waiting for the user.
