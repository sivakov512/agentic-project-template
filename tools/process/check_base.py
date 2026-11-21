#!/usr/bin/env python3
"""Checks that a pull request's run in CI tests it on its base branch as the branch is now
(docs/process/workflow.md, step 7, "The base"). On a pull request CI checks out GitHub's merge of the pull
request into the base branch, and GitHub makes that merge again only some time after the base moves: a
run, even one started by closing and reopening the pull request, may test it on an old base, pass, and
let a merge break `main`. check.py runs this in CI on pull request events only, where it fails such a
run; merge.py reads the failure and runs the checks again on the new base. Standard library and git only.
"""

import subprocess

# The title of the annotation a failed run leaves on GitHub; merge.py looks for it.
TITLE = "Stale base"


def problem(merge_parents, base, current):
    """What is wrong with the run, or None: merge_parents are the parents of the commit CI checked out
    (GitHub's merge: the base, then the pull request's head), current the base branch's commit now."""
    if len(merge_parents) != 2:
        return (f"the run doesn't test GitHub's merge of the pull request into {base}, so it can't tell "
                f"which {base} it tests")
    if merge_parents[0] != current:
        return (f"the run tests the pull request on {base} at {merge_parents[0][:8]}, but {base} is now at "
                f"{current[:8]}: GitHub hadn't yet merged it again on the new {base}. Run the checks again "
                f"with tools/process/merge.py, which waits for that merge (docs/process/workflow.md, "
                f"step 7)")
    return None


def check(root, environ):
    """The errors for check.py: none outside a pull request's run in GitHub Actions."""
    base = environ.get("GITHUB_BASE_REF")
    if environ.get("GITHUB_EVENT_NAME") != "pull_request" or not base:
        return []
    head = subprocess.run(["git", "cat-file", "-p", "HEAD"], cwd=root, capture_output=True, text=True,
                          check=True).stdout
    parents = [line.split()[1] for line in head.splitlines() if line.startswith("parent ")]
    listed = subprocess.run(["git", "ls-remote", "origin", f"refs/heads/{base}"], cwd=root,
                            capture_output=True, text=True, check=True).stdout.split()
    found = problem(parents, base, listed[0] if listed else "")
    return [found] if found else []
