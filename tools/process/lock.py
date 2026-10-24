#!/usr/bin/env python3
"""Writes .process-lock.json for the template's files as they are now. Runs in the template only, after
changing the process (docs/process/updates.md, "Changing the process"); in a project it refuses, because
there the lock comes only from the template. Standard library and git only.

    python3 tools/process/lock.py
"""

import re
import subprocess
import sys

import owned


def origin(root):
    """The owner/name of the repository's origin remote on GitHub, or None."""
    done = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True, text=True)
    match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", done.stdout.strip())
    return match.group(1) if done.returncode == 0 and match else None


def main():
    repo = origin(owned.ROOT)
    try:
        lock = owned.read_lock(owned.ROOT)
    except ValueError:
        lock = None  # a broken lock is rewritten
    if repo is None:
        print("lock.py: this repository has no origin on GitHub, so it can't name itself as the template")
        return 1
    if lock and lock.get("template") != repo:
        print(f"lock.py: this is a project, not the template {lock.get('template')}: its template files "
              "can't change here (docs/process/updates.md)")
        return 1
    try:
        lock = owned.write_lock(owned.ROOT, repo)
    except (OSError, ValueError) as error:
        print(f"lock.py: {error}")
        return 1
    print(f"{owned.LOCK}: {repo} {lock['version']}, {len(lock['files'])} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
