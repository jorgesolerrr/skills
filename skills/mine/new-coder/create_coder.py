"""Create a software factory instance for one repository on this hub, then start it.

Runs inside the hub container, fed on stdin:

    python - <repository-url> <name> <domain> [--check COMMAND]... [--workspace-skills]

It copies the kinby coder's secrets and commit identity, so no secret leaves the box.
"""

import argparse
import asyncio
import json
import re
import secrets
import sys
import urllib.request
from pathlib import Path

import yaml
from kinby.cli.client import format_error
from kinby.cli.contract_socket import contract_client
from kinby.cli.hub_update import follow_operation
from kinby.contracts import (
    IMAGE_PREPARE,
    INSTANCE_CREATE,
    INSTANCE_START,
    PACKAGE_LIST,
    AccessToken,
    ErrorEnvelope,
    ImagePrepareCommand,
    InstanceCreateCommand,
    InstanceStartCommand,
    OperationGetCommand,
    PackageListCommand,
)
from pydantic import SecretStr

HUB = Path("/hub")
CONTRACT_URL = "ws://127.0.0.1:8080/ws"
MODEL = "anthropic:claude-sonnet-5"
#: The coder's .env values the new instance reuses.
SHARED_SECRETS = ("GH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN")
WORKSPACE_SKILLS = 'skills = [".claude/skills"]'


class Failed(Exception):
    """A step failed; the message says which, and what the hub holds by then."""


def main() -> int:
    parser = argparse.ArgumentParser(prog="create_coder")
    parser.add_argument("repository", help="https://github.com/<owner>/<repository>")
    parser.add_argument("name", help="the instance's manifest id and persona name")
    parser.add_argument("domain", help="the hub's public domain, for the webhook URL")
    parser.add_argument("--check", action="append", default=[], help="a check command, in order")
    parser.add_argument("--workspace-skills", action="store_true")
    args = parser.parse_args()
    match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?", args.repository)
    if match is None:
        parser.error("the repository must be https://github.com/<owner>/<repository>")
    try:
        asyncio.run(create(args, owner=match[1], repo=match[2]))
    except Failed as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


async def create(args: argparse.Namespace, *, owner: str, repo: str) -> None:
    coder = read_env(HUB / "coder" / ".env")
    webhook_secret = secrets.token_hex(32)
    token = AccessToken((HUB / "access-token").read_text(encoding="utf-8").strip())
    async with contract_client(CONTRACT_URL, token) as client:
        listed = checked(await client.call(PACKAGE_LIST, PackageListCommand()))
        selection = next(p.selection for p in listed.packages if p.id == "coder")

        print("== preparing the image", flush=True)
        prepared = checked(
            await client.call(IMAGE_PREPARE, ImagePrepareCommand(package=selection))
        )
        await followed(client, prepared.operation_id, "image preparation")

        print("== creating the instance", flush=True)
        command = InstanceCreateCommand(
            manifest_id=args.name,
            persona_name=args.name,
            model=MODEL,
            package=selection,
            config={
                "repository": f"https://github.com/{owner}/{repo}.git",
                "commit_name": coder["GIT_USER_NAME"],
                "commit_email": coder["GIT_USER_EMAIL"],
            },
            secrets={
                **{name: SecretStr(coder[name]) for name in SHARED_SECRETS},
                # The built-in API key field; the hub files it under ANTHROPIC_API_KEY.
                "api_key": SecretStr(coder["ANTHROPIC_API_KEY"]),
                "GITHUB_WEBHOOK_SECRET": SecretStr(webhook_secret),
            },
        )
        created = checked(await client.call(INSTANCE_CREATE, command))
        instance_id = created.instance_id
        await followed(client, created.operation_id, "creation")
        print(f"instance: {instance_id}", flush=True)

        directory = HUB / "instances" / str(instance_id)
        set_checks(directory / "package.yaml", args.check)
        if args.workspace_skills:
            add_workspace_skills(directory / "kinby.toml")
        print("== configured checks and conventions", flush=True)

        print("== starting", flush=True)
        started = checked(
            await client.call(INSTANCE_START, InstanceStartCommand(instance_id=instance_id))
        )
        await followed(client, started.operation_id, f"start of {instance_id}")

        # After the start, so GitHub's first ping reaches a running instance.
        hook_url = f"https://{args.domain}/instances/{instance_id}/signals/implement-ready-issue"
        add_webhook(owner, repo, hook_url, webhook_secret, coder["GH_TOKEN"], instance_id)
        print(f"== webhook: {hook_url}", flush=True)
        print(f"DONE {instance_id}")


def checked[T](answer: T | ErrorEnvelope) -> T:
    if isinstance(answer, ErrorEnvelope):
        fields = "".join(f"\n  {name}: {why}" for name, why in answer.fields.items())
        raise Failed(format_error(answer) + fields)
    return answer


async def followed(client, operation_id, what: str) -> None:
    if await follow_operation(client, OperationGetCommand(operation_id=operation_id)) != 0:
        raise Failed(f"the {what} failed")


def read_env(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        name, sep, value = line.partition("=")
        if sep and not name.lstrip().startswith("#"):
            values[name.strip()] = value.strip().strip("\"'")
    return values


def set_checks(path: Path, commands: list[str]) -> None:
    """The hub wrote package.yaml without comments, so a load and dump loses nothing."""
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    config["checks"]["commands"] = commands
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")


def add_workspace_skills(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if WORKSPACE_SKILLS in text:
        return
    anchor = re.search(r"^instructions = .*$", text, flags=re.MULTILINE)
    if anchor is None:
        raise Failed(f"{path} has no [workspace.conventions] instructions line")
    path.write_text(
        f"{text[: anchor.end()]}\n{WORKSPACE_SKILLS}{text[anchor.end() :]}", encoding="utf-8"
    )


def add_webhook(
    owner: str, repo: str, url: str, secret: str, token: str, instance_id: object
) -> None:
    body = {
        "name": "web",
        "active": True,
        "events": ["issues", "pull_request"],
        "config": {"url": url, "content_type": "json", "secret": secret, "insecure_ssl": "0"},
    }
    request = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo}/hooks",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(request, timeout=30).close()
    except OSError as exc:
        raise Failed(f"adding the webhook failed ({exc}); instance {instance_id} runs") from exc


if __name__ == "__main__":
    sys.exit(main())
