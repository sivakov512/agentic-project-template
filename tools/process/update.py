#!/usr/bin/env python3
"""The process update (docs/process/updates.md, "Getting a newer process"): when the template has a newer
release, brings its files in on a branch made from main as it is on GitHub, and opens a pull request.
The coordinator runs it with a clean working tree, git and gh signed in as the agents' account; it leaves
the checkout on the update's branch. It takes a release only when its tag is on the template's main
(owned.fetch_release), and stops before running anything of it otherwise. Standard library, git and gh
only.

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

{owner_review}

## Not done and open questions

What the changelog asks of the project, if anything, is the coordinator's to do in this pull request.
"""
# The "Owner review" section, as the update goes without the owner or to the owner because of .github/.
NO_REVIEW = """\
None needed while this pull request only brings the template's release, which the owner agreed in the
template, and what the changelog asks of the project changes nothing the owner keeps. If it does (the
plan, the settings), the coordinator labels it owner-review and says here what to look at."""
APPROVE_ONLY = """\
Approve only, no reading needed: the template's files here are exactly the template's release
[{tag}](https://github.com/{template}/releases/tag/{tag}), which the owner approved in the template.
GitHub asks for the owner's review because the release changes files under `.github/`, which
`.github/CODEOWNERS` keeps for the owner. If what the changelog asks of the project changes something
else the owner keeps (the plan, the settings), the coordinator says here what to look at."""


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


def review(own_account, touches_github):
    """The review label and the "Owner review" text (to format with tag and template) of the pull request:
    with the agents' own account an update that changes .github/ needs the owner's Approve, since GitHub
    keeps .github/ for the owner (docs/process/updates.md)."""
    if own_account and touches_github:
        return "owner-review", APPROVE_ONLY
    return "ok-without-reading", NO_REVIEW


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

    with tempfile.TemporaryDirectory() as folder:
        checkout = Path(folder) / "template"
        checkout.mkdir()
        run("git", "init", "--quiet", cwd=checkout)
        try:
            release = owned.fetch_release(checkout, template, new)
        except ValueError as error:
            raise Failed(f"can't fetch release {tag} of {template}: {error}")
        # Nothing of a release off the template's main runs here: the owner never approved it.
        if release is None:
            raise Failed(f"release {tag} of {template} is not on the template's main, so the owner never"
                         " approved it there: not taken. Tell the template's coordinator (docs/process/updates.md)")
        run("git", "checkout", "--quiet", "--detach", release, cwd=checkout)
        released = owned.read_lock(checkout) or {}
        if released.get("version") != new:
            raise Failed(f"release {tag} of {template} carries a lock for version {released.get('version')}")
        # The update starts from main as it is on GitHub, whatever was checked out.
        run("git", "checkout", "--quiet", "-B", branch, "origin/main")
        synced = run(sys.executable, str(checkout / "tools/process/sync.py"), str(checkout), str(ROOT))
    # The entries' headings one level down, so they don't read as sections of the description.
    changelog = (synced.split("\n", 1)[1] if "\n" in synced else "").replace("\n## ", "\n### ")
    if changelog.startswith("## "):
        changelog = "#" + changelog

    run("git", "add", "-A")
    config = json.loads((ROOT / "docs/process.json").read_text(encoding="utf-8"))
    own_account = (config.get("project") or {}).get("agents_account") != "owner"
    touches_github = any(name.startswith(".github/") for name in
                         run("git", "diff", "--cached", "--name-only").splitlines())
    label, owner_review = review(own_account, touches_github)
    run("git", "commit", "--quiet", "-m", f"chore: update the process to {new}")
    # The branch is this script's own: one left from a run that couldn't open its pull request is replaced.
    run("git", "push", "--quiet", "--force", "origin", branch)

    body = BODY.format(old=old, new=new, template=template, tag=tag, changelog=changelog or "(none)",
                       owner_review=owner_review.format(tag=tag, template=template))
    pull = gh_json("api", f"repos/{repo}/pulls", "-f", f"title=Plan: update the process to {new}",
                   "-f", f"head={branch}", "-f", "base=main", "-f", f"body={body}")
    run("gh", "api", f"repos/{repo}/issues/{pull['number']}/labels",
        "-f", "labels[]=plan", "-f", f"labels[]={label}")
    print(f"Opened {pull['html_url']}. The checkout is on {branch}: do there what the changelog asks,"
          " and label it owner-review if that changes what the owner keeps (docs/process/updates.md).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Failed, ValueError, KeyError, OSError) as error:
        print(f"Process update failed: {error!r}" if isinstance(error, KeyError) else f"Process update failed: {error}")
        sys.exit(1)
