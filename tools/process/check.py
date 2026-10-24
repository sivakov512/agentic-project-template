#!/usr/bin/env python3
"""Runs every check an agent runs before pushing: the documents, the template's files against the lock,
the checks' own tests, the commits since the branch left main, then the project's checks from
docs/process.json. Standard library and git only.

    python3 tools/process/check.py                  everything
    python3 tools/process/check.py --process-only   what the process workflow runs in CI
"""

import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_docs  # noqa: E402
import check_commits  # noqa: E402
import owned  # noqa: E402

ROOT = HERE.parents[1]


def git(*args):
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else None


def branch_commits():
    """The commit check on this branch's commits since it left main, as CI runs it."""
    fork = git("merge-base", "HEAD", "origin/main") or git("merge-base", "HEAD", "main")
    if not fork:
        return []
    return check_commits.check(check_commits.messages(fork, "HEAD", ROOT), check_commits.rules(ROOT))


def run_tests():
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(suite)
    return result.wasSuccessful()


def main(argv):
    process_only = "--process-only" in argv[1:]
    failed = []
    for name, errors in (("Docs", check_docs.check(ROOT)), ("Template files", owned.check(ROOT)),
                         ("Commits", [] if process_only else branch_commits())):
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
