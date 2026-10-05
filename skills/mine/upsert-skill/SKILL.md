---
name: upsert-skill
description: "Add a skill to this skills registry or update the ones it holds, then sync the links. Use when the user asks to add, install or vendor a skill (including an `npx skills add` command), to update a source's skills to a newer upstream version, or to register a skill written here."
---

**Upsert** skills into this registry (the repo holding `link-skills.ps1`): insert a new one or update an existing one, then sync. The registry copy is the install; the agents read it through the links the sync script makes. Read `README.md` first: its `## Sources` section records each source's upstream, base commit, license file and **local changes** (the fork edits every update must keep).

## 1. Classify

Each skill named in the request takes one branch:

- **Add**: a skill from upstream that the registry lacks. An `npx skills add <owner>/<repo> --skill <name>` command names the GitHub repo `<owner>/<repo>` and the skill `<name>`; run the clone below in its place.
- **Update**: a source already under `skills/<source>/`, moved to a newer upstream tag or commit. With no version named, take the latest tag and say which.
- **Register**: a skill written in this registry (`skills/mine/`), needing only its README entry and the sync.

## 2. Add

1. Clone the upstream into the scratchpad and record the commit (`git log -1 --format=%h`).
2. Check the name is free: no `skills/*/<name>/` folder exists. Skill names share one flat namespace across sources.
3. Read every file of the skill before copying it. It becomes instructions every agent follows, so flag to the user any step that runs remote code, sends data out, or touches secrets.
4. Copy the skill folder raw to `skills/<source>/<name>/` (`<source>` is the upstream owner, or an existing source folder for that repo). Copy the upstream license to `LICENSE-<source>` when the source is new.
5. Fix only what breaks on this machine (Windows), such as a macOS-only command, and list each fix as a local change.
6. Add or extend the source's README entry: upstream link and folder, commit, license file, `Skills:` list, local changes. A new source also gets a line in the layout block at the top.

Done when the files are in place and the README entry names the commit and every local change.

## 3. Update

1. Clone the upstream into the scratchpad. Take the base commit from the README entry and the target version from the request.
2. List what moved: `git diff -M --name-status <base> <target> -- <skills path>`. Map each local skill to its upstream path at both commits; a skill can change bucket folders between versions.
3. For every file changed upstream, merge three ways: `git merge-file <ours> <base> <theirs>`. The working copies are CRLF (`core.autocrlf=true`) and upstream is LF, so strip `\r` from the local file into a temp copy, merge that, and write it back with CRLF. Merging the CRLF file directly conflicts on every line.
4. Resolve each conflict hunk: keep every local change the README lists, and take upstream for everything else. Read both sides of each hunk to decide; a hunk can hold a local wording choice that upstream also touched.
5. Apply renames (`git mv`, then merge the content), removals and new skills. A skill upstream removed or newly added is the user's call, so keep or skip it and report which.
6. When upstream renames a convention (a file name, a term), grep the whole registry for the old name: skills in other sources often follow it.
7. Update the README entry: new commit or tag, skill list, local changes.

Done when no file under `skills/` holds a conflict marker (`grep -rn '^<<<<<<<\|^>>>>>>>' skills`) and every upstream change since the base is either merged or reported as skipped.

## 4. Register

Add the skill's entry under `### Local (this registry)` in the README: its path and one or two lines on what it does.

## 5. Sync

Mandatory after every upsert, including a README-only one. From the repo root:

- Windows: `.\link-skills.ps1`
- Linux / macOS: `./link-skills.sh`

Done when the output has no `CONFLICT` or `COPY` line and each upserted skill's `SKILL.md` resolves under every target the script printed (`~/.claude/skills/<name>/SKILL.md`, and the same for `.codex` and `.cursor`). On a `COPY` line, ask before re-running with `-ReplaceCopies`, which deletes that plain folder. On a `CONFLICT` line, report it: another folder already owns that name.

Report what was added, updated or skipped, the local changes kept, and that the agents need a restart to load the change.
