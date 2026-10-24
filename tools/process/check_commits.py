#!/usr/bin/env python3
"""Checks the commit messages of a pull request. Standard library and git only.

Every subject is at most 72 characters and not empty. docs/process.json may also ask for one-line messages
and no "Co-authored-by" (docs/process/config.md, "commits").

    python3 tools/process/check_commits.py <base sha> <head sha>
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def rules(root):
    try:
        commits = json.loads((root / "docs/process.json").read_text(encoding="utf-8")).get("commits", {})
    except (OSError, ValueError, AttributeError):
        commits = {}
    return commits if isinstance(commits, dict) else {}


def check(messages, rules):
    """Takes (sha, full message) pairs and the commit rules; returns the problems found."""
    errors = []
    for sha, message in messages:
        lines = message.rstrip("\n").split("\n")
        subject = lines[0]
        short = sha[:7]
        if not subject.strip():
            errors.append(f"{short}: empty subject")
        if len(subject) > 72:
            errors.append(f"{short}: subject is {len(subject)} characters, at most 72")
        if rules.get("one_line") and any(line.strip() for line in lines[1:]):
            errors.append(f"{short}: has a body; a commit message is one subject line here")
        if rules.get("no_co_authors") and "co-authored-by" in message.lower():
            errors.append(f"{short}: has a Co-authored-by line")
    return errors


def messages(base, head, root=ROOT):
    out = subprocess.run(
        ["git", "log", "--format=%H%x00%B%x01", f"{base}..{head}"],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout
    for record in out.split("\x01"):
        record = record.strip("\n")
        if record:
            sha, _, message = record.partition("\x00")
            yield sha, message


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        found = list(messages(argv[1], argv[2]))
    except subprocess.CalledProcessError as error:
        print(f"Commits: git can't list {argv[1]}..{argv[2]}: {error.stderr.strip()}")
        return 2
    errors = check(found, rules(ROOT))
    for error in errors:
        print(f"Commit {error}")
    if errors:
        return 1
    print("Commit messages check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
