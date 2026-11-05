#!/usr/bin/env python3
"""Checks that a pull request which needs the owner's OK has it, so the coordinator can merge the rest
on its own (docs/process/workflow.md, "The owner's OK and the merge"). Standard library and git only.

A pull request needs the owner's OK unless it is labelled ok-without-reading, and it always needs it
when it changes what the owner keeps for themself: CLAUDE.md and CLAUDE.local.md at any depth, a .claude
folder or file and anything in it, .mcp.json, docs/plan.md, docs/process.json, anything under .github/,
the paths docs/process.json's "kept" names on the base branch, or the template's files and its lock,
names compared whatever their case. A symlink or submodule at one of these paths, or at a folder on the
way to one, never goes in, approved or not, since the check can't see what is behind it; nor does a file
Claude Code loads as rules (a CLAUDE.md, a rule under .claude/rules/) that imports ("@" and a path) a
file the owner doesn't keep, or a symlink or submodule. The
template's files and the lock of a process update are the exception where each is exactly as in the
newer release the update's lock names, of the template main's lock names, and that release is on the
template's main: the owner agreed it in the template. With the agents' own account the OK is an approval
of the pull request's last commit by the repository's owner; with the owner's account nobody can approve
their own pull request, so the check only makes sure the label isn't ok-without-reading where it can't be,
and the OK stays the owner's word that the coordinator quotes.

check_pr.py takes api and rerun_red from here for its own runs.

In CI, with GH_TOKEN set to a token that can read the pull request's labels and reviews, run from the
base branch's copy of this file as it is now (.github/workflows/process-owner.yml), so the pull request
can't change it:
    python3 -I <the base branch's checkout>/tools/process/check_owner.py "$GITHUB_EVENT_PATH"
"""

import fnmatch
import json
import os
import posixpath
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import owned  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
KEPT_BY_OWNER = ["docs/plan.md", "docs/process.json", ".mcp.json", owned.LOCK]
# Rules for agents and their permissions, hooks and tools, which Claude Code reads at any depth: a file
# of these names, or a .claude folder or file and anything under it.
KEPT_NAMES = ["claude.md", "claude.local.md", ".claude"]
# Where the paths the owner keeps lie, so a symlink or submodule at a folder on the way to them is seen.
KEPT_PLACES = KEPT_BY_OWNER + owned.OWNED_DIRS + owned.OWNED_FILES + [".github"]
# Git's modes for what the check can't look into: a symlink and a submodule.
LINK, SUBMODULE = "120000", "160000"
# Who may give the OK: the repository's owner. Collaborators, the agents' account among them, and on a
# public repository anyone at all can approve too, so their approvals don't count.
OWNER = "OWNER"


def kept_by_owner(name, kept=()):
    """Whether a changed path is one only the owner's OK lets in. kept: the patterns of docs/process.json's
    "kept" (docs/process/config.md), matched with fnmatch from the repository's root. Names are compared
    whatever their case: on the owner's Mac, claude.md or .Claude/ open as CLAUDE.md and .claude/."""
    name = name.casefold()
    return (name in KEPT_BY_OWNER or any(part in KEPT_NAMES for part in name.split("/"))
            or name.startswith(".github/") or owned.is_owned(name)
            or any(fnmatch.fnmatchcase(name, pattern.casefold()) for pattern in kept))


def tree(commit):
    """Every entry of the commit's tree, as (mode, object id, path): files, symlinks and submodules."""
    entries = []
    for entry in git("ls-tree", "-r", "-z", commit).split("\0"):
        meta, _, path = entry.partition("\t")
        if path:
            mode, _, rest = meta.partition(" ")
            entries.append((mode, rest.split(" ")[-1], path))
    return entries


def text_of(object_id):
    """A file's content as text, bad bytes replaced: Claude Code reads such a file too."""
    done = subprocess.run(["git", "cat-file", "-p", object_id], cwd=ROOT, capture_output=True)
    if done.returncode != 0:
        raise ValueError(f"git cat-file -p {object_id}: {done.stderr.decode('utf-8', 'replace').strip()}")
    return done.stdout.decode("utf-8", "replace")


def is_rule_file(path):
    """Whether Claude Code loads the file as rules by itself: a CLAUDE.md or CLAUDE.local.md in any
    folder, or a Markdown file under a .claude/rules/ folder."""
    path = path.casefold()
    return path.rsplit("/", 1)[-1] in KEPT_NAMES[:2] or ("/.claude/rules/" in "/" + path and path.endswith(".md"))


def import_errors(entries, kept=()):
    """Why the pull request can't merge yet: a file Claude Code loads as rules (is_rule_file), or one it
    imports in turn, imports with "@path" a file of the tree (entries, from tree) the owner doesn't keep,
    or a symlink or submodule, or a path through one: its rules could then change without the owner. A
    path is read relative to the importing file and from the repository's root; anything after an "@"
    that could be a path counts, inside code or not, and a path to nothing in the tree is left alone."""
    found = {path.casefold(): (mode, object_id, path) for mode, object_id, path in entries}
    queue = [path for mode, _, path in entries if mode.startswith("100") and is_rule_file(path)]
    seen, errors = set(), []
    while queue:
        path = queue.pop()
        if path.casefold() in seen:
            continue
        seen.add(path.casefold())
        for raw in re.findall(r"@([^\s@`'\"()<>\[\]{}]+)", text_of(found[path.casefold()][1])):
            for name in {raw, raw.rstrip(".,;:!?")}:
                for base in (posixpath.dirname(path), ""):
                    target = posixpath.normpath(posixpath.join(base, name)).casefold()
                    links = [found[folder] for folder in folders(target) + [target]
                             if folder in found and found[folder][0] in (LINK, SUBMODULE)]
                    if links:
                        what = "symlink" if links[0][0] == LINK else "submodule"
                        errors.append(f"{path} imports {raw.rstrip('.,;:!?')} through the {what}"
                                      f" {links[0][2]}: the check can't see what is behind it, so import a"
                                      " plain file")
                    elif target in found and not kept_by_owner(found[target][2], kept):
                        errors.append(f"{path} imports {found[target][2]}, which the owner doesn't keep: add"
                                      " it to \"kept\" in docs/process.json or move it under .claude/")
                    elif target in found:
                        queue.append(found[target][2])
    return sorted(set(errors))


def folders(path):
    """The folders path lies in, outermost first: a/b/c gives a and a/b."""
    parts = path.split("/")
    return ["/".join(parts[:index]) for index in range(1, len(parts))]


def on_the_way(path, kept=(), places=()):
    """Whether path, whatever its case, is one the owner keeps, a folder on the way to one of places (in
    lower case: KEPT_PLACES and the kept files of the trees, as link_errors gathers them), or a folder
    under which a kept pattern could match."""
    path = path.casefold()
    return (kept_by_owner(path, kept)
            or any(place == path or place.startswith(path + "/") for place in places)
            or any(re.split(r"[*?[]", pattern, maxsplit=1)[0].casefold().startswith(path + "/")
                   or fnmatch.fnmatchcase(path + "/\0", pattern.casefold()) for pattern in kept))


def link_errors(entries, kept=(), trees=()):
    """Why the pull request can't merge whatever its approvals: a symlink or submodule among entries (the
    head's tree, from tree) at a path the owner keeps or a folder on the way to one (on_the_way, with the
    trees of the base and the head). The check can't see where a link leads or what a submodule holds, so
    the owner's OK of the path wouldn't cover what is behind it, and following links as the owner's Mac
    would is too easy to get wrong."""
    places = [place.casefold() for place in KEPT_PLACES] + [name.casefold() for _, _, name in trees
                                                            if kept_by_owner(name, kept)]
    errors = []
    for mode, _, path in entries:
        if mode not in (LINK, SUBMODULE) or not on_the_way(path, kept, places):
            continue
        hint = (" A CLAUDE.md that should say what another file says is a plain file with the line"
                " @<that file>, @AGENTS.md say, with that file added to \"kept\" in docs/process.json."
                if path.rsplit("/", 1)[-1].casefold() in ("claude.md", "claude.local.md") else "")
        errors.append(f"{path} is a {'symlink' if mode == LINK else 'submodule'} where the owner keeps the"
                      " paths: it never goes in, not even with the owner's approval; make it a plain file or"
                      " folder." + hint)
    return errors


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


def check(labels, changed, agents_account, reviews, head, author, released=(), kept=()):
    """The reasons the pull request may not merge yet; empty when it may. released: the changed files
    that are exactly as in the template's release (released_files), which the owner agreed already.
    kept: the base branch's "kept" patterns (kept_patterns)."""
    owners = sorted(name for name in changed if kept_by_owner(name, kept) and name not in released)
    errors = []
    if "ok-without-reading" in labels and owners:
        errors.append("it changes what only the owner's OK lets in, so it needs the label owner-review: "
                      + ", ".join(owners[:5]) + (" and more" if len(owners) > 5 else ""))
    needs_ok = "ok-without-reading" not in labels or owners
    if needs_ok and agents_account != "owner" and not approved_head(reviews, head, author):
        errors.append("it needs the owner's OK: an approval of its last commit")
    return errors


def git(*args):
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if done.returncode != 0:
        raise ValueError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def config_at(commit):
    """docs/process.json at a commit; an empty dict where it is missing or not a JSON object."""
    try:
        config = json.loads(git("show", f"{commit}:docs/process.json"))
    except ValueError:
        return {}
    return config if isinstance(config, dict) else {}


def agents_account(base, head, author=None, owner=None):
    """agents_account from docs/process.json on the base branch, so the pull request can't change it for
    itself, and "own" when neither branch has it (the template itself). When the base has none yet
    (setting up, adopting the process) it comes from the pull request: there "owner" would let it in
    without an approval, and "own" would block it for good where the agents really work as the owner,
    since nobody can approve their own pull request. So the pull request's "owner" counts only when its
    author is the repository's owner (owner: that login, None where the repository belongs to an
    organisation and that can't be told); doctor.py checks the setting against gh's account after."""
    for from_pull_request, commit in ((False, base), (True, head)):
        project = config_at(commit).get("project")
        if isinstance(project, dict) and project.get("agents_account"):
            value = project["agents_account"]
            if from_pull_request and value == "owner" and owner and (author or "").lower() != owner.lower():
                return "own"
            return value
    return "own"


def kept_patterns(commit):
    """The patterns of "kept" in docs/process.json at a commit, the base branch's where the pull request
    mustn't change them for itself; empty where there are none."""
    kept = config_at(commit).get("kept")
    return [pattern for pattern in kept if isinstance(pattern, str)] if isinstance(kept, list) else []


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
    for it. Empty in the template itself, when the locks disagree on the template, when the release is
    not newer than the base's (going back to an older one needs the owner's OK), when the release can't
    be fetched, or when its tag is not on the template's main (owned.fetch_release)."""
    owned_changed = [name for name in changed if owned.is_owned(name) or name == owned.LOCK]
    if not owned_changed:
        return set()
    try:
        base_lock = json.loads(git("show", f"{base}:{owned.LOCK}"))
        lock = json.loads(git("show", f"{head}:{owned.LOCK}"))
        template = base_lock["template"]
        if (lock["template"] != template or template.lower() == repo.lower()
                or owned.version_tuple(lock["version"]) <= owned.version_tuple(base_lock["version"])):
            return set()
        release = owned.fetch_release(ROOT, template, lock["version"])
    except (ValueError, KeyError, TypeError, AttributeError):
        return set()
    if release is None:
        return set()
    return {name for name in owned_changed if blob(head, name) == blob(release, name)}




def api(path, method="GET"):
    """Calls GitHub's API at path (after api.github.com/) with GH_TOKEN; returns the parsed JSON, or None
    for an empty answer. Raises OSError (HTTPError) when the call fails, and KeyError without GH_TOKEN.
    check_pr.py uses it too."""
    request = urllib.request.Request(f"https://api.github.com/{path}", method=method,
                                     headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                                              "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request) as response:
        body = response.read()
        return json.loads(body) if body else None


def rerun_red(repo, head, this_run, workflow="process-owner.yml"):
    """Runs again the failed runs of a check (its workflow file) on the same commit. Each event (a push, a label, a review)
    starts a run of its own, and a run an earlier event left red keeps blocking the merge after a later
    one passes; run again, it reads the labels and reviews as they are now. Failures here are ignored:
    the red run can still be run again by hand (docs/process/pull-requests.md)."""
    try:
        runs = api(f"repos/{repo}/actions/workflows/{workflow}/runs?head_sha={head}&status=failure&per_page=100")
        red = [run["id"] for run in runs.get("workflow_runs", []) if str(run["id"]) != this_run]
    except (OSError, ValueError, KeyError, AttributeError):
        return
    for run_id in red:
        try:  # one already running again, or too old, doesn't stop the others
            api(f"repos/{repo}/actions/runs/{run_id}/rerun", method="POST")
        except (OSError, ValueError):
            pass


def labels(repo, number):
    """The pull request's labels as they are now. The event's own list is how they were when it fired, so
    a rerun of a run that an earlier event left red would judge the old labels."""
    return [label["name"] for label in api(f"repos/{repo}/issues/{number}/labels?per_page=100")]


def reviews(repo, number):
    found, page = [], 1
    while True:
        batch = api(f"repos/{repo}/pulls/{number}/reviews?per_page=100&page={page}")
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
        author = (pull.get("user") or {}).get("login")
        owner = event["repository"].get("owner") or {}
        owner = owner.get("login") if owner.get("type") == "User" else None
        changed = changed_files(base, head)
        base_tree, head_tree = tree(base), tree(head)
        kept = kept_patterns(base)
        # The head's "kept" counts for imports too: a pull request that adds to it changes
        # docs/process.json, which needs the owner's OK anyway.
        errors = (import_errors(head_tree, kept + kept_patterns(head))
                  + link_errors(head_tree, kept, base_tree + head_tree)
                  + check(labels(repo, pull["number"]), changed, agents_account(base, head, author, owner),
                          reviews(repo, pull["number"]), head, author, released_files(changed, base, head, repo),
                          kept))
    except (OSError, ValueError, KeyError, IndexError) as error:
        errors = [f"can't read the pull request: {error}"]
    for error in errors:
        print(f"Owner's OK: {error}")
    if errors:
        return 1
    print("Owner's OK check passed")
    if os.environ.get("GITHUB_RUN_ID"):
        rerun_red(repo, head, os.environ["GITHUB_RUN_ID"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
