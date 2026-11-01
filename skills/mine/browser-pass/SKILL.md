---
name: browser-pass
description: Walk a checklist of browser checks against a web app (local dev server, staging, or deployed) in Playwright's bundled Chromium, judge each from screenshots and browser errors, and file each failure. Use when the user asks to test, QA or review a web app's behaviour in the browser, or to run a pass, test-plan or acceptance issue.
---

Run a **pass**: a checklist of browser checks against one web app. The checklist comes from what the user names: a GitHub issue or PR whose body holds `- [ ]` boxes, a spec or test-plan file, or checks typed in chat. The pass is done when every box is ticked, tied to a failure, or listed for the user in the report.

`browser.py` sits next to this file (call that folder `<skill-dir>`). It drives Playwright's bundled Chromium with an optional stored browser session, and after each run prints the console errors, page errors, failed requests and 4xx/5xx responses it saw. `uv run <skill-dir>/browser.py --help` lists the commands. Run commands from the project root in Git Bash.

## Steps

1. **Read the checklist.** For an issue or PR, `gh issue view <N>` or `gh pr view <N>`; for a file, read it; for chat, number the checks yourself. Collect the unticked boxes in order, and what each one needs: a signed-in user, seeded data, a viewport, a state only reachable after another box. Done when you hold that list.

2. **Pick the target.** A URL the user named wins. Otherwise use the project's own way to run the app, in this order: a project skill or `AGENTS.md`/`CLAUDE.md` section on running it, `.claude/launch.json`, the dev script in `package.json` / `pyproject.toml` / `Makefile`, the README. Start a dev server in the background, note its PID, and wait until its URL answers. Deploy only when the user asks or the project's docs say passes run on a deployed environment, and then with the project's own deploy command. Done when the target URL answers.

3. **Open the browser session.** On the first run of the session, `uv run <skill-dir>/browser.py install` fetches Chromium if it is missing. A public app needs no session. For an app behind a sign-in, run a first check script that loads `/` and calls `need_sign_in()` when it lands on the sign-in screen. Exit code 3 means a sign-in is needed:

   ```sh
   uv run <skill-dir>/browser.py login <url> [--wait-for-url "**/dashboard"]
   ```

   It opens a Chromium window. Ask the user to sign in there, once; it stores the session when the page reaches the glob, or when the user closes the tab. On a local dev host, a check script may instead sign in with test credentials from the project's seed, fixture or example-config files. Done when a check script exits 0 signed in.

4. **Walk the checklist.** Take the boxes in order. For each, write a check script in the scratchpad and run it:

   ```sh
   uv run <skill-dir>/browser.py run <url> <script.py> [--viewport 390x844] [--headed] [--fresh]
   ```

   The script starts with `page`, `context`, `shots` (a screenshot folder) and `need_sign_in` bound, and relative URLs resolve against `<url>`. It drives the page with Playwright's sync API (`page.goto("/settings")`, `page.get_by_role(...)`, `expect(...)` from `playwright.sync_api`), saves screenshots under `shots`, and prints what it found. Read every screenshot and the error summary before you judge. `--fresh` runs signed out, `--viewport` checks a phone or tablet width, `--headed` only to watch a step.

   Judge each box against its own words. Tick it when everything it names happened, with no browser error it would care about. File it (step 5) when any part did not. A box you cannot judge alone, such as a design call or a wait longer than the session, stays unticked and goes in the report. Done when every box has one of those three outcomes.

5. **File each failure.** One failure, one record. The record says what you did, what the box expected, and what happened instead (the error text, the failing request, what the screenshot shows), the target URL and the revision under test (`git rev-parse --short HEAD` for a local server).

   - **Checklist from a GitHub issue or PR:** search first with `gh issue list --state open --search "<words>"`; an open issue for the same failure gets a comment instead of a twin. Otherwise `gh issue create --title "<what is wrong, as a statement>" --body-file <file>`, with the repo's triage label when `gh label list` has one, ending with `Found in the browser pass #N.` Then link it from its box: write the body to a file with `gh issue view <N> --json body -q .body`, turn `- [ ] <box>` into `- [ ] <box> (fails: #<new>)` and a passing box into `- [x] <box>`, and save it with `gh issue edit <N> --body-file <file>` (`gh pr edit` for a PR).
   - **Any other checklist:** keep the records for the report; file them only on the user's yes.

   Done when every failure has its record, and on GitHub its issue and its box link.

6. **Clean up.** `uv run <skill-dir>/browser.py cleanup` ends any Chromium a killed run left behind. Stop the dev server you started, by its PID. Data the pass created stays, and the report lists it. Done when cleanup has run and nothing you started is still running.

7. **Report.** Per checklist: the boxes ticked, the failures (issue links or the records themselves), the boxes left for the user, and the data the pass created. The checklist issue stays open for the user to sign off.

## Browser

All browser checks run in Playwright's bundled Chromium through `browser.py`. The user's own Chrome, its profile and the Claude in Chrome extension stay out of it.

`browser.py` records every process it starts in `~/.browser-pass/pids.json` and ends them by PID when a run ends, however it ends. To end a browser yourself, run `browser.py cleanup`, or stop a PID your own command started. Never end a process by name (`taskkill /IM chrome.exe`, `Stop-Process -Name chrome`, `pkill chrome`): the bundled Chromium is also `chrome.exe`, so that closes the user's Chrome too.

Sessions live in `~/.browser-pass/sessions/<host_port>.json`, outside every repository. They hold session cookies, so they are never printed, committed or pasted.

## Secrets

Real secret values (API keys, tokens, anyone's real password) reach the app the way the project already loads them (its `.env`, its seed command, its admin CLI), never typed into a page by a check script. When a check needs a secret the project does not have, ask the user to add it to the right `.env` or secret store; the variable names are in the repo's `.env.example`.
