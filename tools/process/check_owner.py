#!/usr/bin/env python3
"""Checks that a pull request which needs the owner's OK has it, so the coordinator can merge the rest
on its own (docs/process/workflow.md, "The owner's OK and the merge"). Standard library and git only.

A pull request needs the owner's OK unless it is labelled ok-without-reading, and it always needs it
when it changes what the owner keeps for themself: CLAUDE.md, docs/plan.md, docs/process.json, anything
under .github/, or the template's files and its lock. The template's files and the lock of a process
update are the exception where each is exactly as in the release of the template that main's lock
already names: the owner
agreed that release in the template. With the agents' own account the OK is an approval of the pull
request's last commit by the repository's owner; with the owner's account nobody can approve
their own pull request, so the check only makes sure the label isn't ok-without-reading where it can't be,
and the OK stays the owner's word that the coordinator quotes.

In CI, with GH_TOKEN set to a token that can read the pull request's reviews:
    python3 tools/process/check_owner.py "$GITHUB_EVENT_PATH"
"""

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import owned  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
# Where a template's releases are fetched from; {} is its owner/name from the lock.
TEMPLATE_SOURCE = "https://github.com/{}.git"
KEPT_BY_OWNER = ["CLAUDE.md", "docs/plan.md", "docs/process.json", owned.LOCK]
# Who may give the OK: the repository's owner. Collaborators, the agents' account among them, and on a
# public repository anyone at all can approve too, so their approvals don't count.
OWNER = "OWNER"


def kept_by_owner(name):
    """Whether a changed path is one only the owner's OK lets in."""
    return name in KEPT_BY_OWNER or name.startswith(".github/") or owned.is_owned(name)


def approved_head(reviews, head, author):
    """Whether the repository's owner, if not the author, approved the commit head and hasn't withdrawn
    it since. reviews is GitHub's list for the pull request, oldest first."""
    last = {}
    for review in reviews:
        login = (review.get("user") or {}).get("login")
        if (login and login != author and review.get("author_association") == OWNER
                and review.get("state") != "COMMENTED"):
            last[login] = review
    return any(review.get("state") == "APPROVED" and review.get("commit_id") == head for review in last.values())


def check(labels, changed, agents_account, reviews, head, author, released=()):
    """The reasons the pull request may not merge yet; empty when it may. released: the changed files
    that are exactly as in the template's release (released_files), which the owner agreed already."""
    kept = sorted(name for name in changed if kept_by_owner(name) and name not in released)
    errors = []
    if "ok-without-reading" in labels and kept:
        errors.append("it changes what only the owner's OK lets in, so it needs the label owner-review: "
                      + ", ".join(kept[:5]) + (" and more" if len(kept) > 5 else ""))
    needs_ok = "ok-without-reading" not in labels or kept
    if needs_ok and agents_account != "owner" and not approved_head(reviews, head, author):
        errors.append("it needs the owner's OK: an approval of its last commit")
    return errors


def git(*args):
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if done.returncode != 0:
        raise ValueError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def agents_account(base, head):
    """agents_account from docs/process.json on the base branch, so the pull request can't change it for
    itself; from the pull request when the base has none yet (setting up, adopting the process), and
    "own" when neither has it (the template itself)."""
    for commit in (base, head):
        try:
            config = json.loads(git("show", f"{commit}:docs/process.json"))
        except ValueError:
            continue
        project = config.get("project") if isinstance(config, dict) else None
        if isinstance(project, dict) and project.get("agents_account"):
            return project["agents_account"]
    return "own"


def changed_files(base, head):
    """The paths the pull request changes; a moved file counts at both its old and its new path."""
    return [name for name in git("diff", "--name-only", "--no-renames", f"{base}...{head}").splitlines() if name]


def blob(commit, name):
    """The id of a file's content at a commit, or None where the commit doesn't have it."""
    try:
        return git("rev-parse", "--verify", "--quiet", f"{commit}:{name}").strip()
    except ValueError:
        return None


def released_files(changed, base, head, repo):
    """The template's changed files and the lock, those exactly as in the release the pull request's lock
    names, of the template main's lock names: the pull request can't choose another template to vouch
    for it. Empty in the template itself, when the locks disagree on the template, or when the release
    can't be fetched."""
    owned_changed = [name for name in changed if owned.is_owned(name) or name == owned.LOCK]
    if not owned_changed:
        return set()
    try:
        template = json.loads(git("show", f"{base}:{owned.LOCK}"))["template"]
        lock = json.loads(git("show", f"{head}:{owned.LOCK}"))
        if lock["template"] != template or template.lower() == repo.lower():
            return set()
        git("fetch", "--quiet", "--depth=1", TEMPLATE_SOURCE.format(template), f"refs/tags/v{lock['version']}")
    except (ValueError, KeyError, TypeError):
        return set()
    return {name for name in owned_changed if blob(head, name) == blob("FETCH_HEAD", name)}


def reviews(repo, number):
    found, page = [], 1
    while True:
        request = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/pulls/{number}/reviews?per_page=100&page={page}",
            headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                     "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(request) as response:
            batch = json.load(response)
        found += batch
        if len(batch) < 100:
            return found
        page += 1


def main(argv):
    try:
        event = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        pull = event["pull_request"]
        base, head = pull["base"]["sha"], pull["head"]["sha"]
        repo = event["repository"]["full_name"]
        changed = changed_files(base, head)
        errors = check([label["name"] for label in pull.get("labels", [])], changed, agents_account(base, head),
                       reviews(repo, pull["number"]), head, (pull.get("user") or {}).get("login"),
                       released_files(changed, base, head, repo))
    except (OSError, ValueError, KeyError, IndexError) as error:
        errors = [f"can't read the pull request: {error}"]
    for error in errors:
        print(f"Owner's OK: {error}")
    if errors:
        return 1
    print("Owner's OK check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
