#!/usr/bin/env python3
"""Checks that a pull request's run in CI tests it on its base branch as the branch is now
(docs/process/workflow.md, step 7, "The base"). On a pull request CI checks out GitHub's merge of the pull
request into the base branch, and GitHub makes that merge again only some time after the base moves: a
run, even one started by closing and reopening the pull request, may test it on an old base, pass, and
let a merge break `main`. `check.py --process-only` runs this in the `process-docs` job on pull request
events only and fails such a run; merge.py reads that failure by its annotation's title and runs the
checks again. Standard library and git only.
"""

import subprocess

# The title of the annotation a run on an old base leaves on GitHub; merge.py looks for it.
TITLE = "Stale base"


def problem(merge_parents, base, current):
    """What is wrong with the run, as (stale, message), or None. merge_parents are the parents of the
    commit CI checked out (GitHub's merge: the base, then the pull request's head), current the base
    branch's commit now; stale says the run tested an old base."""
    if len(merge_parents) != 2:
        return False, (f"the run doesn't test GitHub's merge of the pull request into {base}, so it can't "
                       f"tell which {base} it tests")
    if merge_parents[0] != current:
        return True, (f"the run tests the pull request on {base} at {merge_parents[0][:8]}, but {base} is "
                      f"now at {current[:8]}: GitHub hadn't yet merged it again on the new {base}. The "
                      f"coordinator runs the checks again (docs/process/workflow.md, step 7)")
    return None


def check(root, environ):
    """The problems, as (stale, message) pairs: none outside a pull request's run in GitHub Actions.
    Raises subprocess.CalledProcessError when git can't read the checkout or the remote."""
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
