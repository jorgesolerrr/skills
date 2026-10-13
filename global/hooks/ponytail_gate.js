// Gate for the ponytail hooks: run one of them only when the session's repo is in REPOS.
//
// Registered three times in ~/.claude/settings.json, as `node ponytail_gate.js <hook>`:
//   SessionStart -> activate, UserPromptSubmit -> mode-tracker, SubagentStart -> subagent.
// A session matches the way project_overlay.py matches: any folder in the project path, or the main
// checkout's folder name (via the git common dir, so worktrees count), equals a name in REPOS.
// No match, or any error: no output, exit 0. Stdin is left unread, for the ponytail script.
//
// Test: CLAUDE_PROJECT_DIR=C:/path/to/hoteldatahub node ponytail_gate.js activate
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const REPOS = new Set(['hoteldatahub']);
const HOOKS = new Set(['activate', 'mode-tracker', 'subagent']);
const PONYTAIL_HOOKS = path.join(__dirname, '..', '..', 'plugins', 'ponytail', 'hooks');

function matches(dir) {
  if (path.resolve(dir).split(/[\\/]+/).some((part) => REPOS.has(part.toLowerCase()))) return true;
  try {
    const common = execFileSync('git', ['rev-parse', '--path-format=absolute', '--git-common-dir'], {
      cwd: dir, encoding: 'utf8', timeout: 3000, stdio: ['ignore', 'pipe', 'ignore'], windowsHide: true,
    }).trim();
    const repo = path.basename(common) === '.git' ? path.dirname(common) : common;
    return REPOS.has(path.basename(repo).toLowerCase());
  } catch (e) {
    return false;
  }
}

const hook = process.argv[2];
let run = false;
try {
  run = HOOKS.has(hook) && matches(process.env.CLAUDE_PROJECT_DIR || process.cwd());
} catch (e) { /* a broken gate must never block a session */ }
if (!run) process.exit(0);

// ponytail-activate.js offers its statusline badge once, until this flag exists. Not wanted here.
if (hook === 'activate') {
  try {
    const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(require('os').homedir(), '.claude');
    fs.writeFileSync(path.join(claudeDir, '.ponytail-statusline-nudged'), '', { flag: 'wx' });
  } catch (e) { /* already there */ }
}

require(path.join(PONYTAIL_HOOKS, `ponytail-${hook}.js`));
