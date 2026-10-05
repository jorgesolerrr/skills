"""SessionStart hook: inject a per-repo overlay file as session context, for repos whose own CLAUDE.md/AGENTS.md is not mine.

A session matches a repo when the main checkout's folder name (via the git common dir, so worktrees count)
or any folder in the cwd path equals a key in OVERLAYS. Works for Claude Code and Codex: both read
`hookSpecificOutput.additionalContext` from a SessionStart hook. No match, or any error: no output, exit 0.

Test: echo '{"cwd": "C:/path/to/repo", "hook_event_name": "SessionStart"}' | python project_overlay.py
"""
import json
import subprocess
import sys
from pathlib import Path

SKILLS_REPO = Path(__file__).resolve().parents[2]

# Repo folder name (lowercase) -> overlay file, relative to the skills repo.
OVERLAYS = {
    "hoteldatahub": "skills/work/_hoteldatahub/context.md",
}


def repo_names(cwd):
    """Candidate repo names for cwd: the main checkout's folder first, then every folder in the path."""
    names = []
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        if common:
            common_path = Path(common)
            names.append((common_path.parent if common_path.name == ".git" else common_path).name)
    except (OSError, subprocess.SubprocessError):
        pass
    names.extend(part for part in reversed(Path(cwd).parts))
    return [n.lower() for n in names]


def overlay_for(cwd):
    for name in repo_names(cwd):
        if name in OVERLAYS:
            path = SKILLS_REPO / OVERLAYS[name]
            if path.is_file():
                return name, path
    return None


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        data = {}
    cwd = data.get("cwd") or str(Path.cwd())
    if not Path(cwd).is_dir():
        return
    match = overlay_for(cwd)
    if not match:
        return
    name, path = match
    text = f"<!-- {name} overlay, from {path} (Jorge's global setup) -->\n" + path.read_text(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a broken overlay must never block a session
        pass
    sys.exit(0)
