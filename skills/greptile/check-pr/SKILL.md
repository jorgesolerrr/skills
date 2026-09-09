---
name: check-pr
description: >
  Checks a GitHub pull request for unresolved review comments, failing status checks, and an
  incomplete PR description. Waits for pending checks to complete, categorizes issues as actionable
  or informational, and optionally fixes and resolves them. Use when the user wants to check a PR,
  address review feedback, or prepare a change for merge.
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
gh pr view --json number -q .number
```

Key fields: `number`, `headRefName`, `headRefOid`.

### 2. Fetch PR details

```bash
gh pr view <PR_NUMBER> --json title,body,state,reviews,comments,headRefName,statusCheckRollup
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments
gh api --paginate "repos/{owner}/{repo}/issues/<PR_NUMBER>/comments?per_page=100"
```

GitHub PRs are also issues, so general PR comments live on the issue comments endpoint. Greptile may edit a single general PR comment on each review cycle instead of creating a new review or comment. Always inspect the latest Greptile-authored general comment by `updated_at`, including any "Prompt to fix all with AI" section, before concluding that the PR is clear.

### 3. Wait for pending checks

Before analyzing, ensure all status checks have completed. If any checks are `PENDING` or `IN_PROGRESS`, poll `statusCheckRollup` from `gh pr view` every 30 seconds until all checks reach a terminal state.

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

1. Switch to the PR's branch if not already on it.
2. Ask the user if they want to fix the issues.
3. If yes, make the fixes, then commit and push:

```bash
git add <files>
git commit -m "address review feedback"
git push
```

### 8. Resolve review threads

After addressing comments, resolve the corresponding review threads.

Fetch unresolved thread IDs (paginate if needed — see [the GraphQL reference](references/graphql-queries.md)):

```bash
gh api graphql -f query='
query($cursor: String) {
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: PR_NUMBER) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes { body path }
          }
        }
      }
    }
  }
}'
```

If `hasNextPage` is true, repeat with `-f cursor=ENDCURSOR` to get remaining threads.

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
