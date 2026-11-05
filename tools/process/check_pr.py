#!/usr/bin/env python3
"""Checks a pull request: its description against .github/pull_request_template.md, its title and its labels.
Standard library only.

Fails when a section of the template is missing or says next to nothing (a bare "None" is enough for "Not
done and open questions"; a coordinator record or a process update needs only the sections in SHORT);
when "Backlog item" doesn't name exactly one item that exists in docs/backlog.md (or say what else it
is: "Coordinator record", which may name several, "Setup", "Process update" or "Process change"); when
"Behaviour change" doesn't start with "None" and why, or with "Yes" and at least three steps to try it;
when the title doesn't start with its kind, where docs/process.json doesn't ask for Conventional Commits
(check_commits.py checks the title against the commit rules); or when the labels don't hold exactly one
review label, other labels aside (docs/process/pull-requests.md). Pull requests opened by a GitHub App
(a release or dependency bot) are not checked.

In CI, with GH_TOKEN set (.github/workflows/process-pr.yml); the pull request is read from the API when
the check runs, since the event's copy is how it was when the event fired, and a passing run runs again
the red runs earlier events left on the same commit:
    python3 tools/process/check_pr.py "$GITHUB_EVENT_PATH"
Locally, on a draft:
    python3 tools/process/check_pr.py --body description.md [--title "Code: …" --labels owner-review]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_commits  # noqa: E402
import check_owner  # noqa: E402

SECTIONS = [
    "Backlog item",
    "What changed",
    "Behaviour change",
    "Why",
    "How it was checked",
    "Docs updated",
    "Owner review",
    "Not done and open questions",
]
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
# The title prefixes of the kinds, where titles are not Conventional Commits subjects.
KINDS = ("Plan:", "Spec:", "Research:", "Code:")
# The one label a pull request carries, and its description for doctor.py --fix-labels.
REVIEW_LABELS = {"owner-review": "The owner reads it before saying yes",
                 "ok-without-reading": "The coordinator merges it; the owner sees it in the report"}
# What a pull request that is no backlog item says instead (docs/process/pull-requests.md).
NOT_AN_ITEM = re.compile(r"^(coordinator record|setup|process update|process change)\b", re.IGNORECASE)
# The sections a coordinator record or a process update needs; it may leave out the rest.
SHORT = ["Backlog item", "What changed", "Owner review"]
SHORT_RECORD = re.compile(r"^(coordinator record|process update)\b", re.IGNORECASE)
# A section where the template's own comment asks for a bare "None" when there is nothing to say.
NOTHING_OPEN = ("Not done and open questions", re.compile(r"^none\.?$", re.IGNORECASE))


def sections(body):
    """Maps each "## " heading to the text under it, with HTML comments removed."""
    found = {}
    current = None
    for line in COMMENT.sub("", body).splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1)
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in found.items()}


def words(text):
    return re.findall(r"[A-Za-z0-9]+", text)


def check(body, root, title=None, labels=None):
    errors = []
    found = sections(body)
    short = SHORT_RECORD.match(found.get("Backlog item", ""))
    for name in SHORT if short else SECTIONS:
        if name not in found:
            errors.append(f"section \"{name}\" is missing")
        elif not found[name]:
            errors.append(f"section \"{name}\" is empty")
        elif len(words(found[name])) < 2 and not (name == "Backlog item" and NOT_AN_ITEM.match(found[name])
                                                  or name == NOTHING_OPEN[0] and NOTHING_OPEN[1].match(found[name])):
            errors.append(f"section \"{name}\" says next to nothing")

    item = found.get("Backlog item", "")
    if item:
        ids = sorted(set(re.findall(r"\bB-\d{3}\b", item)))
        record = NOT_AN_ITEM.match(item)
        backlog_path = root / "docs" / "backlog.md"
        backlog = backlog_path.read_text(encoding="utf-8") if backlog_path.exists() else ""
        if not ids and not record:
            errors.append("\"Backlog item\" names no B-### and is not one of: Coordinator record, Setup, Process update, Process change")
        elif len(ids) > 1 and not (record and record.group(1).lower() == "coordinator record"):
            errors.append(f"\"Backlog item\" names {len(ids)} items; a pull request belongs to one")
        for item_id in ids:
            if not re.search(rf"^- \[[ x]\] \*\*{item_id}\*\*", backlog, re.MULTILINE):
                errors.append(f"\"Backlog item\": {item_id} is not in docs/backlog.md")

    behaviour = found.get("Behaviour change", "")
    if behaviour and not short:
        answer = re.match(r"^(none|yes)\b(.*)", behaviour, re.IGNORECASE | re.DOTALL)
        if not answer:
            errors.append("\"Behaviour change\" must start with \"None\" or \"Yes\"")
        elif answer.group(1).lower() == "none" and len(words(answer.group(2))) < 2:
            errors.append("\"Behaviour change: None\" must say why nothing changes for the user")
        elif answer.group(1).lower() == "yes":
            steps = re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", answer.group(2), re.MULTILINE)
            if len(steps) < 3:
                errors.append("\"Behaviour change: Yes\" needs at least three steps to try it, as a list")

    # With Conventional Commits the type stands in for the kind, and check_commits.py checks it.
    if title is not None and not check_commits.rules(root).get("conventional"):
        if not any(title.startswith(prefix + " ") for prefix in KINDS):
            errors.append("the title must start with one of: " + ", ".join(KINDS))
    if labels is not None and len([label for label in labels if label in REVIEW_LABELS]) != 1:
        errors.append("it needs exactly one review label: " + ", ".join(REVIEW_LABELS))
    return errors


def main(argv):
    parser = argparse.ArgumentParser(description="Check a pull request description.")
    parser.add_argument("event", nargs="?", help="the GitHub event file")
    parser.add_argument("--body", help="a file with the description, instead of an event file")
    parser.add_argument("--title", help="with --body: the title to check")
    parser.add_argument("--labels", help="with --body: the labels to check, comma-separated")
    args = parser.parse_args(argv[1:])
    repo = None
    if bool(args.body) == bool(args.event):
        parser.print_help()
        return 2
    try:
        if args.body:
            body = Path(args.body).read_text(encoding="utf-8")
            title = args.title
            labels = args.labels.split(",") if args.labels is not None else None
        else:
            event = json.loads(Path(args.event).read_text(encoding="utf-8"))
            pull_request = event.get("pull_request", {})
            repo = (event.get("repository") or {}).get("full_name")
            if os.environ.get("GH_TOKEN") and repo and pull_request.get("number"):
                pull_request = check_owner.api(f"repos/{repo}/pulls/{pull_request['number']}")
            if pull_request.get("draft"):
                print("Draft pull request: its description is checked when it leaves draft")
                return 0
            if pull_request.get("user", {}).get("type") == "Bot":
                print("Opened by a GitHub App: not checked (docs/process/pull-requests.md)")
                return 0
            body = pull_request.get("body") or ""
            title = pull_request.get("title") or ""
            labels = [label["name"] for label in pull_request.get("labels", [])]
    except (OSError, ValueError, KeyError) as error:
        print(f"Pull request description: can't read it: {error}")
        return 2
    errors = check(body, Path(__file__).resolve().parents[2], title, labels)
    for error in errors:
        print(f"Pull request description: {error}")
    if errors:
        print("Fill it in by .github/pull_request_template.md")
        return 1
    print("Pull request description check passed")
    if args.event and os.environ.get("GITHUB_RUN_ID") and repo:
        check_owner.rerun_red(repo, pull_request["head"]["sha"], os.environ["GITHUB_RUN_ID"], "process-pr.yml")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
