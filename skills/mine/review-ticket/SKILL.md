---
name: review-ticket
description: "Loop an adversarial cross-model review of the current ticket branch until no hard findings remain (max five rounds); suggestions go to the user. Second of three sessions, after `implement-ticket`; `deepen-ticket` follows."
disable-model-invocation: true
---

Review the ticket branch you are on. The branch and its commits are the only state carried in: the ticket id comes from the commit message (`#123`) or the branch name, fetched per `docs/agents/issue-tracker.md` (if that file is missing, tell the user to run `/setup-matt-pocock-skills` and stop).

## Process

1. **Pin the fixed point.** Record `git merge-base HEAD <default-branch>` once; every round compares against that sha. Done when `git rev-parse` resolves it and `git log <sha>..HEAD` shows the implementation commit.

2. **Review loop.** Call the Skill tool with "adversarial-review", passing the fixed point and the ticket. Its findings come tagged: `[hard]` is a breach of a documented standard or a mismatch with the ticket; `[suggestion]` is a judgement call. The reviewer is the other model, so hard findings are not yours to argue with: fix each one, or write down why it is wrong. Suggestions are the user's decision: collect them, act on none. After fixing, run typechecking and the full suite, and commit: amend while the branch is un-pushed, a follow-up commit once it is. Repeat until a review comes back `Clean` (zero hard findings on both axes), or five rounds have run. Done when the last review reads `Clean`, or the remaining hard findings are listed for the user with your reason for leaving each.

3. **Hand off.** Reply to the user with the rounds (hard findings fixed per round, any left open with your reason), the suggestions from the final review verbatim under `## Suggestions` for the user to accept or drop, and that `/deepen-ticket` is the next session.
