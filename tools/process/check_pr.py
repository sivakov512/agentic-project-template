#!/usr/bin/env python3
"""Checks a pull request: its description against .github/pull_request_template.md, its title and its labels.
Standard library only.

Fails when a section of the template is missing or says next to nothing; when "Backlog item" doesn't name
exactly one item that exists in docs/backlog.md (or say what else it is: "Coordinator record", "Setup",
"Process update" or "Process change"); when "Behaviour change" doesn't start with "None" and why, or with
"Yes" and at least three steps to try it; when the title doesn't start with its kind; or when the
labels aren't one kind and one review label that agree with the title (docs/process/pull-requests.md).
Pull requests opened by a GitHub App (a release or dependency bot) are not checked.

In CI:
    python3 tools/process/check_pr.py "$GITHUB_EVENT_PATH"
Locally, on a draft:
    python3 tools/process/check_pr.py --body description.md [--title "Code: …" --labels code,owner-review]
"""

import argparse
import json
import re
import sys
from pathlib import Path

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
KINDS = {"plan": "Plan:", "spec": "Spec:", "research": "Research:", "code": "Code:"}
KIND_DESCRIPTIONS = {
    "plan": "The plan, rules for agents, the process, checks and CI",
    "spec": "What the product must do and how it looks",
    "research": "Studies, facts found by experiment",
    "code": "The code of the tools and of the product",
}
REVIEW_LABELS = {"owner-review": "The owner reads it before saying yes",
                 "ok-without-reading": "The owner says yes without reading it"}
# What a pull request that is no backlog item says instead (docs/process/pull-requests.md).
NOT_AN_ITEM = re.compile(r"^(coordinator record|setup|process update|process change)\b", re.IGNORECASE)


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
    for name in SECTIONS:
        if name not in found:
            errors.append(f"section \"{name}\" is missing")
        elif not found[name]:
            errors.append(f"section \"{name}\" is empty")
        elif len(words(found[name])) < 2 and not (name == "Backlog item" and NOT_AN_ITEM.match(found[name])):
            errors.append(f"section \"{name}\" says next to nothing")

    item = found.get("Backlog item", "")
    if item:
        ids = sorted(set(re.findall(r"\bB-\d{3}\b", item)))
        record = NOT_AN_ITEM.match(item)
        backlog_path = root / "docs" / "backlog.md"
        backlog = backlog_path.read_text(encoding="utf-8") if backlog_path.exists() else ""
        if not ids and not record:
            errors.append("\"Backlog item\" names no B-### and is not one of: Coordinator record, Setup, Process update, Process change")
        elif len(ids) > 1:
            errors.append(f"\"Backlog item\" names {len(ids)} items; a pull request belongs to one")
        for item_id in ids:
            if not re.search(rf"^- \[[ x]\] \*\*{item_id}\*\*", backlog, re.MULTILINE):
                errors.append(f"\"Backlog item\": {item_id} is not in docs/backlog.md")

    behaviour = found.get("Behaviour change", "")
    if behaviour:
        answer = re.match(r"^(none|yes)\b(.*)", behaviour, re.IGNORECASE | re.DOTALL)
        if not answer:
            errors.append("\"Behaviour change\" must start with \"None\" or \"Yes\"")
        elif answer.group(1).lower() == "none" and len(words(answer.group(2))) < 2:
            errors.append("\"Behaviour change: None\" must say why nothing changes for the user")
        elif answer.group(1).lower() == "yes":
            steps = re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", answer.group(2), re.MULTILINE)
            if len(steps) < 3:
                errors.append("\"Behaviour change: Yes\" needs at least three steps to try it, as a list")

    if title is not None:
        kinds = [k for k, prefix in KINDS.items() if title.startswith(prefix + " ")]
        if not kinds:
            errors.append("the title must start with one of: " + ", ".join(KINDS.values()))
    if labels is not None:
        kind_labels = [label for label in labels if label in KINDS]
        review_labels = [label for label in labels if label in REVIEW_LABELS]
        if len(kind_labels) != 1:
            errors.append("it needs exactly one kind label: " + ", ".join(KINDS))
        elif title is not None and not title.startswith(KINDS[kind_labels[0]] + " "):
            errors.append(f"the title must start with \"{KINDS[kind_labels[0]]}\" to match the label")
        if len(review_labels) != 1:
            errors.append("it needs exactly one review label: " + ", ".join(REVIEW_LABELS))
    return errors


def main(argv):
    parser = argparse.ArgumentParser(description="Check a pull request description.")
    parser.add_argument("event", nargs="?", help="the GitHub event file")
    parser.add_argument("--body", help="a file with the description, instead of an event file")
    parser.add_argument("--title", help="with --body: the title to check")
    parser.add_argument("--labels", help="with --body: the labels to check, comma-separated")
    args = parser.parse_args(argv[1:])
    if bool(args.body) == bool(args.event):
        parser.print_help()
        return 2
    try:
        if args.body:
            body = Path(args.body).read_text(encoding="utf-8")
            title = args.title
            labels = args.labels.split(",") if args.labels is not None else None
        else:
            pull_request = json.loads(Path(args.event).read_text(encoding="utf-8")).get("pull_request", {})
            if pull_request.get("draft"):
                print("Draft pull request: its description is checked when it leaves draft")
                return 0
            if pull_request.get("user", {}).get("type") == "Bot":
                print("Opened by a GitHub App: not checked (docs/process/pull-requests.md)")
                return 0
            body = pull_request.get("body") or ""
            title = pull_request.get("title") or ""
            labels = [label["name"] for label in pull_request.get("labels", [])]
    except (OSError, ValueError) as error:
        print(f"Pull request description: can't read it: {error}")
        return 2
    errors = check(body, Path(__file__).resolve().parents[2], title, labels)
    for error in errors:
        print(f"Pull request description: {error}")
    if errors:
        print("Fill it in by .github/pull_request_template.md")
        return 1
    print("Pull request description check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
