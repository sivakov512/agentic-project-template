#!/usr/bin/env python3
"""Runs every check an agent runs before pushing: the documents, the template's files against the lock,
that workflows skipping draft pull requests run when one leaves draft, the checks' own tests, then the
project's checks from docs/process.json. In a pull request's run in CI it also notes which commit of
the base the run tests, for merge.py (docs/process/workflow.md#the-merge). The pull request's
description and title have checks of their own, check_pr.py and check_commits.py
(docs/process/rules.md, "Your work"). Standard library and git only.

    python3 tools/process/check.py                  everything
    python3 tools/process/check.py --process-only   what the process workflow runs in CI
"""

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_docs  # noqa: E402
import owned  # noqa: E402

ROOT = HERE.parents[1]


# How a workflow skips draft pull requests: draft == false, draft != true, or !...draft.
SKIPS_DRAFTS = r"pull_request\.draft\s*(==\s*false|!=\s*true)|!\s*github\.event\.pull_request\.draft"


def workflow_problems(root):
    """The workflows under .github/workflows that skip draft pull requests but don't run on
    `ready_for_review`, as messages: a skipped job counts as passing for the merge, so such a job would
    never test the pull request before it merges. Empty when there are none."""
    problems = []
    for path in sorted((root / ".github" / "workflows").glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        if re.search(SKIPS_DRAFTS, text) and "ready_for_review" not in text:
            problems.append(f"{path.relative_to(root)} skips draft pull requests but doesn't run on "
                            f"ready_for_review, so its skipped jobs would never test the pull request "
                            f"(docs/process/workflow.md#reviews-in-draft)")
    return problems


# The title of the note a pull request's run leaves on GitHub with the base commit it tests, which
# merge.py reads.
TESTED_BASE = "Tested base"


def tested_base(root, environ):
    """The commit of the base branch that a pull request's run in GitHub Actions tests: the first parent
    of GitHub's merge it checked out. None outside such a run, when HEAD isn't a merge, or when git can't
    read it."""
    if environ.get("GITHUB_EVENT_NAME") != "pull_request":
        return None
    done = subprocess.run(["git", "cat-file", "-p", "HEAD"], cwd=root, capture_output=True, text=True)
    parents = [line.split()[1] for line in done.stdout.splitlines() if line.startswith("parent ")]
    return parents[0] if done.returncode == 0 and len(parents) == 2 else None


def run_tests():
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(suite)
    return result.wasSuccessful()


def main(argv):
    process_only = "--process-only" in argv[1:]
    base = tested_base(ROOT, os.environ) if process_only else None
    if base:
        print(f"::notice title={TESTED_BASE}::{base}")
    failed = []
    for name, errors in (("Docs", check_docs.check(ROOT)), ("Template files", owned.check(ROOT)),
                         ("Workflows", workflow_problems(ROOT))):
        for error in errors:
            print(f"{name}: {error}")
        if errors:
            failed.append(name)
    if not run_tests():
        failed.append("Tests of the checks")
    if not process_only:
        try:
            config = check_docs.load_config(ROOT)
        except ValueError:
            config = None
        # A bad config is reported by the docs check; its commands are not run.
        commands = config.get("checks", []) if config is not None and not check_docs.config_errors(config) else []
        for command in commands:
            print(f"$ {command}", flush=True)
            if subprocess.run(command, shell=True, cwd=ROOT).returncode != 0:
                failed.append(command)
    if failed:
        print("Failed: " + "; ".join(dict.fromkeys(failed)))
        return 1
    print("All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
