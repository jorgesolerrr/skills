---
name: resolving-merge-conflicts
description: "Resolve an in-progress git merge or rebase that stopped on conflicts. Use when git reports CONFLICT or files carry `<<<<<<<` markers."
---

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`. In a rebase the sides swap: `ours` is the branch you are rebasing onto, `theirs` is your commit being replayed.

4. Discover the project's **automated checks** and run them, typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge/rebase.** Confirm `git diff --check` reports no conflict markers, then stage the files you resolved or fixed, by path. Run `git commit --no-edit` for a merge, or `git rebase --continue` for a rebase. A rebase stops again at each conflicting commit: repeat steps 1–5 for each one.

Done when `git status` shows no merge or rebase in progress and the checks from step 4 pass.
