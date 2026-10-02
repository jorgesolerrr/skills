---
name: review-ticket
description: "Loop an adversarial cross-model review of the current ticket branch until no hard findings remain (max three rounds, later rounds on the delta only); suggestions go to the user. Second of three sessions, after `implement-ticket`; `deepen-ticket` follows."
disable-model-invocation: true
---

Review the ticket branch you are on. The branch and its commits are the only state carried in: the ticket id comes from the commit message (`#123`) or the branch name. Fetch the ticket per `docs/agents/issue-tracker.md`. When that file is missing and the repo has a GitHub remote, fetch it with `gh issue view <id> --comments`; with neither, tell the user to run `/setup-matt-pocock-skills` and stop.

## Process

1. **Pin the fixed point.** Record `git merge-base HEAD <default-branch>` once; every round compares against that sha. Run typechecking and the full suite once now and save the result; reviewers read code and never run the suite. Done when `git rev-parse` resolves the sha, `git log <sha>..HEAD` shows the implementation commit, and the check result is saved.

2. **Review loop.** Each round, call the Skill tool with "adversarial-review", passing the fixed point, the ticket, and the saved check result. From round 2 on, also pass the **round history**: the previous round's head sha and the file `.scratch/review-<ticket-id>/round-<N-1>.md`, so the reviewers look at the delta and at whether the old findings were addressed.

   Findings come tagged: `[hard]` is a breach of a documented standard or a mismatch with the ticket; `[suggestion]` is a judgement call. The reviewer is the other model, so hard findings are not yours to argue with: fix each one, or write down why it is wrong. Suggestions are the user's decision: collect them, act on none.

   After fixing, rerun typechecking and the full suite, save the result, and commit: amend while the branch is un-pushed, a follow-up commit once it is. Then write `.scratch/review-<ticket-id>/round-<N>.md`: the round's head sha before your fixes, each hard finding verbatim, and how you handled it (fixed in which commit, or why not).

   Stop when a review ends `Clean`, when three rounds have run, or when a review ends `Incomplete` (a reviewer returned no verdict: report which axis and its output, and leave the retry to the user). Done when one of the three stops is reached and every remaining hard finding is listed with your reason for leaving it.

3. **Hand off.** Reply to the user with the rounds (hard findings fixed per round, any left open with your reason, or the incomplete axis), the suggestions from the final review verbatim under `## Suggestions` for the user to accept or drop, and that `/deepen-ticket` is the next session.
