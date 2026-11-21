#!/usr/bin/env python3
"""Runs every check an agent runs before pushing: the documents, the template's files against the lock,
the checks' own tests, then the project's checks from docs/process.json; in a pull request's run in CI,
also that the run tests the pull request on its base as the base is now (check_base.py). The pull
request's description and title have checks of their own, check_pr.py and check_commits.py
(docs/process/rules.md, "Your work"). Standard library and git only.

    python3 tools/process/check.py                  everything
    python3 tools/process/check.py --process-only   what the process workflow runs in CI
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_base  # noqa: E402
import check_docs  # noqa: E402
import owned  # noqa: E402

ROOT = HERE.parents[1]


def run_tests():
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(suite)
    return result.wasSuccessful()


def main(argv):
    process_only = "--process-only" in argv[1:]
    failed = []
    for name, errors in (("Docs", check_docs.check(ROOT)), ("Template files", owned.check(ROOT))):
        for error in errors:
            print(f"{name}: {error}")
        if errors:
            failed.append(name)
    for error in check_base.check(ROOT, os.environ):
        # The annotation's title is how merge.py tells this failure from others.
        print(f"::error title={check_base.TITLE}::{error}")
        print(f"Base: {error}")
        failed.append("Base")
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
