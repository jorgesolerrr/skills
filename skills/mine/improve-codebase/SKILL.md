---
name: improve-codebase
description: "Survey a codebase, or the modules a calling skill names, for deepening opportunities, then grill the one the user picks. Use when the user asks where the architecture hurts or wants refactor candidates."
---

# Improve codebase

Surface architectural friction and propose **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

This skill is _informed_ by the project's domain model and built on a shared design vocabulary:

- Call the Skill tool with "codebase-design" for the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles (the deletion test, "the interface is the test surface", "one adapter = hypothetical seam, two = real"). Its [`DEEPENING.md`](../codebase-design/DEEPENING.md) defines the four dependency categories a card's badge names.
- The domain language in `GLOSSARY.md` gives names to good seams; ADRs in `docs/adr/` record decisions this skill should not re-litigate.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user or a calling skill named a direction (a module, a subsystem, a pain point, the modules a diff touched), take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots, the files and areas that keep coming up, and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Read the project's domain glossary (`GLOSSARY.md`, if it exists) and any ADRs in the area you're touching first.

Then spawn a sub-agent to walk the codebase. Brief it with the scope and the `codebase-design` vocabulary. It explores organically and notes where it experiences friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow**, with an interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

It applies the **deletion test** to anything it suspects is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want. It returns each suspect module with its files and its deletion-test verdict.

Done when every named module or hot spot in scope has been walked and you hold 3 to 6 candidates, or can say why there are fewer.

### 2. Present candidates inline

Write the candidates into your reply as Markdown. Render each candidate as a card per [references/report.md](references/report.md), which also holds the scaffold, the diagram patterns, and the tone.

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (a blockquote callout: _"contradicts ADR-0007, but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

Interfaces come later, in the grilling loop. Once the candidates are presented:

- **Called by the user**: ask "Which of these would you like to explore?"
- **Called by another skill**: skip the question and the grilling loop; write or return the cards where the caller asks, then stop.

### 3. Grilling loop

Once the user picks a candidate, call the Skill tool with "grilling" to walk the decision tree with them: constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize; call the Skill tool with "domain-modeling" to keep the domain model current as you go:

- **Naming a deepened module after a concept not in `GLOSSARY.md`?** Add the term to `GLOSSARY.md`. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `GLOSSARY.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing; skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Want to explore alternative interfaces for the deepened module?** Call the Skill tool with "codebase-design" and use its design-it-twice parallel sub-agent pattern.
