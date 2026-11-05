#!/usr/bin/env python3
"""Checks a pull request's title against the commit rules. Standard library only.

main takes each pull request as one squash commit whose subject is the title and whose body is empty
(docs/process/workflow.md, step 7), so the title is the commit main gets: at most 72 characters and not
empty, and a Conventional Commits subject where docs/process.json asks for it (docs/process/config.md,
"commits"). The commits on the branch are not checked: none of them reaches main. Pull requests opened
by a GitHub App are checked too, since their titles land on main as well.

In CI, with GH_TOKEN set (.github/workflows/process-pr.yml); the title is read from the API when the
check runs, since the event's copy is how it was when the event fired:
    python3 tools/process/check_commits.py "$GITHUB_EVENT_PATH"
Locally:
    python3 tools/process/check_commits.py --title "Code: export to CSV"
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_owner  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
# A Conventional Commits subject: one of the usual types (the ones release tools read), an optional scope,
# an optional "!", then ": " and a description.
TYPES = ("feat", "fix", "perf", "revert", "refactor", "chore", "docs", "style", "test", "build", "ci")
CONVENTIONAL = re.compile(r"^(" + "|".join(TYPES) + r")(\([a-z0-9][a-z0-9._/-]*\))?!?: \S")


def rules(root):
    """The "commits" settings of docs/process.json under root; an empty dict when there are none.
    check_pr.py reads them too."""
    try:
        commits = json.loads((root / "docs/process.json").read_text(encoding="utf-8")).get("commits", {})
    except (OSError, ValueError, AttributeError):
        commits = {}
    return commits if isinstance(commits, dict) else {}


def check(title, rules):
    """Takes the title and the commit rules; returns the problems found."""
    errors = []
    if not title.strip():
        errors.append("the title is empty")
    if len(title) > 72:
        errors.append(f"the title is {len(title)} characters, at most 72")
    if rules.get("conventional") and title.strip() and not CONVENTIONAL.match(title):
        errors.append("the title is not a Conventional Commits subject (\"type(scope): description\", type one"
                      f" of {', '.join(TYPES)})")
    return errors


def main(argv):
    parser = argparse.ArgumentParser(description="Check a pull request's title against the commit rules.")
    parser.add_argument("event", nargs="?", help="the GitHub event file")
    parser.add_argument("--title", help="the title to check, instead of an event file")
    args = parser.parse_args(argv[1:])
    if (args.title is None) == (args.event is None):
        parser.print_help()
        return 2
    title = args.title
    if args.event:
        try:
            event = json.loads(Path(args.event).read_text(encoding="utf-8"))
            pull_request = event.get("pull_request", {})
            repo = (event.get("repository") or {}).get("full_name")
            if os.environ.get("GH_TOKEN") and repo and pull_request.get("number"):
                pull_request = check_owner.api(f"repos/{repo}/pulls/{pull_request['number']}")
            title = pull_request.get("title") or ""
        except (OSError, ValueError, KeyError) as error:
            print(f"Title: can't read the pull request: {error}")
            return 2
    errors = check(title, rules(ROOT))
    for error in errors:
        print(f"Title: {error}; it becomes the subject of main's commit (docs/process/config.md)")
    if errors:
        return 1
    print("Title check against the commit rules passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
