---
name: greploop
description: Loop a PR through Greptile review until 5/5 confidence with zero unresolved comments.
disable-model-invocation: true
license: MIT
compatibility: Requires git and gh (GitHub CLI) authenticated, and Greptile installed on the repo.
metadata:
  author: greptileai
  version: "1.3"
allowed-tools: Bash(gh:*) Bash(git:*)
---

# Greploop

Iteratively fix a PR until Greptile gives a perfect review: 5/5 confidence, zero unresolved comments.

## Inputs

- **PR number** (optional): If not provided, detect the PR for the current branch.

## Instructions

### 1. Identify the PR

```bash
gh pr view --json number,headRefName,headRefOid
```

Switch to the PR branch if not already on it.

Key fields: `number`, `headRefName`, `headRefOid`.

### 2. Loop

Repeat the following cycle. **Max 5 iterations** to avoid runaway loops.

#### A. Trigger Greptile review

Push the latest changes (if any):

```bash
git push
```

Check if Greptile is already running before posting a new trigger comment:

```bash
GREPTILE_STATE=$(gh pr checks <PR_NUMBER> --json name,state --jq '.[] | select(.name | test("greptile"; "i")) | .state')
```

If Greptile is **not** already running (`PENDING` or `IN_PROGRESS`), request a fresh review:

```bash
if [ "$GREPTILE_STATE" != "PENDING" ] && [ "$GREPTILE_STATE" != "IN_PROGRESS" ]; then
  gh pr comment <PR_NUMBER> --body "@greptile review"
fi
```

Then poll for the Greptile check run to complete. The loop runs up to 10 minutes, so run this block with a 600000 ms timeout (or in the background):

```bash
HEAD_SHA=$(gh pr view <PR_NUMBER> --json headRefOid -q .headRefOid)
ATTEMPTS=0
MAX_ATTEMPTS=60
POLL_INTERVAL_SECONDS=10

while true; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -gt "$MAX_ATTEMPTS" ]; then
    echo "Timed out waiting for the Greptile check run after approximately 10 minutes." >&2
    exit 1
  fi

  GREPTILE_CHECK=$(gh api "repos/{owner}/{repo}/commits/$HEAD_SHA/check-runs" \
    --jq '.check_runs[] | select(.name | test("greptile"; "i")) | "\(.status // "completed") \(.conclusion // "pending")"' 2>/dev/null)

  if [ -z "$GREPTILE_CHECK" ]; then
    echo "Waiting for Greptile check to appear..."
    sleep "$POLL_INTERVAL_SECONDS"
    continue
  fi

  read -r STATUS CONCLUSION <<< "$GREPTILE_CHECK"

  if [ "$STATUS" = "completed" ]; then
    if [ "$CONCLUSION" = "success" ]; then
      echo "Greptile check passed!"
    else
      echo "Greptile check completed with: $CONCLUSION"
    fi
    break
  fi

  echo "Waiting for Greptile... (status: $STATUS)"
  sleep "$POLL_INTERVAL_SECONDS"
done
```

If polling times out, stop the greploop workflow and report the timeout. Do not continue with stale or missing review results.

#### B. Fetch Greptile review results

Greptile may surface its score in several places — check **all** of them:

**1. PR description (body):**
```bash
gh pr view <PR_NUMBER> --json body -q '.body'
```

**2. General PR comments (issue comments):**
```bash
gh api --paginate "repos/{owner}/{repo}/issues/<PR_NUMBER>/comments?per_page=100"
```

Filter for Greptile-authored comments and use the body from the most recently updated comment (`updated_at`), not the most recently created comment. Greptile may edit the same general PR comment on each review cycle; parse the current body, including the "Prompt to fix all with AI" section, before deciding there are no remaining issues.

**3. PR reviews:**
```bash
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews
```

Look for the most recent entry from `greptile-apps[bot]` or `greptile-apps-staging[bot]`.

Parse the text for:
- **Confidence score**: a pattern like `3/5` or `5/5` (or `Confidence: 3/5`).
- **Comment count**: Number of inline review comments noted in the summary.

**4. Unresolved review threads** (`gh` fills `{owner}` and `{repo}`; see [GraphQL reference](references/graphql-queries.md)):
```bash
gh api graphql --paginate -F owner='{owner}' -F repo='{repo}' -F pr=<PR_NUMBER> -f query='
query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes { body path author { login } }
          }
        }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)'
```

The unresolved comment count is the number of threads this returns.

Use whichever source has the **most recently updated** score. Prefer `updated_at` from issue comments when comparing an edited Greptile summary against older review entries.

Also carry forward actionable items from the latest Greptile general PR comment, especially the "Prompt to fix all with AI" section, even if the thread query in B.4 returns zero unresolved threads.

#### C. Check exit conditions

Stop the loop if **any** of these are true:

- Confidence score is **5/5** AND there are **zero unresolved comments**
- Max iterations reached (report current state)

#### D. Fix actionable comments

For each unresolved Greptile comment:

1. Read the file and understand the comment in context.
2. Determine if it's actionable (code change needed) or informational.
3. If actionable, make the fix.
4. If informational or a false positive, note it but still resolve the thread.

#### E. Resolve threads

Resolve every thread handled in D (fixed, informational, or false positive), using the thread IDs from B.4:

```bash
gh api graphql -f query='
mutation {
  t1: resolveReviewThread(input: {threadId: "ID1"}) { thread { isResolved } }
  t2: resolveReviewThread(input: {threadId: "ID2"}) { thread { isResolved } }
}'
```

#### F. Commit and push

If `git status --porcelain` is empty after D, exit the loop and report the remaining comments as informational. Otherwise stage only the files you edited:

```bash
git add <files you edited>
git commit -m "address greptile review feedback (greploop iteration N)"
git push
```

Then go back to step **A**.

### 3. Report

After exiting the loop, summarize:

| Field              | Value      |
| ------------------ | ---------- |
| Iterations         | N          |
| Final confidence   | X/5        |
| Comments resolved  | N          |
| Remaining comments | N (if any) |

If the loop exited due to max iterations, list any remaining unresolved comments and suggest next steps.

## Output format

```
Greploop complete.
  Iterations:    2
  Confidence:    5/5
  Resolved:      7 comments
  Remaining:     0
```

If not fully resolved:

```
Greploop stopped after 5 iterations.
  Confidence:    4/5
  Resolved:      12 comments
  Remaining:     2

Remaining issues:
  - src/auth.ts:45 — "Consider rate limiting this endpoint"
  - src/db.ts:112 — "Missing index on user_id column"
```
