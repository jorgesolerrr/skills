---
name: check-pr
description: >
  Report a GitHub PR's merge readiness: pending or failing checks, unresolved review threads, an
  incomplete description, and optionally fix them. Use when the user asks for a PR's status or
  whether it is ready to merge.
license: MIT
compatibility: Requires git and gh (GitHub CLI) installed and authenticated.
metadata:
  author: greptileai
  version: "1.3"
allowed-tools: Bash(gh:*) Bash(git:*)
---

# Check PR

Analyze a GitHub pull request for review comments, status checks, and description completeness, then help address any issues found.

## Inputs

- **PR number** (optional): If not provided, detect the PR for the current branch.

## Instructions

### 1. Identify the PR

If a number was provided, use it. Otherwise, detect it:

```bash
gh pr view --json number,headRefName,headRefOid
```

Key fields: `number`, `headRefName`, `headRefOid`.

### 2. Fetch PR details

```bash
gh pr view <PR_NUMBER> --json title,body,state,reviews,comments,headRefName,statusCheckRollup
gh api --paginate "repos/{owner}/{repo}/issues/<PR_NUMBER>/comments?per_page=100"
```

Fetch inline review threads with their resolution state, keeping only unresolved ones (`gh` fills `{owner}` and `{repo}` and follows `endCursor` across pages):

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
          comments(first: 3) {
            nodes { body path author { login } }
          }
        }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)'
```

GitHub PRs are also issues, so general PR comments live on the issue comments endpoint. Greptile may edit a single general PR comment on each review cycle instead of creating a new review or comment. Always inspect the latest Greptile-authored general comment by `updated_at`, including any "Prompt to fix all with AI" section, before concluding that the PR is clear.

### 3. Wait for pending checks

Before analyzing, ensure all status checks have completed. If any checks are `PENDING` or `IN_PROGRESS`, wait for them to reach a terminal state:

```bash
gh pr checks <PR_NUMBER> --watch --interval 30
```

### 4. Analyze the PR

Once all checks are complete, evaluate these areas:

#### A. Status Checks

- Are all CI checks passing?
- If any are failing, identify which ones and the failure reason.

#### B. PR Description

- Is the description complete and follows team conventions?
- Are all required sections filled in?
- Are there TODOs or placeholders that need updating?

#### C. Review Comments

- Inline code review comments that need addressing
- Look for bot review comments (e.g. from `greptile-apps[bot]`, linters, etc.)
- Human reviewer comments

#### D. General Comments

- Discussion comments on the PR
- Check the issue comments endpoint and use `updated_at` to catch bot comments edited in place. Greptile's latest edited summary can contain actionable items even when there are no new inline comments.
- Bot comments (deploy previews, etc.) — usually informational

### 5. Categorize issues

For each issue found, categorize as:

| Category | Meaning |
|---|---|
| **Actionable** | Code changes, test improvements, or fixes needed |
| **Informational** | Verification notes, questions, or FYIs that don't require changes |
| **Already addressed** | Issues that appear to be resolved by subsequent commits |

### 6. Report findings

Present a summary table:

| Area | Issue | Status | Action Needed |
|------|-------|--------|---------------|
| Status Checks | CI build failing | Failing | Fix type error in `src/api.ts` |
| Review | "Add null check" — @reviewer | Actionable | Add guard clause |
| Description | TODO placeholder in test plan | Actionable | Fill in test plan |
| Review | "Looks good" — @teammate | Informational | None |

### 7. Fix issues (if requested)

If there are actionable items:

1. Ask the user if they want to fix the issues.
2. If yes, switch to the PR's branch if not already on it.
3. Make the fixes, then commit and push:

```bash
git add <files>
git commit -m "address review feedback"
git push
```

### 8. Resolve review threads

After addressing comments, resolve the corresponding review threads.

Use the unresolved thread IDs fetched in step 2 ([GraphQL reference](references/graphql-queries.md)).

Then resolve threads that have been addressed or are informational:

```bash
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "THREAD_ID"}) {
    thread { isResolved }
  }
}'
```

Batch multiple resolutions into a single mutation using aliases (`t1`, `t2`, etc.).

### 9. Multiple PRs

If checking a chain of PRs, process them sequentially.

## Output format

Summarize:
- PR title and current state
- Status checks summary (passing/failing/pending)
- Total issues found
- Actionable items with descriptions
- Items that can be ignored with reasons
- Recommended next steps
