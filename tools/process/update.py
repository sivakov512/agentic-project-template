#!/usr/bin/env python3
"""The process update (docs/process/updates.md, "Getting a newer process"): when the template has a newer
release, brings its files in on a branch made from main as it is on GitHub, and opens a pull request.
The coordinator runs it with a clean working tree, git and gh signed in as the agents' account; it leaves
the checkout on the update's branch. Standard library, git and gh only.

    python3 tools/process/update.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import owned  # noqa: E402

ROOT = HERE.parents[1]

BODY = """\
## Backlog item

Process update: {old} to {new}, from {template}.

## What changed

The template's files at release {tag}, and the lock. The changelog entries since {old}:

{changelog}

## Behaviour change

None: only the process files change; the product is not touched.

## Why

The process lives in the template; projects take its releases (docs/process/updates.md).

## How it was checked

Opened by tools/process/update.py; the checks of this pull request are the evidence.

## Docs updated

The template's files only. The coordinator adds here what the changelog asks of the project, if
anything.

## Owner review

Only what the changelog entries above ask of this project (their "Projects:" lines), which the
coordinator does in this pull request; the owner reviewed each change in the template already.

## Not done and open questions

What the changelog asks of the project, if anything, is the coordinator's to do in this pull request.
"""


class Failed(Exception):
    pass


def run(*args, cwd=ROOT):
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if done.returncode != 0:
        command = " ".join(args[:3])
        raise Failed(f"{command}: {done.stderr.strip() or done.stdout.strip()}")
    return done.stdout.strip()


def gh_json(*args):
    return json.loads(run("gh", *args))


def main():
    repo = run("gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    if run("git", "status", "--porcelain"):
        raise Failed("the working tree has changes: commit or stash them first")
    run("git", "fetch", "--quiet", "origin", "main")
    try:
        lock = json.loads(run("git", "show", f"origin/main:{owned.LOCK}"))
    except (Failed, ValueError):
        print(f"main has no readable {owned.LOCK}: nothing to update from")
        return 1
    template = lock["template"]
    if repo == template:
        print("This is the template itself: nothing to update")
        return 0

    try:
        tag = gh_json("api", f"repos/{template}/releases/latest")["tag_name"]
    except Failed:
        print(f"No release of {template} can be read yet: nothing to update")
        return 0
    new = tag.lstrip("v")
    old = lock["version"]
    if owned.version_tuple(new) <= owned.version_tuple(old):
        print(f"The process is the newest: {old}")
        return 0

    branch = f"process-update-{new}"
    open_updates = [pull for pull in gh_json("api", f"repos/{repo}/pulls?state=open&per_page=100")
                    if pull["head"]["ref"].startswith("process-update-")]
    if open_updates:
        print(f"A process update is already open: {open_updates[0]['html_url']}. Merge or close it first")
        return 0

    # The update starts from main as it is on GitHub, whatever was checked out.
    run("git", "checkout", "--quiet", "-B", branch, "origin/main")
    with tempfile.TemporaryDirectory() as folder:
        checkout = Path(folder) / "template"
        run("git", "clone", "--quiet", "--depth", "1", "--branch", tag, f"https://github.com/{template}.git",
            str(checkout))
        released = owned.read_lock(checkout) or {}
        if released.get("version") != new:
            raise Failed(f"release {tag} of {template} carries a lock for version {released.get('version')}")
        synced = run(sys.executable, str(checkout / "tools/process/sync.py"), str(checkout), str(ROOT))
    # The entries' headings one level down, so they don't read as sections of the description.
    changelog = (synced.split("\n", 1)[1] if "\n" in synced else "").replace("\n## ", "\n### ")
    if changelog.startswith("## "):
        changelog = "#" + changelog

    run("git", "add", "-A")
    run("git", "commit", "--quiet", "-m", f"chore: update the process to {new}")
    # The branch is this script's own: one left from a run that couldn't open its pull request is replaced.
    run("git", "push", "--quiet", "--force", "origin", branch)

    body = BODY.format(old=old, new=new, template=template, tag=tag, changelog=changelog or "(none)")
    pull = gh_json("api", f"repos/{repo}/pulls", "-f", f"title=Plan: update the process to {new}",
                   "-f", f"head={branch}", "-f", "base=main", "-f", f"body={body}")
    run("gh", "api", f"repos/{repo}/issues/{pull['number']}/labels",
        "-f", "labels[]=plan", "-f", "labels[]=owner-review")
    print(f"Opened {pull['html_url']}. The checkout is on {branch}: do there what the changelog asks.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Failed, ValueError, KeyError, OSError) as error:
        print(f"Process update failed: {error!r}" if isinstance(error, KeyError) else f"Process update failed: {error}")
        sys.exit(1)
