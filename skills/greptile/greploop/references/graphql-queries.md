# GraphQL Queries Reference

Useful GitHub GraphQL queries for working with PR review threads.

## Fetch unresolved review threads (with pagination)

```bash
gh api graphql --paginate -F owner='{owner}' -F repo='{repo}' -F pr=<PR_NUMBER> -f query='
query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100, after: $endCursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          comments(first: 3) {
            nodes {
              body
              path
              author { login }
              createdAt
            }
          }
        }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)'
```

`gh` fills `{owner}` and `{repo}`, and `--paginate` follows `endCursor` until `hasNextPage` is `false`.

## Resolve a single review thread

```graphql
mutation {
  resolveReviewThread(input: {threadId: "THREAD_ID"}) {
    thread { isResolved }
  }
}
```

## Batch-resolve multiple threads

Use GraphQL aliases to resolve several threads in one request:

```graphql
mutation {
  t1: resolveReviewThread(input: {threadId: "THREAD_ID_1"}) {
    thread { isResolved }
  }
  t2: resolveReviewThread(input: {threadId: "THREAD_ID_2"}) {
    thread { isResolved }
  }
  t3: resolveReviewThread(input: {threadId: "THREAD_ID_3"}) {
    thread { isResolved }
  }
}
```

## Fetch PR details (REST)

```bash
gh pr view <PR_NUMBER> --json title,body,state,reviews,comments,headRefName,statusCheckRollup
```

## Fetch general PR comments edited in place (REST)

General PR comments are issue comments. Greptile may update one summary comment repeatedly, so select by `updated_at` instead of `created_at`:

```bash
gh api --paginate "repos/{owner}/{repo}/issues/<PR_NUMBER>/comments?per_page=100" \
  --jq '.[] | select(.user.login | test("greptile"; "i")) | {author: .user.login, updated_at, body}'
```

`--jq` runs once per page, so pick the comment with the latest `updated_at` from the output.
