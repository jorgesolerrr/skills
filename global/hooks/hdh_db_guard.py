"""PreToolUse guard: stop coding agents from writing to a non-local hoteldatahub DB.

Claude Code: registered in ~/.claude/settings.json (matcher "Bash|PowerShell").
Codex:       registered in ~/.codex/hooks.json with --codex (Codex cannot "ask",
             so a non-local target becomes "deny").

Reads the PreToolUse JSON on stdin. Exits 0 with no output unless the shell
command is a DB-touching Django/MySQL call inside a hoteldatahub checkout. For
those it resolves DATABASES['default'] the way Django would (--settings,
DJANGO_SETTINGS_MODULE, inline env overrides, .env) in a subprocess with the
repo's own interpreter, and asks for approval when the host is not local.

It never prints secrets: only ENGINE, HOST and NAME leave the subprocess.
There is deliberately no bypass switch.
"""

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time

CANONICAL_ROOT = r"C:\00_Mis cosas\Proyectos\FidelTour\hoteldatahub"
LOCAL_HOSTS = {"", "localhost", "127.0.0.1", "::1", "0.0.0.0", "mysql_container", "db"}
SHELL_TOOLS = {"bash", "powershell", "shell", "shell_command", "exec_command", "local_shell"}

# manage.py subcommands that never write to the DB. Anything else, including
# unknown custom commands, is treated as a possible write.
SAFE_MANAGE_CMDS = {
    "check", "help", "version", "showmigrations", "sqlmigrate", "makemigrations",
    "diffsettings", "collectstatic", "findstatic", "compilemessages", "makemessages",
    "startapp", "startproject", "inspectdb", "dumpdata", "squashmigrations",
}
MYSQL_CLIENTS = {"mysql", "mysqldump", "mysqladmin", "mysqlimport", "mysqlsh", "mariadb"}
PYTHON_RE = re.compile(r"^(python[0-9.]*|py|pythonw)(\.exe)?$", re.I)
SETTINGS_DEFAULT_RE = re.compile(r"DJANGO_SETTINGS_MODULE['\"]\s*,\s*['\"]([\w.]+)['\"]")
SEP_TOKENS = {";", "&&", "||", "|", "&", "(", ")", ";;", "|&"}
RESOLVE_TIMEOUT = 15
CACHE_DIR = os.path.join(tempfile.gettempdir(), "hdh_db_guard")

# Runs inside the repo's interpreter. Stubs sentry_sdk so importing settings
# never initialises Sentry, and prints only ENGINE/HOST/NAME.
RESOLVER = r'''
import importlib, importlib.abc, importlib.machinery, io, json, os, sys, types
root, module = sys.argv[1], sys.argv[2]
sys.path.insert(0, root)
os.chdir(root)

class _Any(types.ModuleType):
    __path__ = []
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return _Any(name)
    def __call__(self, *a, **k):
        return _Any("call")

class _Finder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, name, path, target=None):
        if name == "sentry_sdk" or name.startswith("sentry_sdk."):
            return importlib.machinery.ModuleSpec(name, self, is_package=True)
        return None
    def create_module(self, spec):
        return _Any(spec.name)
    def exec_module(self, module):
        pass

sys.meta_path.insert(0, _Finder())
real_stdout = sys.stdout
sys.stdout = io.StringIO()
try:
    mod = importlib.import_module(module)
    db = (getattr(mod, "DATABASES", None) or {}).get("default") or {}
    out = {"ok": True, "engine": str(db.get("ENGINE", "")), "host": str(db.get("HOST", "") or ""),
           "name": str(db.get("NAME", ""))}
except BaseException as exc:
    msg = str(exc).splitlines()[0][:160] if str(exc) else ""
    out = {"ok": False, "error": type(exc).__name__ + (": " + msg if msg else "")}
sys.stdout = real_stdout
print("HDHGUARD::" + json.dumps(out))
'''


# ---------------------------------------------------------------- paths

def to_win(path):
    path = path.strip().strip("'\"")
    m = re.match(r"^/([a-zA-Z])(/.*)?$", path)
    if m:
        path = m.group(1).upper() + ":" + (m.group(2) or "/")
    if path.startswith("~"):
        path = os.path.expanduser(path)
    return path


def resolve_dir(base, path):
    path = to_win(path)
    if not path:
        return base
    if not os.path.isabs(path):
        path = os.path.join(base, path)
    return os.path.normpath(path)


def is_hdh_root(path):
    return os.path.isfile(os.path.join(path, "manage.py")) and os.path.isfile(
        os.path.join(path, "hoteldatahub", "settings_dev.py"))


def find_root(path):
    if not path:
        return None
    path = os.path.normpath(to_win(path))
    if os.path.isfile(path):
        path = os.path.dirname(path)
    while True:
        if is_hdh_root(path):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


# ---------------------------------------------------------------- parsing

def tokenize(command, powershell):
    text = command.replace("\r", "")
    text = re.sub(r"\n", " ; ", text)
    if powershell:
        text = text.replace("\\", "/")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=";&|()")
        lex.whitespace_split = True
        lex.commenters = ""
        tokens = list(lex)
    except ValueError:
        tokens = re.findall(r"\"[^\"]*\"|'[^']*'|[;&|()]+|[^\s;&|()]+", text)
        tokens = [t.strip("'\"") for t in tokens]
    return [t.replace("\\", "/") for t in tokens]


def segments(tokens):
    seg = []
    for tok in tokens:
        if tok in SEP_TOKENS or (tok and set(tok) <= set(";&|()")):
            if seg:
                yield seg
            seg = []
        else:
            seg.append(tok)
    if seg:
        yield seg


ENV_ASSIGN_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.S)


def take_env(seg, env):
    """Strip leading env assignments (bash VAR=x, export, env, $env:VAR = x).

    Returns (remaining tokens, inline env that applies to this segment only).
    Persistent assignments (export, $env:) go into `env` for later segments.
    """
    inline = {}
    i = 0
    if seg and seg[0].lower().startswith("$env:"):
        tok = seg[0][5:]
        if "=" in tok:
            name, value = tok.split("=", 1)
        elif len(seg) >= 3 and seg[1] == "=":
            name, value = tok, seg[2]
        elif len(seg) >= 2 and seg[1].startswith("="):
            name, value = tok, seg[1][1:]
        else:
            return seg, inline
        env[name] = value
        return [], inline
    persistent = False
    if seg and seg[0] in ("export", "env"):
        persistent = seg[0] == "export"
        i = 1
    while i < len(seg):
        m = ENV_ASSIGN_RE.match(seg[i])
        if not m:
            break
        (env if persistent else inline)[m.group(1)] = m.group(2)
        i += 1
    return seg[i:], inline


def is_python(tok):
    return bool(PYTHON_RE.match(os.path.basename(tok)))


def settings_opt(args):
    for j, a in enumerate(args):
        if a.startswith("--settings="):
            return a.split("=", 1)[1]
        if a == "--settings" and j + 1 < len(args):
            return args[j + 1]
    return None


def first_positional(args):
    skip = False
    for a in args:
        if skip:
            skip = False
            continue
        if a in ("--settings", "--pythonpath", "--database", "-v", "--verbosity"):
            skip = True
            continue
        if a.startswith("-"):
            continue
        return a
    return None


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def default_settings(root, source_text=None):
    text = source_text if source_text is not None else read_text(os.path.join(root, "manage.py"))
    m = SETTINGS_DEFAULT_RE.search(text)
    return m.group(1) if m else "hoteldatahub.settings"


def mysql_target(args):
    host, db, skip = None, None, False
    for j, a in enumerate(args):
        if skip:
            skip = False
            continue
        if a in ("-h", "--host"):
            host = args[j + 1] if j + 1 < len(args) else ""
            skip = True
        elif a.startswith("--host="):
            host = a.split("=", 1)[1]
        elif a.startswith("-h") and len(a) > 2:
            host = a[2:]
        elif a in ("-u", "-P", "-p", "--user", "--port", "-e", "--execute", "-D", "--database"):
            if a in ("-D", "--database") and j + 1 < len(args):
                db = args[j + 1]
            skip = a != "-p"
        elif a.startswith("--database="):
            db = a.split("=", 1)[1]
        elif not a.startswith("-") and db is None:
            db = a
    return host, db


def analyse(command, cwd, powershell):
    """Yield risky actions: dicts with kind 'django' or 'mysql'."""
    env = {}
    cur = cwd
    for seg in segments(tokenize(command, powershell)):
        seg, inline = take_env(seg, env)
        if not seg:
            continue
        head = seg[0].lower()
        if head in ("cd", "set-location", "pushd", "sl", "chdir") and len(seg) > 1:
            args = [a for a in seg[1:] if not a.startswith("-")]
            if args:
                cur = resolve_dir(cur, args[0])
            continue
        merged = dict(env, **inline)
        if head == "&" and len(seg) > 1:
            seg = seg[1:]
        # mysql client (direct, or via docker exec)
        for j, tok in enumerate(seg):
            base = os.path.basename(tok).lower().replace(".exe", "")
            if base in MYSQL_CLIENTS:
                host, db = mysql_target(seg[j + 1:])
                if host is not None and host.lower() not in LOCAL_HOSTS:
                    yield {"kind": "mysql", "host": host, "name": db or "?", "what": base}
                break
        # git -C <path> etc. are irrelevant; look for Django entry points
        manage_idx = next((j for j, t in enumerate(seg) if os.path.basename(t) == "manage.py"), None)
        if manage_idx is not None:
            args = seg[manage_idx + 1:]
            sub = first_positional(args)
            if sub is None or "-h" in args or "--help" in args or sub in SAFE_MANAGE_CMDS:
                continue
            if sub == "makemigrations" and "--merge" not in args:
                continue
            root = find_root(resolve_dir(cur, seg[manage_idx]))
            if not root:
                continue
            yield {"kind": "django", "root": root, "what": "manage.py " + sub,
                   "settings": settings_opt(args) or merged.get("DJANGO_SETTINGS_MODULE"),
                   "default": default_settings(root), "env": merged}
            continue
        # python -m django <cmd> / django-admin <cmd>
        dj_idx = None
        for j, t in enumerate(seg):
            if os.path.basename(t).lower().replace(".exe", "") in ("django-admin", "django-admin.py"):
                dj_idx = j
            elif t == "-m" and j + 1 < len(seg) and seg[j + 1] == "django" and j > 0 and is_python(seg[j - 1]):
                dj_idx = j + 1
            if dj_idx is not None:
                break
        if dj_idx is not None:
            args = seg[dj_idx + 1:]
            sub = first_positional(args)
            root = find_root(cur)
            if root and sub and sub not in SAFE_MANAGE_CMDS and "--help" not in args:
                yield {"kind": "django", "root": root, "what": "django-admin " + sub,
                       "settings": settings_opt(args) or merged.get("DJANGO_SETTINGS_MODULE"),
                       "default": default_settings(root), "env": merged}
            continue
        # python <script.py> / python -c "<code>" that bootstraps Django
        py_idx = next((j for j, t in enumerate(seg) if is_python(t)), None)
        if py_idx is None:
            continue
        rest = seg[py_idx + 1:]
        source, label = None, None
        if "-c" in rest:
            k = rest.index("-c")
            source = rest[k + 1] if k + 1 < len(rest) else ""
            label = "python -c"
        else:
            script = next((a for a in rest if a.lower().endswith(".py")), None)
            if script:
                path = resolve_dir(cur, script)
                source, label = read_text(path), "python " + os.path.basename(path)
                root = find_root(path)
        if not source or not ("django.setup" in source or "DJANGO_SETTINGS_MODULE" in source):
            continue
        root = find_root(cur) if label == "python -c" else root
        if not root:
            continue
        yield {"kind": "django", "root": root, "what": label,
               "settings": merged.get("DJANGO_SETTINGS_MODULE"),
               "default": default_settings(root, source) if SETTINGS_DEFAULT_RE.search(source)
               else default_settings(root), "env": merged}


# ---------------------------------------------------------------- resolution

def interpreter(root):
    for base in (root, CANONICAL_ROOT):
        exe = os.path.join(base, ".venv", "Scripts", "python.exe")
        if os.path.isfile(exe):
            return exe
    return sys.executable


def fingerprint(root, module):
    files = [os.path.join(root, ".env"), os.path.join(root, "manage.py")]
    pkg_dir = os.path.join(root, *module.split(".")[:-1]) if "." in module else root
    try:
        files += [os.path.join(pkg_dir, f) for f in sorted(os.listdir(pkg_dir))
                  if f.startswith("settings") and f.endswith(".py")]
    except OSError:
        pass
    files.append(os.path.join(root, *module.split(".")) + ".py")
    stamps = []
    for f in files:
        try:
            st = os.stat(f)
            stamps.append([f, st.st_mtime_ns, st.st_size])
        except OSError:
            stamps.append([f, None, None])
    return stamps


def resolve_db(root, module, overrides):
    """Return (result dict, cached flag). Result has ok/engine/host/name or error."""
    exe = interpreter(root)
    relevant_env = {k: v for k, v in os.environ.items()
                    if re.match(r"^(DB_|DATABASE|MYSQL|DJANGO)", k)}
    key_src = json.dumps([root.lower(), module, exe.lower(), sorted(overrides.items()),
                          sorted(relevant_env.items())])
    key = hashlib.sha256(key_src.encode()).hexdigest()[:32]
    stamps = fingerprint(root, module)
    cache_file = os.path.join(CACHE_DIR, key + ".json")
    try:
        with open(cache_file, encoding="utf-8") as fh:
            cached = json.load(fh)
        if cached.get("stamps") == stamps:
            return cached["result"], True
    except (OSError, ValueError):
        pass

    env = dict(os.environ)
    env.update(overrides)
    env["DJANGO_SETTINGS_MODULE"] = module
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["SENTRY_DSN"] = ""
    env.pop("PYTHONSTARTUP", None)
    try:
        proc = subprocess.run([exe, "-c", RESOLVER, root, module], cwd=root, env=env,
                              capture_output=True, text=True, timeout=RESOLVE_TIMEOUT,
                              stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "settings import timed out after %ss" % RESOLVE_TIMEOUT}, False
    except OSError as exc:
        return {"ok": False, "error": "cannot start %s: %s" % (exe, type(exc).__name__)}, False
    line = next((l for l in proc.stdout.splitlines() if l.startswith("HDHGUARD::")), None)
    if not line:
        return {"ok": False, "error": "resolver exited %s without a result" % proc.returncode}, False
    result = json.loads(line[len("HDHGUARD::"):])
    if result.get("ok"):
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as fh:
                json.dump({"stamps": stamps, "result": result}, fh)
        except OSError:
            pass
    return result, False


def is_local(result):
    if "sqlite" in result.get("engine", "").lower():
        return True
    return result.get("host", "").strip().lower() in LOCAL_HOSTS


# ---------------------------------------------------------------- main

def emit(decision, reason, codex):
    if codex and decision == "ask":
        decision = "deny"
        reason += (" Codex hooks cannot ask, so this is blocked: stop and ask Jorge to run it"
                   " himself or to point the DB at local.")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))


def main():
    codex = "--codex" in sys.argv[1:]
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except ValueError:
        return 0
    tool = str(data.get("tool_name", "")).lower()
    if tool not in SHELL_TOOLS:
        return 0
    tool_input = data.get("tool_input") or {}
    command = tool_input.get("command", "")
    if isinstance(command, list):
        command = " ".join(str(c) for c in command)
    command = str(command)
    cwd = to_win(str(tool_input.get("workdir") or data.get("cwd") or os.getcwd()))
    if find_root(cwd) is None and "hoteldatahub" not in command.lower():
        return 0

    try:
        problems = []
        seen = {}
        for action in analyse(command, cwd, tool == "powershell"):
            if action["kind"] == "mysql":
                problems.append("%s targets %s/%s, not local" % (action["what"], action["host"], action["name"]))
                continue
            module = action["settings"] or os.environ.get("DJANGO_SETTINGS_MODULE") or action["default"]
            key = (action["root"], module, tuple(sorted(action["env"].items())))
            if key not in seen:
                seen[key] = resolve_db(action["root"], module, action["env"])[0]
            res = seen[key]
            if not res.get("ok"):
                problems.append("%s: could not resolve the DB target from %s (%s)"
                                % (action["what"], module, res.get("error")))
            elif not is_local(res):
                problems.append("%s: hoteldatahub DB target is %s/%s (settings %s), not local"
                                % (action["what"], res.get("host"), res.get("name"), module))
    except Exception as exc:  # a guard bug must fail closed, not open
        problems = ["hdh_db_guard error: %s: %s" % (type(exc).__name__, str(exc)[:160])]

    if problems:
        emit("ask", "; ".join(problems) + ". Jorge must approve writes to this database.", codex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
