---
name: cli-review
description: >
  Run the Greptile CLI on the local branch and summarize its findings. Use when the user wants
  Greptile feedback before a PR exists.
license: MIT
metadata:
  author: greptileai
  version: "1.0"
allowed-tools: Bash(git:*) Bash(greptile:*) Bash(command:*) Bash(npm:*)
---

# CLI Review

Run a Greptile review from the local checkout and summarize the findings.

## Instructions

### 1. Confirm repository context

Start from the current repository root:

```bash
git rev-parse --show-toplevel
```

If the command fails, tell the user that the Greptile CLI review must be run from a git repository.

### 2. Check for the Greptile CLI

Check whether `greptile` is installed:

```bash
command -v greptile
```

If it is missing, do not install it automatically. Ask the user for permission, then show the recommended install command:

```bash
npm i -g greptile
```

After installation, re-run `command -v greptile`.

### 3. Ensure authentication

Check the signed-in account:

```bash
greptile whoami
```

If not signed in, print `greptile login` for the user to run, and wait for them to confirm.

### 4. Run the review

Prefer JSON output:

```bash
greptile review --json
```

For a stacked branch pass `-b <base>`; if `--json` fails, show the raw error.

### 5. Summarize results

Parse the JSON output and report:

- Review status
- Number of findings
- Highest severity findings first
- Files that need edits
- Suggested next command or fix path

Keep the summary concise and focused on actionable findings.
