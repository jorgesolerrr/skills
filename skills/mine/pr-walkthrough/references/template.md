# Walkthrough template

Copy the skeleton below into `docs/walkthroughs/<pr-slug>/WALKTHROUGH.md` and fill every section in order. Keep the headings verbatim. Sections marked *(explanation)* carry the why and may hold a view. Sections marked *(reference)* describe, dry and complete. Drop **Spec match** only when no spec was found.

Diagram slots are image references to SVGs exported from `diagram-design` sources in `diagrams/`. Rules are in [`diagrams.md`](diagrams.md).

## Status vocabulary for Spec match

| Status | Meaning |
|---|---|
| `done` | The diff implements it as decided. |
| `partial` | Some of it is in the diff; name what is left. |
| `missing` | Nothing in the diff addresses it. |
| `deviated` | The diff does something else on purpose; name the difference and the reason if the PR gives one. |
| `deferred` | The PR or issue says it is out of scope for this change. |

---

````markdown
# <PR title>

| | |
|---|---|
| **Change** | PR #<n> · `<head-branch>` → `<base-branch>` · <n> commits |
| **Fixed point** | `<sha or ref>` |
| **Stamped at** | `<head sha>` (paths and lines are true at this commit) |
| **Issue** | #<n> <title>, or `none` |
| **Spec** | [`<path>`](<path>), or `none` |
| **Author** | <name> |

## At a glance *(explanation)*

Three sentences. What changed for the user, how the code got there, and the one module whose change carries the most risk.

## Link chain *(reference)*

| Hop | Found | Where |
|---|---|---|
| PR → issue | yes / no | #<n> |
| Issue → spec | yes / no | `<path>` |
| Spec → decisions | <n> decisions, <n> user stories | — |

## Change map *(reference)*

Which modules the diff touches and how they depend on each other after the change. Added, changed, and removed modules use the legend roles.

![Dependency graph of the modules this change touches, marked added, changed, or removed](diagrams/change-map.svg)

Source: [`change-map.html`](diagrams/change-map.html)

| Module | Files | Role in the change |
|---|---|---|
| `<module>` | `src/…`, `src/…` | changed · <one line> |

## How it works now *(reference)*

### Bird's-eye

One data-flow diagram of the feature after the change, boxes are modules, arrows carry the data or event that crosses.

![Data flow of <feature> after this change](diagrams/flow-after.svg)

Source: [`flow-after.html`](diagrams/flow-after.html)

Walkthrough: one numbered step per arrow, each naming the function and the `path:line` that does it.

### Flow: <name>

For each flow whose behavior changed, a before-and-after pair of sequence diagrams. For a new flow, the after only.

| Before | After |
|---|---|
| ![<flow> before this change](diagrams/flow-<slug>-before.svg) | ![<flow> after this change](diagrams/flow-<slug>-after.svg) |

What changed between the two: numbered, each item with its `path:line`.

## Impact on the project *(explanation)*

### Blast radius

Modules outside the diff that call a changed symbol.

![Modules that depend on the symbols this change touches](diagrams/blast-radius.svg)

Source: [`blast-radius.html`](diagrams/blast-radius.html)

### Contracts changed

| Symbol | Before | After | Callers |
|---|---|---|---|
| `module.fn` | `(a: A): B` | `(a: A, opts: O): B` | `src/…:12`, `src/…:40` |

### Tests

| Test file | Added or changed | Seam | Covers |
|---|---|---|---|
| `tests/…` | added | <seam> | <behavior> |

### Risks

Numbered. What could break, where you would see it first, and how to check.

## Spec match *(reference)*

### Decisions

| # | Decision | Status | Evidence |
|---|---|---|---|
| D1 | <decision, quoted from the spec> | done | `src/…:34` |

### User stories

| # | Story | Status | Evidence |
|---|---|---|---|
| 1 | <story, quoted> | partial | `src/…:70`, missing <what> |

### Not in the spec

Hunks that no decision or story explains. Each with `path:line` and a guess at why it is there.

### Totals

done <n> · partial <n> · missing <n> · deviated <n> · deferred <n>

## Reading order *(reference)*

Open the files in this order to understand the change. Every changed file appears once.

1. `src/…` — <why this first>
2. `src/…` — <what it adds to what you just read>

## Retrospective *(explanation)*

Candidates from the `retro` skill for the session that produced this change, in severity order. Each names the category, the moment in the session, and the proposed change to the environment.

## Glossary *(reference)*

Project-specific terms used above, one line each, matching the project's domain glossary.
````
