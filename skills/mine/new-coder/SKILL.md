---
name: new-coder
description: Create a software factory (kinby package `coder`) on the playground hub for a GitHub repository, behaving like the kinby coder. Takes the repository URL.
disable-model-invocation: true
---

# New coder

Create one more instance of package `coder` on the hub at `kinby.jorgesolerrr.dev` (SSH host `playground`, hub container `kinby-hub-1`, hub directory `/hub` inside it). It works issues labeled `ready-for-agent` in the given repository and behaves like the kinby coder at `/hub/coder`: same secrets, commit identity and factory settings. Only the repository, its check commands and its webhook differ. The model is the `MODEL` constant in `create_coder.py`.

[`create_coder.py`](create_coder.py) does the hub side inside the hub container. It copies `GH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY` (sent as the built-in `api_key` field), `GIT_USER_NAME` and `GIT_USER_EMAIL` from `/hub/coder/.env` and generates a fresh webhook secret, so no secret passes through this machine or your output. It prepares the image, creates the instance, writes the checks, starts the instance and adds the webhook.

## Steps

Run every command below in the Bash tool: they rely on POSIX quoting and redirection.

1. **Resolve the repository.** Take the URL as `https://github.com/<owner>/<repository>`. Run `gh repo view <owner>/<repository>`. The coder's token must reach it too: `ssh playground 'docker exec kinby-hub-1 sh -c ". /hub/coder/.env; curl -s -o /dev/null -w %{http_code} -H \"Authorization: Bearer \$GH_TOKEN\" https://api.github.com/repos/<owner>/<repository>"'` prints `200`. Done when both succeed.

2. **Choose the checks.** Find the commands the repository's own gate runs before a merge: its `AGENTS.md`/`CLAUDE.md`, CI workflows, `package.json` scripts, `pyproject.toml`, `Makefile`. List them in order, the way the kinby coder has `bun install --frozen-lockfile` then `bun run check`. A repository with no code yet gets an empty list. Note whether it has `.claude/skills`; if so, the instance loads them (`--workspace-skills`), as the kinby coder does. Done when every check is traced to the file that runs it in CI or the docs.

3. **Confirm.** Show the user the instance name (default `<repository in lower case>-coder`, which must not already exist: `ssh playground 'docker exec kinby-hub-1 sh -c "grep -h ^id /hub/instances/*/kinby.toml"'`), the check list, and whether workspace skills load. Proceed on their answer.

4. **Labels.** Make sure the repository has `ready-for-agent`, `ready-for-human` and `merge-ready`. Create each missing one with `gh label create <name> -R <owner>/<repository>` (`merge-ready` with `--color 0E8A16`).

5. **Run the script.** Preparing the image can take several minutes; give the command a 10-minute timeout. The working directory resets between calls, so feed the script by its absolute path:

   ```sh
   ssh playground "docker exec -i kinby-hub-1 python - https://github.com/<owner>/<repository> <name> kinby.jorgesolerrr.dev --check '<command 1>' --check '<command 2>' --workspace-skills" < <skill-dir>/create_coder.py
   ```

   Pass one `--check` per command from step 2, in order (none for an empty list), and `--workspace-skills` only when the repository has `.claude/skills`. Inside the double quotes, write each `$` in a command as `\$`.

   It prints each hub step and ends with `DONE <instance-id>`. On `FAILED`, the message says what the hub holds by then. A failure after `instance:` leaves a created instance: fix the cause, then remove that instance from the web app before running again, or finish the remaining steps by hand.

6. **Verify.** `ssh playground 'docker ps --filter name=<instance-id>'` shows it healthy, and the webhook's ping delivery succeeded: `gh api repos/<owner>/<repository>/hooks --jq '.[] | [.config.url, .last_response.code] | @tsv'` shows the new URL with `200`. A `null` code right after creation means the ping is not delivered yet: check again after a few seconds. Done when both hold.

7. **Report** the instance ID, name, checks and webhook URL. Say that babysitting is off, as on the kinby coder, so there is no babysit webhook and the Codex sign-in stays pending in the web app until babysitting is wanted.
