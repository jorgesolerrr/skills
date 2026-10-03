---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at the seams the spec or ticket names; ask only when none is named.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

If HEAD is the default branch, create a branch first. Commit your work to it.

Then run /adversarial-review against the merge base and fix every [hard] finding in a follow-up commit.

Done when every requirement in the spec has a passing test at a seam, the full suite is green, and no [hard] finding is left.
