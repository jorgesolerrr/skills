#!/usr/bin/env bash
# link-skills.sh - link every skill in this registry into the agents' skill folders (Linux/macOS).
# Flattens skills/<source>/<name>/ into ~/.claude/skills/<name> and ~/.codex/skills/<name>.
# Re-runnable: removes dangling links, adds missing ones, reports name conflicts.
# Usage: ./link-skills.sh            (targets ~/.claude/skills and ~/.codex/skills)
#        ./link-skills.sh ~/.cursor/skills   (custom target dirs)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$ROOT/skills"
if [ $# -gt 0 ]; then TARGETS=("$@"); else TARGETS=("$HOME/.claude/skills" "$HOME/.codex/skills"); fi

for dst in "${TARGETS[@]}"; do
  mkdir -p "$dst"
  find "$dst" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete | sed 's/^/removed dead link: /'
  for skill in "$SRC"/*/*/; do
    skill="${skill%/}"
    name="$(basename "$skill")"
    [ -f "$skill/SKILL.md" ] || continue
    link="$dst/$name"
    if [ -L "$link" ]; then
      [ "$(readlink -f "$link")" = "$skill" ] || echo "CONFLICT $link -> $(readlink "$link") (wanted $skill)"
    elif [ -e "$link" ]; then
      echo "SKIP $link exists and is not a link"
    else
      ln -s "$skill" "$link"
    fi
  done
  echo "$dst: $(find "$dst" -maxdepth 1 -type l | wc -l) skills linked"
done
