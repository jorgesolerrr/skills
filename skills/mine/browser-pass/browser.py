# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright==1.63.0", "psutil==7.2.2"]
# ///
"""Drive Playwright's bundled Chromium against any web app, with an optional stored browser session.

    uv run browser.py install                                   download the bundled Chromium once
    uv run browser.py login <url> [--wait-for-url GLOB]         sign in by hand, store the session
    uv run browser.py run <url> <script.py> [options]           run one check script
    uv run browser.py cleanup                                   end what a killed run left behind

<url> is the app's base URL. A bare host gets https://, and localhost or 127.0.0.1 gets http://.

A check script runs with these names already bound:
    page, context    a Playwright Page and BrowserContext; relative URLs resolve against <url>
    shots            a Path to save screenshots in (--shots, default: the script's folder)
    need_sign_in()   call it when the page shows the app's sign-in screen: the stored session
                     is deleted and the run exits 3

After the script, the run prints the console errors, page errors, failed requests and HTTP
responses of 400 or more that it saw. Exit code 3 means a sign-in is needed.

Browser sessions live in ~/.browser-pass/sessions/<host_port>.json, outside every repository.
Every process this helper starts is recorded in ~/.browser-pass/pids.json and ended by PID.
"""

from __future__ import annotations

import argparse
import json
import re
import runpy
import subprocess
import sys
from collections.abc import Iterable, Iterator
from contextlib import contextmanager, suppress
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit

import psutil
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

STATE = Path.home() / ".browser-pass"
PIDS = STATE / "pids.json"
SESSIONS = STATE / "sessions"
SIGN_IN_NEEDED = 3
SIGN_IN_MS = 600_000
LOCAL_HOSTS = {"localhost", "127.0.0.1", "[::1]"}


class SignInNeeded(Exception):
    """Raised by a check script through need_sign_in()."""


@dataclass(frozen=True)
class Started:
    """A process this helper started. The creation time tells it from a later one on its PID."""

    pid: int
    created: float


def _recorded() -> list[Started]:
    if not PIDS.is_file():
        return []
    return [Started(**entry) for entry in json.loads(PIDS.read_text("utf-8"))]


def _write(started: list[Started]) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    PIDS.write_text(json.dumps([asdict(entry) for entry in started]), "utf-8")


def _record(processes: Iterable[psutil.Process]) -> list[Started]:
    started = [Started(process.pid, process.create_time()) for process in processes]
    _write(_recorded() + started)
    return started


def _playwright_owned(process: psutil.Process) -> bool:
    """Playwright's driver and bundled browsers live in their own folders, never Chrome's."""
    parts = Path(process.exe()).parts
    return "ms-playwright" in parts or "playwright" in parts


def _end(started: list[Started]) -> None:
    """Kill each recorded process still alive, with its children, by PID and nothing else."""
    killed: list[psutil.Process] = []
    for entry in started:
        try:
            process = psutil.Process(entry.pid)
            if process.create_time() != entry.created:
                continue
            tree = [*process.children(recursive=True), process]
        except psutil.NoSuchProcess:
            continue
        for member in tree:
            with suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                if _playwright_owned(member):
                    member.kill()
                    killed.append(member)
    psutil.wait_procs(killed, timeout=10)
    _write([entry for entry in _recorded() if entry not in started])


@contextmanager
def _chromium(*, headed: bool) -> Iterator[Browser]:
    """Launch bundled Chromium and end every process the launch started, however the run ends."""
    started: list[Started] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not headed)
            # Everything under this process is ours: the Playwright driver and its Chromium.
            started = _record(psutil.Process().children(recursive=True))
            try:
                yield browser
            finally:
                browser.close()
    finally:
        _end(started)


def base_url(target: str) -> str:
    """The app's origin with a scheme: https for a bare host, http for a local one."""
    if "://" not in target:
        host = target.split("/")[0].split(":")[0]
        scheme = "http" if host in LOCAL_HOSTS or host.endswith(".localhost") else "https"
        target = f"{scheme}://{target}"
    return target.rstrip("/")


def _session_file(url: str) -> Path:
    parts = urlsplit(url)
    key = re.sub(r"[^A-Za-z0-9.-]", "_", parts.netloc)
    return SESSIONS / f"{key}.json"


def install() -> int:
    """Download the Chromium build this Playwright version drives."""
    return subprocess.call([sys.executable, "-m", "playwright", "install", "chromium"])


def login(target: str, *, path: str, wait_for_url: str | None) -> int:
    """Open a window for a sign-in by hand, then store the browser session for later runs."""
    url = base_url(target)
    with _chromium(headed=True) as browser:
        context = browser.new_context(base_url=url)
        page = context.new_page()
        page.goto(path)
        try:
            if wait_for_url:
                print(f"Sign in in the Chromium window. Waiting up to ten minutes for {wait_for_url}.")
                page.wait_for_url(wait_for_url, timeout=SIGN_IN_MS)
            else:
                print("Sign in in the Chromium window, then close the tab. Waiting up to ten minutes.")
                page.wait_for_event("close", timeout=SIGN_IN_MS)
        except Exception:
            print("No sign-in arrived.", file=sys.stderr)
            return SIGN_IN_NEEDED
        SESSIONS.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=_session_file(url))
    print(f"Stored the browser session for {urlsplit(url).netloc}.")
    return 0


def _watch(page: Page, origin: str, seen: list[str]) -> None:
    """Note what a reviewer would look for in devtools: errors and failing requests."""
    page.on(
        "console",
        lambda message: message.type == "error" and seen.append(f"console: {message.text}"),
    )
    page.on("pageerror", lambda error: seen.append(f"page error: {error}"))
    page.on(
        "requestfailed",
        lambda request: seen.append(f"request failed: {request.method} {request.url} ({request.failure})"),
    )
    page.on(
        "response",
        lambda response: response.status >= 400
        and response.url.startswith(origin)
        and seen.append(f"HTTP {response.status}: {response.request.method} {response.url}"),
    )


def run(
    target: str,
    script: Path,
    *,
    headed: bool,
    fresh: bool,
    viewport: str,
    shots: Path | None,
) -> int:
    """Run one check script against the app, with the stored browser session when there is one."""
    url = base_url(target)
    session = _session_file(url)
    width, height = (int(n) for n in viewport.lower().split("x"))
    shots = (shots or script.resolve().parent)
    shots.mkdir(parents=True, exist_ok=True)
    seen: list[str] = []

    def need_sign_in() -> None:
        raise SignInNeeded

    with _chromium(headed=headed) as browser:
        context: BrowserContext = browser.new_context(
            base_url=url,
            storage_state=session if session.is_file() and not fresh else None,
            viewport={"width": width, "height": height},
        )
        context.on("page", lambda page: _watch(page, url, seen))
        page = context.new_page()
        try:
            runpy.run_path(
                str(script),
                init_globals={
                    "page": page,
                    "context": context,
                    "shots": shots,
                    "need_sign_in": need_sign_in,
                },
            )
        except SignInNeeded:
            session.unlink(missing_ok=True)
            print(f"{urlsplit(url).netloc} needs a sign-in. Run login.", file=sys.stderr)
            return SIGN_IN_NEEDED
        finally:
            if seen:
                print(f"--- {len(seen)} browser errors and failing requests ---")
                print("\n".join(seen))
            else:
                print("--- no browser errors or failing requests ---")
    return 0


def cleanup() -> int:
    """End the processes a killed run recorded and could not end itself."""
    started = _recorded()
    _end(started)
    print(f"Checked {len(started)} recorded processes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="browser.py", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("install", help="download the bundled Chromium")
    login_parser = commands.add_parser("login", help="sign in by hand and store the session")
    login_parser.add_argument("url")
    login_parser.add_argument("--path", default="/", help="page to open first (default: /)")
    login_parser.add_argument(
        "--wait-for-url", help="glob the page reaches once signed in; default: wait for the tab to close"
    )
    run_parser = commands.add_parser("run", help="run a check script with `page` bound")
    run_parser.add_argument("url")
    run_parser.add_argument("script", type=Path)
    run_parser.add_argument("--headed", action="store_true", help="show the window")
    run_parser.add_argument("--fresh", action="store_true", help="ignore the stored session")
    run_parser.add_argument("--viewport", default="1440x900", help="WIDTHxHEIGHT (default 1440x900)")
    run_parser.add_argument("--shots", type=Path, help="screenshot folder (default: the script's)")
    commands.add_parser("cleanup", help="end processes a killed run left behind")
    args = parser.parse_args()
    match args.command:
        case "install":
            return install()
        case "login":
            return login(args.url, path=args.path, wait_for_url=args.wait_for_url)
        case "run":
            return run(
                args.url,
                args.script,
                headed=args.headed,
                fresh=args.fresh,
                viewport=args.viewport,
                shots=args.shots,
            )
        case _:
            return cleanup()


if __name__ == "__main__":
    sys.exit(main())
