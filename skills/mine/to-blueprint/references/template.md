# Blueprint template

Copy the skeleton below into `docs/blueprints/<feature-slug>/BLUEPRINT.md` and fill every section in order. Keep the headings verbatim so blueprints are navigable as a set. Sections marked *(explanation)* carry the why and may hold a view. Sections marked *(reference)* describe, dry and complete.

Diagrams are Mermaid fences in place. Rules for choosing, drawing, and marking them are in [`diagrams.md`](diagrams.md).

---

````markdown
# <Feature name>

Stamped at `<short commit sha>`: paths and symbols are true at this commit.

## At a glance *(explanation)*

Three sentences. What the user gets, the shape of the solution, the one decision that most constrains it.

## Problem *(explanation)*

The problem from the user's perspective. Specific: the situation they are in and what goes wrong.

## Solution *(explanation)*

The solution from the user's perspective. What changes for them, not how.

## Decision log *(explanation)*

One row per decision settled in the grilling. Numbered so later sections can cite `D3`.

| # | Decision | Chosen | Rejected | Why |
|---|---|---|---|---|
| D1 | <question the grilling asked> | <choice> | <alternatives> | <reason, one or two sentences> |

## Bird's-eye flow *(reference)*

One diagram of the whole feature end to end. Boxes are modules or systems. Arrows carry the data or event that crosses. Cite decisions on the arrows where a decision picked the route, for example `D2`.

```mermaid
flowchart LR
```

Figure: data flow of <feature> from <entry> to <exit>.

Prose walkthrough: one numbered step per arrow, in order.

## Module map *(reference)*

Which modules are touched and how they depend on each other after the change. New modules carry the `new` class. Each module's public interface is listed under the diagram: the functions or types other modules call, with their signatures.

```mermaid
flowchart TB
```

Figure: dependency graph of the modules <feature> touches, new ones marked.

### Interfaces

- `moduleB.doThing(input: Shape): Result` — <one line: what it does, who calls it>.

## Ground-level flows *(reference)*

One subsection per flow named in the bird's-eye diagram. Each has a sequence diagram (or state machine when the flow is a lifecycle) whose participants are the functions from the module map, followed by a numbered step list that names the data shape at each hop.

### Flow: <name>

```mermaid
sequenceDiagram
```

Figure: sequence of calls for <flow name>, with the data shape at each hop.

1. <step>: input `<shape>`, output `<shape>`.

## Data shapes *(reference)*

Every type the feature adds or changes, drawn as a class diagram with its fields and relations. Schema changes as an ER diagram. New types carry the `new` class. A code snippet appears only for a decision a diagram cannot hold, trimmed to that part.

```mermaid
classDiagram
```

Figure: types <feature> adds or changes and how they relate.

## File map *(reference)*

Every file the agent touches. `create`, `modify`, or `delete`. Stamped at the commit in the header; regenerate the existence check with `git ls-files <paths>`.

| Path | Action | What changes | Flow |
|---|---|---|---|
| `src/…` | modify | <one line> | <flow name> |

## Testing *(reference)*

- **Seams**: where the feature is tested and why that seam (cite the decision).
- **What a good test looks like here**: external behavior only, no implementation details.
- **Prior art**: existing tests of the same kind, by path.
- **Cases**: numbered list of the behaviors the tests must cover, each naming its flow and the decision it protects.

## Out of scope *(reference)*

What this blueprint deliberately leaves out, and where it goes instead if known.

## Open questions *(reference)*

Points the grilling did not settle. Each with the options on the table and the recommended default. The agent building this stops and asks before acting on any of them.

## Glossary *(reference)*

Terms used in this doc that are project-specific, one line each, matching the project's domain glossary.
````
