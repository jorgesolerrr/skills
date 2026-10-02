#!/usr/bin/env bash
# link-skills.sh - link every skill in this registry into the agents' skill folders (Linux/macOS),
# then wire global/AGENTS.md into Claude Code and Codex.
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

# Global rules: one source (global/AGENTS.md), imported by Claude, copied for Codex.
GLOBAL="$ROOT/global/AGENTS.md"
IMPORT="@$GLOBAL"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
mkdir -p "$HOME/.claude" "$HOME/.codex"
if ! grep -qxF "$IMPORT" "$CLAUDE_MD" 2>/dev/null; then
  echo "$IMPORT" >> "$CLAUDE_MD"
  echo "Claude: added '$IMPORT' to $CLAUDE_MD"
fi
CODEX_MD="$HOME/.codex/AGENTS.md"
if [ -f "$CODEX_MD" ] && ! grep -q 'synced from' "$CODEX_MD"; then
  echo "Codex: $CODEX_MD exists and was not written by this script; left as is"
else
  { echo "<!-- synced from $GLOBAL by link-skills; edit the source, not this copy -->"; cat "$GLOBAL"; } > "$CODEX_MD"
  echo "Codex: synced $CODEX_MD"
fi
