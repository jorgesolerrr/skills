---
name: merge-train
description: "Merge a set of PRs: address each PR's review in a fresh subagent (a native stack's fixes all land on its top branch), squash-merge a native GitHub stack in one `gh stack merge` and other stacks bottom-up with children retargeted to the default branch, hand conflicts to a fresh subagent, and delete only branches of merged PRs."
disable-model-invocation: true
---

Get a **train** of PRs merged. The user names it: PR numbers, an issue or spec whose tickets the PRs close, or nothing (every open, non-draft PR in the repo).

You are the dispatcher. Subagents do the reviews and the conflict work, each in its own worktree, so this conversation holds only the train's state: which PR is where, and why.

## Process

### 1. Load the train

List the PRs with `gh pr list --state open --limit 200 --json number,title,headRefName,baseRefName,isDraft,mergeable,url,closingIssuesReferences`. For a spec or issue, keep the PRs whose `closingIssuesReferences` include one of its tickets.

Build the **stacks**: a PR whose base is another PR's head branch is that PR's child. Order the train with each stack as a unit, parent before child, and stacks and lone PRs by number.

For each stack, check whether GitHub tracks it as a **native stack**: `gh api repos/<owner>/<repo>/pulls/<n> --jq .stack` returns `{number, position, size, base}` on every PR of one, and `null` otherwise. A native stack merges in one step (3a); any other stack merges PR by PR (3b).

Show the user the ordered train (stacks drawn as `#12 → #13 → #14`, each marked native or not) and wait for their go. This is the only gate.

Done when the user has approved the order.

### 2. Address every review

Add `.worktrees/` to `.git/info/exclude` if it is not there. This conversation coordinates every unit itself, so each step stays visible to the user. A subagent addresses one PR and never launches subagents of its own.

List each PR's unresolved review threads with the query from address-review step 3. A PR with none needs only `gh pr checks <n>` read. Every other PR gets one fresh subagent, and units run in parallel. Each prompt carries:

- the absolute path of [`../address-review/SKILL.md`](../address-review/SKILL.md), to follow for that one PR, with the overrides of its unit below;
- the PR number and its worktree, `.worktrees/pr-<n>`;
- to return: one line per thread (verdict and action), the fix commit sha, the check status, and any **decision** threads verbatim.

**A lone PR**: the worktree is on its head branch, and address-review runs as written.

**A native stack**: every fix goes on the top PR's branch. The top holds every PR below it and 3a merges the stack all-or-nothing, so the fixes reach the default branch together and no branch below the top changes. The stack's subagents all run in parallel, and each prompt adds:

- the worktree is detached at `origin/<top-branch>`, and every verdict reads the code there. A thread on code that a later PR of the stack rewrote is **already fixed**, citing that PR.
- the checks are the tests covering the change, plus lint and typecheck; the top PR's CI runs the full checks.
- after committing `Address review on #<n>`: `git fetch origin && git rebase origin/<top-branch>` (a sibling's fix on the same lines goes through `resolving-merge-conflicts`), then `git push origin HEAD:<top-branch>`. A rejected push repeats the fetch, rebase and push.
- the reply cites the pushed sha: `Fixed in <sha> on #<top>: <what changed>.`

Then wait for the top PR's checks: `gh pr checks <top> --watch`.

**Any other stack** merges PR by PR in 3b, so each PR carries its own fixes. Walk it bottom first. Before a PR's subagent starts, merge its fixed parent into its head branch in `.worktrees/pr-<n>` and push; a conflict goes to that subagent. Subagents run in parallel only for PRs whose parent did not change.

A background subagent can stop with an interim result ("waiting for the subagent") while it still owes work. That is not its report: resume it with SendMessage, tell it to finish the remaining PRs and to end only with the final report.

Done when every subagent has sent its final report. A PR with failing checks or open **decision** threads leaves the train, and takes every descendant in its stack with it: record why. In a native stack whose top branch holds fixes, a PR that leaves takes the whole stack, since the fixes for the PRs below it would not merge.

### 3. Merge in order

Take the train's units in order: a native stack goes through 3a, and a lone PR or any other stack goes through 3b.

#### 3a. A native stack

The [`gh stack`](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) extension (`gh extension install github/gh-stack`) merges the stack. If the extension is missing, merge the stack through 3b.

1. Each PR from the bottom up to the top one still on the train: `gh pr checks <n>` exits 0, and its review threads are all resolved. If a PR fails, the top of the merge becomes the PR below it, and the failing PR and every PR above it are recorded as stopped. When the top branch holds review fixes, the whole stack stops instead.
2. `gh stack merge <top-n> --squash --yes`. It merges every PR from the bottom up to `<top-n>` in one all-or-nothing operation, one squash commit per PR, bottom first, so nothing has to be retargeted or rebased. GitHub requires every PR in it to be approved where branch protection requires approval, its checks to be green, and the stack's history to be linear. If GitHub reports the history as not linear, run `gh stack rebase` from a worktree of the top branch, then `gh stack push`, and retry.
3. Confirm that `gh pr view <n> --json state,mergeCommit` reads `MERGED` for every PR, and record each squash sha. The merge leaves the head branches on the remote, and step 4 deletes them.

When the merge fails, no PR has merged. Record the stack as stopped with the output, or fall back to 3b if the error is about the stack itself rather than a PR's checks or reviews.

#### 3b. PR by PR

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

Delete a branch only when `gh pr list --state merged --head <branch>` returns its PR. For each such branch: remove its `.worktrees/pr-<n>` worktree, then the local branch, then the remote branch if the merge left it (`gh stack merge` always does, and `--delete-branch` can). Leave every other branch and worktree as it was. Then check out the default branch and pull.

Run the merge and the cleanup from the repo root, never from inside a worktree you are about to remove. On Windows, `git worktree remove --force` can deregister a worktree and still fail to delete its folder: `Directory not empty` (`node_modules`, `.venv`), or `Permission denied` while a shell sits inside it. Delete any such leftover `.worktrees/pr-<n>` folder of a merged PR, then run `git worktree prune`.

When the pull is blocked by uncommitted changes in the main checkout, those changes are the user's. Leave them untouched: no stash, checkout or reset. Report that the default branch is behind and which files block the pull.

Done when every deleted branch maps to a merged PR, and neither `git worktree list` nor the disk holds a `.worktrees/pr-<n>` of a merged PR.

### 5. Report

A table: PR, outcome (merged with the squash sha, or stopped with the reason), threads fixed (`legit`) and answered `wrong`. List the branches deleted and any **decision** threads waiting for the user.
