# Walkthrough template

Copy the skeleton below into `.walkthroughs/<pr-slug>/WALKTHROUGH.md` and fill every section in order. Keep the headings verbatim. Sections marked *(explanation)* carry the why and may hold a view. Sections marked *(reference)* describe, dry and complete. When there is no spec, drop **Link chain** and **Spec match** and write `none` for the spec in the header line. The retrospective is its own file, `RETRO.md`, shaped at the end of this page.

Diagrams are Mermaid fences in place. Rules are in [`diagrams.md`](diagrams.md).

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

PR #<n> · `<head-branch>` → `<base-branch>` · <n> commits · fixed point `<sha or ref>` · stamped at `<head sha>` · issue #<n> or `none` · spec [`<path>`](<path>) or `none`

## At a glance *(explanation)*

Three sentences. What changed for the user, how the code got there, and the one module whose change carries the most risk.

## Link chain *(reference, with a spec only)*

| Hop | Found | Where |
|---|---|---|
| PR → issue | yes / no | #<n> |
| Issue → spec | yes / no | `<path>` |
| Spec → decisions | <n> decisions | — |

## Change map *(reference)*

Which modules the diff touches and how they depend on each other after the change. Every node carries `added`, `changed`, `removed`, or nothing for untouched context.

```mermaid
flowchart TB
```

Figure: dependency graph of the modules this change touches, marked added, changed, or removed.

| Module | Files | Role in the change |
|---|---|---|
| `<module>` | `src/…`, `src/…` | changed · <one line> |

## How it works now *(reference)*

### Bird's-eye

One data-flow diagram of the feature after the change, boxes are modules, arrows carry the data or event that crosses.

```mermaid
flowchart LR
```

Figure: data flow of <feature> after this change.

Walkthrough: one numbered step per arrow, each naming the function and the `path:line` that does it.

### Flow: <name>

For each flow whose behavior changed, a before-and-after pair of sequence diagrams with the same participants in the same order. For a new flow, the after only.

#### Before

```mermaid
sequenceDiagram
```

#### After

```mermaid
sequenceDiagram
```

Figure: <flow> before and after this change, changed messages marked.

What changed between the two: numbered, each item with its `path:line`.

## Impact on the project *(explanation)*

### Blast radius

Modules outside the diff that call a changed symbol.

```mermaid
flowchart TB
```

Figure: modules that depend on the symbols this change touches.

### Contracts changed

| Symbol | Before | After | Callers |
|---|---|---|---|
| `module.fn` | `(a: A): B` | `(a: A, opts: O): B` | `src/…:12`, `src/…:40` |

### Data types changed

Every type the diff adds or changes (dataclass, record, DTO, interface, event, config object), drawn after the change with fields marked `added`, `changed`, or `removed`. A schema change is an ER diagram.

```mermaid
classDiagram
```

Figure: types this change adds or changes and how they relate.

### Tests

| Test file | Added or changed | Seam | Covers |
|---|---|---|---|
| `tests/…` | added | <seam> | <behavior> |

### Risks

Numbered. What could break, where you would see it first, and how to check.

## Spec match *(reference, with a spec only)*

### Decisions

| # | Decision | Status | Evidence |
|---|---|---|---|
| D1 | <decision, quoted from the spec> | done | `src/…:34` |

### Not in the spec

Hunks that no decision explains. Each with `path:line` and a guess at why it is there.

### Totals

done <n> · partial <n> · missing <n> · deviated <n> · deferred <n>

## Reading order *(reference)*

Open the files in this order to understand the change. Every changed file appears once.

1. `src/…` — <why this first>
2. `src/…` — <what it adds to what you just read>

## Glossary *(reference)*

Project-specific terms used above, one line each, matching the project's domain glossary.
````

## RETRO.md

Written by step 5 of the skill from the `retro` skill's candidates, in severity order.

````markdown
# Retro: <PR title>

Session: <current session, or the log paths read>

## 1. <Category> · <one-line title>

**Moment.** What happened in the session, with the tool call or turn where it shows.

**Proposed change.** The edit to the environment: which file, hook, check, or tool, and the exact change.

## 2. …
````

When no session logs exist, the file holds the single line `No session logs available`.
