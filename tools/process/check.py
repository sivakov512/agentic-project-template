#!/usr/bin/env python3
"""Runs every check an agent runs before pushing: the documents, the template's files against the lock,
that workflows skipping draft pull requests run when one leaves draft, the checks' own tests, then the
project's checks from docs/process.json. The pull request's description and title have checks of their
own, check_pr.py and check_commits.py (docs/process/rules.md, "Your work"). Standard library and git only.

    python3 tools/process/check.py                  everything
    python3 tools/process/check.py --process-only   what the process workflow runs in CI
"""

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


def workflow_problems(root):
    """The workflows under .github/workflows that skip draft pull requests but don't run on
    `ready_for_review`, as messages: a skipped job counts as passing for the merge, so such a job would
    never test the pull request before it merges. Empty when there are none."""
    problems = []
    for path in sorted((root / ".github" / "workflows").glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        if re.search(r"pull_request\.draft\s*==\s*false", text) and "ready_for_review" not in text:
            problems.append(f"{path.relative_to(root)} skips draft pull requests but doesn't run on "
                            f"ready_for_review, so its skipped jobs would never test the pull request "
                            f"(docs/process/workflow.md#reviews-in-draft)")
    return problems


def run_tests():
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(suite)
    return result.wasSuccessful()


def main(argv):
    process_only = "--process-only" in argv[1:]
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
