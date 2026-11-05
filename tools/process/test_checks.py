"""Tests for the process checks. Run: python3 -m unittest discover -s tools/process -p "test_*.py"."""

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_commits  # noqa: E402
import check_docs  # noqa: E402
import check_lock  # noqa: E402
import check_owner  # noqa: E402
import check_pr  # noqa: E402
import doctor  # noqa: E402
import owned  # noqa: E402
import sync  # noqa: E402
import update  # noqa: E402

TEMPLATE = Path(__file__).resolve().parents[2] / ".github" / "pull_request_template.md"

BACKLOG = """\
# Backlog

- [x] **B-001** First.
  Depends on: nothing.
  Done when: it is done and checked.

- [ ] **B-002** Second.
  Depends on: B-001.
  Done when:
  - one thing is there;

  - and another one too.
"""

# A project's kinds of ID and coverage, as docs/process.json gives them: cases to requirements.
CONFIG = {
    "project": {"set_up": True, "owner_language": "English", "tracker": "none", "releases": "none",
                "agents_account": "own", "merged_by": "coordinator"},
    "ids": [
        {"kind": "case", "prefix": "C", "file": "docs/cases.md", "defined_by": "heading"},
        {"kind": "scenario", "prefix": "S", "file": "docs/scenarios.md", "defined_by": "heading"},
        {"kind": "step", "prefix": "S", "parts": 2, "file": "docs/walkthroughs.md", "defined_by": "heading"},
        {"kind": "feature", "prefix": "F", "dash": True, "digits": 3, "file": "docs/feature-map.md",
         "defined_by": "table"},
        {"kind": "fr", "prefix": "FR", "dash": True, "digits": 3, "file": "docs/requirements.md",
         "defined_by": "heading"},
        {"kind": "nfr", "prefix": "NFR", "dash": True, "digits": 3, "file": "docs/requirements.md",
         "defined_by": "heading"},
    ],
    "coverage": [
        {"kind": "case", "field": "Solved by", "refs": ["scenario"]},
        {"kind": "scenario", "children": "step"},
        {"kind": "step", "field": "Requirements", "refs": ["fr", "nfr"]},
        {"kind": "fr", "field": "Source", "refs": ["step", "feature"],
         "or_match": "cases\\.md#cross-cutting-needs|walkthroughs\\.md#open-questions-"},
        {"kind": "nfr", "field": "Source", "refs": ["step", "feature"],
         "or_match": "cases\\.md#cross-cutting-needs|walkthroughs\\.md#open-questions-"},
        {"kind": "feature", "field": "Requirements", "refs": ["fr", "nfr"], "or_starts": "out of scope"},
    ],
}

# Covered all the way: the coverage checks' good sample.
SPEC = {
    "docs/cases.md": "### C1. A case\n\nSolved by: S1 and S2.\n\n## Cross-cutting needs\n",
    "docs/scenarios.md": "### S1. First\n\n### S2. Second\n",
    "docs/walkthroughs.md": "## S1. First\n\n### S1.1 Start\n\nSteps S1.1-S1.1.\n\n- **Requirements:** FR-001.\n\n"
                            "## S2. Second\n\n### S2.1 Go on\n\n- **Requirements:** FR-001,\n  NFR-001.\n\n"
                            "## Open questions, part 1\n",
    "docs/feature-map.md": "| ID | Function | Requirements |\n|---|---|---|\n| F-001 | Run | FR-001 |\n"
                           "| F-002 | Lock | out of scope: not needed |\n\n"
                           "  | Plan | Price |\n  |---|---|\n  | Basic | 10 |\n",
    "docs/requirements.md": "### FR-001 Do it\n\n- **Source:** S1.1, F-001.\n\n"
                            "### NFR-001 Fast\n\n- **Source:** [a need](cases.md#cross-cutting-needs),\n"
                            "  [a question](walkthroughs.md#open-questions-part-1).\n",
}

GOOD_BODY = """\
## Backlog item

B-002 Second.

## What changed

The walkthroughs file.

## Behaviour change

None: only documents change.

## Why

Milestone two needs it.

## How it was checked

`python3 tools/process/check.py`: passed.

## Docs updated

None, nothing else changed.

## Owner review

Not needed: text for machines.

## Not done and open questions

None.
"""


def git_in(root, *args):
    """Runs git in root as a throwaway author; returns its output."""
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=root,
                          check=True, capture_output=True, text=True).stdout.strip()


def commit_files(root, files, message):
    """Writes files in the repository at root, commits everything, and returns the commit."""
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    git_in(root, "add", "-A")
    git_in(root, "commit", "-qm", message)
    return git_in(root, "rev-parse", "HEAD")


class Repo:
    """A throwaway repository with the given files, the backlog and the sample docs/process.json."""

    def __init__(self, files, config=CONFIG):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        files = {"docs/backlog.md": BACKLOG, "docs/process.json": json.dumps(config), **files}
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(text), encoding="utf-8")

    def __enter__(self):
        return self.root

    def __exit__(self, *exc):
        self.tmp.cleanup()


class DocsCheck(unittest.TestCase):
    def errors(self, files, config=CONFIG):
        with Repo(files, config) as root:
            return check_docs.check(root)

    def assertFound(self, text, errors):
        self.assertTrue(any(text in error for error in errors), errors)

    def test_good_repository_passes(self):
        files = {
            **SPEC,
            "docs/plan.md": "## How it goes\n\nSee [backlog](backlog.md), B-002, S2, `B-999` in code.\n\n"
                            "```\nB-998\n```\n\n[Here](#how-it-goes), [there](now.md#where-we-are).\n",
            "docs/now.md": "# Now\n\n## Where we are\n",
            "docs/decisions/README.md": "| [0001](0001-first-one.md) | First | accepted |\n",
            "docs/decisions/0001-first-one.md": "# 0001\n",
            "docs/design/page.html": '<a href="https://example.com">a link</a><script src="app.js"></script>\n',
        }
        self.assertEqual(self.errors(files), [])

    def test_no_kinds_of_its_own_leaves_other_prefixes_alone(self):
        files = {"docs/plan.md": "Talk to AWS S3, see RFC 7231 and C4 models; do B-002.\n"}
        self.assertEqual(self.errors(files, config={"ids": [], "coverage": []}), [])

    def test_ignored_files_are_not_checked_for_ids(self):
        files = {"docs/audit/2026.md": "Severity S1 to S4, see FR-999.\n"}
        config = {**CONFIG, "ids_ignore": ["docs/audit/*.md"]}
        self.assertEqual(self.errors(files, config), [])
        self.assertFound("write it as code", self.errors(files))

    def test_ids_in_the_process_folder_are_not_checked(self):
        files = {"docs/process/config.md": "For example S7 and FR-999.\n"}
        self.assertEqual(self.errors(files), [])

    def test_unreadable_documents_give_a_message(self):
        with Repo({}) as root:
            (root / "docs/legacy.md").write_bytes(b"\xff\xfe old text")
            self.assertFound("not UTF-8", check_docs.check(root))
        config = {**CONFIG, "ids": CONFIG["ids"] + [{"kind": "x", "prefix": "X", "file": "docs", "defined_by": "heading"}]}
        self.assertFound("can't read", self.errors({}, config))
        self.assertFound("unknown kind", self.errors({}, {"coverage": [{"kind": ["backlog"], "children": "backlog"}]}))

    def test_invalid_config_fails(self):
        with Repo({}) as root:
            (root / "docs/process.json").write_text("{not json", encoding="utf-8")
            self.assertFound("not valid JSON", check_docs.check(root))

    def test_missing_link_target_fails(self):
        self.assertFound("missing file", self.errors({"docs/plan.md": "See [this](nowhere.md).\n"}))

    def test_heading_with_inline_code_keeps_it_in_the_anchor(self):
        now = "# Now\n\n## Breaks on `a.b`\n"
        good = self.errors({"docs/plan.md": "See [it](now.md#breaks-on-ab).\n", "docs/now.md": now})
        self.assertEqual(good, [])
        bad = self.errors({"docs/plan.md": "See [it](now.md#breaks-on-).\n", "docs/now.md": now})
        self.assertFound("missing heading", bad)

    def test_files_git_ignores_are_skipped(self):
        stray = {".gitignore": "vendor/\n", "vendor/lib/README.md": "See [this](nowhere.md) and B-999.\n"}
        with Repo(stray) as root:
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            self.assertEqual(check_docs.check(root), [])

    def test_missing_heading_fails(self):
        files = {"docs/plan.md": "See [this](now.md#gone).\n", "docs/now.md": "# Now\n"}
        self.assertFound("missing heading", self.errors(files))

    def test_undefined_id_fails(self):
        errors = self.errors({"docs/plan.md": "Do B-003 and FR-007, see S4, C3 and F-002.\n"})
        for item_id in ("B-003", "FR-007", "S4", "C3", "F-002"):
            self.assertFound(f"{item_id} is defined nowhere", errors)

    def test_range_of_steps_is_checked_whole(self):
        files = {"docs/scenarios.md": "### S1. First\n", "docs/plan.md": "Steps S1.1-S1.5.\n"}
        errors = self.errors(files)
        self.assertFound("S1.1 is defined nowhere", errors)
        self.assertFound("S1.5 is defined nowhere", errors)

    def test_malformed_id_fails(self):
        errors = self.errors({"docs/plan.md": "See FR-0001, NFR-12, B-7 and S1.2.3.\n"})
        for item_id in ("FR-0001", "NFR-12", "B-7", "S1.2.3"):
            self.assertFound(f"{item_id} is not a valid ID", errors)

    def test_duplicate_id_fails(self):
        errors = self.errors({"docs/requirements.md": "### FR-001 One\n\n### FR-001 Again\n"})
        self.assertFound("already defined", errors)

    def test_backlog_item_without_done_when_fails(self):
        backlog = BACKLOG + "\n- [ ] **B-003** Third.\n  Depends on: nothing.\n"
        self.assertFound("B-003 has no \"Done when\"", self.errors({"docs/backlog.md": backlog}))

    def test_backlog_item_with_empty_done_when_fails(self):
        backlog = BACKLOG + "\n- [ ] **B-003** Third.\n  Depends on: nothing.\n  Done when:\n"
        self.assertFound("B-003 has an empty \"Done when\"", self.errors({"docs/backlog.md": backlog}))

    def test_depends_on_only_in_title_fails(self):
        backlog = BACKLOG + "\n- [ ] **B-003** Depends on nothing.\n  Done when: it is all there.\n"
        self.assertFound("B-003 has no \"Depends on\"", self.errors({"docs/backlog.md": backlog}))

    def test_backlog_item_titled_with_code_is_defined(self):
        backlog = BACKLOG + "\n- [ ] **B-003** `tool check` runs.\n  Depends on: nothing.\n  Done when: the command runs and passes.\n"
        files = {"docs/backlog.md": backlog, "docs/plan.md": "Then B-003.\n"}
        self.assertEqual(self.errors(files), [])

    def test_backlog_item_in_wrong_form_fails(self):
        errors = self.errors({"docs/backlog.md": BACKLOG + "\n  - [ ] B-003 Third.\n"})
        self.assertFound("must be a top-level", errors)

    def test_decision_not_listed_fails(self):
        files = {"docs/decisions/README.md": "# Decisions\n", "docs/decisions/0001-first-one.md": "# 0001\n"}
        self.assertFound("not listed", self.errors(files))

    def test_decision_number_taken_twice_fails(self):
        files = {
            "docs/decisions/README.md": "[a](0001-one.md) [b](0001-two.md)\n",
            "docs/decisions/0001-one.md": "# 0001\n",
            "docs/decisions/0001-two.md": "# 0001\n",
        }
        self.assertFound("is taken by", self.errors(files))

    def test_case_without_scenario_fails(self):
        cases = SPEC["docs/cases.md"].replace("Solved by: S1 and S2.", "Solved by: nothing yet.")
        self.assertFound("C1 names no scenario", self.errors({**SPEC, "docs/cases.md": cases}))

    def test_scenario_without_children_fails(self):
        scenarios = SPEC["docs/scenarios.md"] + "\n### S3. Third\n"
        self.assertFound("S3 has no step", self.errors({**SPEC, "docs/scenarios.md": scenarios}))

    def test_step_without_requirement_fails(self):
        for requirements in ("", "- **Requirements:** none yet.\n"):
            with self.subTest(requirements=requirements):
                walkthroughs = SPEC["docs/walkthroughs.md"].replace("- **Requirements:** FR-001.\n", requirements)
                errors = self.errors({**SPEC, "docs/walkthroughs.md": walkthroughs})
                self.assertFound("S1.1 names no fr or nfr", errors)

    def test_requirement_without_source_fails(self):
        for source in ("", "- **Source:** the owner said so.\n"):
            with self.subTest(source=source):
                requirements = SPEC["docs/requirements.md"].replace("- **Source:** S1.1, F-001.\n", source)
                errors = self.errors({**SPEC, "docs/requirements.md": requirements})
                self.assertFound("FR-001 names no step or feature", errors)

    def test_table_row_without_id_fails(self):
        feature_map = SPEC["docs/feature-map.md"].replace("| F-001 | Run |", "|  | Run |")
        self.assertFound("a row has no ID", self.errors({**SPEC, "docs/feature-map.md": feature_map}))

    def test_table_row_without_requirement_fails(self):
        feature_map = SPEC["docs/feature-map.md"].replace("| Run | FR-001 |", "| Run | — |")
        errors = self.errors({**SPEC, "docs/feature-map.md": feature_map})
        self.assertFound("F-001 names no fr or nfr", errors)

    def test_rule_with_unknown_kind_fails(self):
        config = {**CONFIG, "coverage": [{"kind": "nothing", "children": "step"}]}
        self.assertFound("unknown kind", self.errors(SPEC, config))

    def test_bad_config_is_reported_not_raised(self):
        for config, text in [
            ({"ids": [{"kind": "x", "prefix": "X"}]}, "lacks file, defined_by"),
            ({"ids": [{"kind": "x", "prefix": "X", "file": "a.md", "defined_by": "list"}]}, "heading or table"),
            ({"ids": [{"kind": "x", "prefix": "x1", "file": "a.md", "defined_by": "heading"}]}, "capital letters"),
            ({"coverage": [{"kind": "backlog"}]}, "either children or field"),
            ({"coverage": [{"kind": "backlog", "field": "F", "refs": ["nothing"]}]}, "unknown kind"),
            ([], "must be an object"),
            ({"coverage": ["x"]}, "coverage[0] must be an object"),
            ({"coverage": [{"kind": "backlog", "field": "F", "refs": ["backlog"], "or_match": "("}]},
             "not a valid regular expression"),
            ({"coverage": [{"kind": "backlog", "field": "F", "refs": "backlog"}]}, "refs must be a list"),
            ({"ids": [{"kind": "x", "prefix": "X", "file": "a.md", "defined_by": "heading", "parts": 0}]},
             "parts must be"),
            ({"ids": [{"kind": "x", "prefix": "X", "file": "a.md", "defined_by": "heading", "digits": "x"}]},
             "digits must be"),
            ({"checks": "echo"}, "checks must be a list"),
            ({"project": None}, "project must be an object"),
            ({"project": {**CONFIG["project"], "owner_language": ""}}, "owner_language must be set"),
            ({"project": {**CONFIG["project"], "tracker": ""}}, "tracker must be set"),
            ({"project": {**CONFIG["project"], "releases": ""}}, "releases must be set"),
            ({"project": {**CONFIG["project"], "merged_by": ""}}, "merged_by must be set"),
            ({"project": {**CONFIG["project"], "agents_account": "bot"}}, "agents_account must be own or owner"),
            ({"ids_ignore": "docs/a.md"}, "ids_ignore must be a list"),
            ({"commits": {"one_line": "yes"}}, "commits must be an object of true or false"),
            ({"commits": {"signed": True}}, "knows only one_line, no_co_authors and conventional"),
            ({"ids": [{"kind": "x", "prefix": "X", "file": "a.md", "defined_by": "heading"},
                      {"kind": "x", "prefix": "Y", "file": "b.md", "defined_by": "heading"}]}, "named twice"),
        ]:
            with self.subTest(text=text):
                self.assertFound(text, self.errors({}, config))


class PullRequestCheck(unittest.TestCase):
    def errors(self, body):
        with Repo({}) as root:
            return check_pr.check(body, root)

    def test_filled_description_passes(self):
        self.assertEqual(self.errors(GOOD_BODY), [])

    def test_pull_requests_that_are_no_item_pass(self):
        for text in ("Coordinator record: the owner's decision of Oct 19.", "Setup", "Setup of the project.",
                     "Process update: 0.1.0 to 0.2.0.", "Process change: reviews in one comment."):
            with self.subTest(text=text):
                self.assertEqual(self.errors(GOOD_BODY.replace("B-002 Second.", text)), [])

    def test_behaviour_change_needs_a_reason_or_steps(self):
        for text, error in [
            ("Maybe.", "must start with \"None\" or \"Yes\""),
            ("None", "must say why"),
            ("Yes: the export works.", "at least three steps"),
            ("Yes:\n\n- open it\n- export", "at least three steps"),
        ]:
            with self.subTest(text=text):
                body = GOOD_BODY.replace("None: only documents change.", text)
                self.assertTrue(any(error in e for e in self.errors(body)), self.errors(body))

    def test_behaviour_change_with_steps_passes(self):
        body = GOOD_BODY.replace("None: only documents change.", "Yes:\n\n1. Open it.\n2. Export.\n3. See the file.")
        self.assertEqual(self.errors(body), [])

    def test_template_left_unfilled_fails(self):
        errors = self.errors(TEMPLATE.read_text())
        self.assertEqual(len([e for e in errors if "is empty" in e]), len(check_pr.SECTIONS), errors)

    def test_required_checks_are_the_workflows_jobs(self):
        jobs = []
        for workflow in (TEMPLATE.parents[1] / ".github/workflows").glob("process-*.yml"):
            jobs += re.findall(r"^  (process-[a-z]+):", workflow.read_text(encoding="utf-8"), re.MULTILINE)
        self.assertEqual(sorted(jobs), sorted(doctor.REQUIRED_CHECKS))

    def test_template_and_check_agree(self):
        self.assertEqual(list(check_pr.sections(TEMPLATE.read_text())), check_pr.SECTIONS)

    def test_missing_section_fails(self):
        body = GOOD_BODY.replace("## Why\n\nMilestone two needs it.\n", "")
        self.assertIn("section \"Why\" is missing", self.errors(body))

    def test_section_with_next_to_nothing_fails(self):
        body = GOOD_BODY.replace("Milestone two needs it.", "-")
        self.assertIn("section \"Why\" says next to nothing", self.errors(body))

    def test_unknown_backlog_item_fails(self):
        body = GOOD_BODY.replace("B-002 Second.", "B-042 Something.")
        self.assertIn("\"Backlog item\": B-042 is not in docs/backlog.md", self.errors(body))

    def test_two_backlog_items_fail(self):
        body = GOOD_BODY.replace("B-002 Second.", "B-001 and B-002.")
        self.assertTrue(any("belongs to one" in error for error in self.errors(body)))

    def test_a_coordinator_record_may_name_several_items_that_exist(self):
        body = GOOD_BODY.replace("B-002 Second.", "Coordinator record: adds B-001 and B-002.")
        self.assertEqual(self.errors(body), [])
        body = GOOD_BODY.replace("B-002 Second.", "Coordinator record: adds B-001 and B-042.")
        self.assertEqual(self.errors(body), ["\"Backlog item\": B-042 is not in docs/backlog.md"])

    def test_nothing_open_may_say_a_bare_none(self):
        for text in ("None", "none."):
            with self.subTest(text=text):
                self.assertEqual(self.errors(GOOD_BODY.replace("open questions\n\nNone.", "open questions\n\n" + text)), [])
        body = GOOD_BODY.replace("Milestone two needs it.", "None.")
        self.assertIn("section \"Why\" says next to nothing", self.errors(body))

    def meta(self, title, labels):
        with Repo({}) as root:
            return check_pr.check(GOOD_BODY, root, title, labels)

    def test_title_and_labels_that_agree_pass(self):
        self.assertEqual(self.meta("Spec: walkthroughs", ["spec", "ok-without-reading"]), [])

    def test_title_without_kind_fails(self):
        self.assertTrue(any("title must start" in e for e in self.meta("Walkthroughs", ["spec", "ok-without-reading"])))

    def test_title_not_matching_label_fails(self):
        self.assertTrue(any("to match the label" in e for e in self.meta("Code: walkthroughs", ["spec", "ok-without-reading"])))

    def test_missing_or_double_labels_fail(self):
        self.assertTrue(any("one kind label" in e for e in self.meta("Spec: x y", ["ok-without-reading"])))
        self.assertTrue(any("one kind label" in e for e in self.meta("Spec: x y", ["spec", "code", "ok-without-reading"])))
        self.assertTrue(any("one review label" in e for e in self.meta("Spec: x y", ["spec"])))

    def test_owner_review_with_next_to_nothing_fails(self):
        body = GOOD_BODY.replace("Not needed: text for machines.", "No.")
        self.assertIn("section \"Owner review\" says next to nothing", self.errors(body))


class PullRequestEvent(unittest.TestCase):
    def run_check(self, pull_request, *more):
        with tempfile.TemporaryDirectory() as tmp:
            event = Path(tmp) / "event.json"
            event.write_text(json.dumps({"pull_request": pull_request}), encoding="utf-8")
            script = Path(__file__).resolve().parent / "check_pr.py"
            env = {key: value for key, value in os.environ.items() if key not in ("GH_TOKEN", "GITHUB_RUN_ID")}
            return subprocess.run([sys.executable, str(script), str(event), *more], capture_output=True, text=True,
                                  env=env)

    def test_draft_is_not_checked(self):
        result = self.run_check({"draft": True, "body": "Plan and questions.", "title": "x", "labels": []})
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_ready_pull_request_is_checked(self):
        result = self.run_check({"draft": False, "body": "Plan and questions.", "title": "x", "labels": []})
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_github_app_is_not_checked_but_a_user_is(self):
        pull_request = {"draft": False, "body": "Release 1.2.0", "title": "chore: release", "labels": [],
                        "user": {"type": "Bot"}}
        self.assertEqual(self.run_check(pull_request).returncode, 0)
        self.assertEqual(self.run_check({**pull_request, "user": {"type": "User"}}).returncode, 1)

    def test_in_ci_the_pull_request_is_read_now_and_red_runs_are_run_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            event = Path(tmp) / "event.json"
            event.write_text(json.dumps({"pull_request": {"number": 5, "draft": False, "title": "Plan: x", "body": "",
                                                          "labels": []},
                                         "repository": {"full_name": "someone/project"}}))
            now = {"number": 5, "draft": False, "title": "Plan: the work", "body": GOOD_BODY,
                   "labels": [{"name": "plan"}, {"name": "ok-without-reading"}], "user": {"type": "User"},
                   "head": {"sha": "h"}}
            reran = []
            saved = check_owner.api, check_owner.rerun_red, check_pr.check
            check_owner.api = lambda path, method="GET": now
            check_owner.rerun_red = lambda repo, head, run, workflow: reran.append((head, run, workflow))
            check_pr.check = lambda body, root, title, labels: [] if labels == ["plan", "ok-without-reading"] else ["x"]
            try:
                with mock.patch.dict("os.environ", {"GH_TOKEN": "t", "GITHUB_RUN_ID": "9"}):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(check_pr.main(["check_pr.py", str(event)]), 0)
            finally:
                check_owner.api, check_owner.rerun_red, check_pr.check = saved
            self.assertEqual(reran, [("h", "9", "process-pr.yml")])

    def test_body_and_event_together_are_refused(self):
        result = self.run_check({"draft": False}, "--body", "x.md")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class OwnerCheck(unittest.TestCase):
    HEAD = "abc123"

    def errors(self, labels, changed=("src/app.py",), account="own", reviews=()):
        return check_owner.check(labels, list(changed), account, list(reviews), self.HEAD, "agents")

    def review(self, state, login="owner", commit=HEAD, association="OWNER"):
        return {"user": {"login": login}, "state": state, "commit_id": commit, "author_association": association}

    def test_ok_without_reading_needs_no_approval(self):
        self.assertEqual(self.errors(["code", "ok-without-reading"]), [])

    def test_owner_review_needs_an_approval_of_the_last_commit(self):
        self.assertEqual(len(self.errors(["code", "owner-review"])), 1)
        self.assertEqual(self.errors(["code", "owner-review"], reviews=[self.review("APPROVED")]), [])
        self.assertEqual(len(self.errors(["code", "owner-review"],
                                         reviews=[self.review("APPROVED", commit="older")])), 1)

    def test_no_review_label_needs_an_approval(self):
        self.assertEqual(len(self.errors([])), 1)

    def test_a_later_review_withdraws_the_approval_and_comments_dont(self):
        approved = self.review("APPROVED")
        self.assertEqual(len(self.errors(["owner-review"], reviews=[approved, self.review("CHANGES_REQUESTED")])), 1)
        self.assertEqual(len(self.errors(["owner-review"], reviews=[approved, self.review("DISMISSED")])), 1)
        self.assertEqual(self.errors(["owner-review"], reviews=[approved, self.review("COMMENTED")]), [])

    def test_the_author_cant_approve(self):
        self.assertEqual(len(self.errors(["owner-review"], reviews=[self.review("APPROVED", login="agents")])), 1)

    def test_only_the_owner_can_approve(self):
        for association in ("NONE", "COLLABORATOR", "MEMBER"):
            with self.subTest(association=association):
                other = self.review("APPROVED", login="someone", association=association)
                self.assertEqual(len(self.errors(["owner-review"], reviews=[other])), 1)

    def test_a_moved_file_counts_at_its_old_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=root,
                                      check=True, capture_output=True, text=True).stdout.strip()
            git("init", "-q")
            (root / "docs").mkdir()
            (root / "docs/plan.md").write_text("# Plan\n\nThe contract, long enough to be seen as moved.\n")
            git("add", "-A")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            git("mv", "docs/plan.md", "docs/old-plan.md")
            git("commit", "-qm", "move")
            original, check_owner.ROOT = check_owner.ROOT, root
            try:
                changed = check_owner.changed_files(base, git("rev-parse", "HEAD"))
            finally:
                check_owner.ROOT = original
        self.assertEqual(sorted(changed), ["docs/old-plan.md", "docs/plan.md"])

    def test_what_the_owner_keeps_needs_owner_review(self):
        for name in ("CLAUDE.md", "docs/plan.md", "docs/process.json", ".process-lock.json",
                     ".github/workflows/project-checks.yml",
                     "docs/process/rules.md", "tools/process/check.py",
                     ".claude/settings.json", "firmware/.claude/agents/flash.md", ".mcp.json", "CLAUDE.local.md",
                     "firmware/CLAUDE.md", ".claude", "firmware/.claude",
                     "src/claude.md", ".Claude/settings.json", "docs/Claude.md", ".MCP.json", "Docs/Plan.md"):
            with self.subTest(name=name):
                errors = self.errors(["plan", "ok-without-reading"], changed=[name])
                self.assertEqual(len(errors), 2, errors)
                self.assertIn("owner-review", errors[0])
        self.assertEqual(self.errors(["code", "ok-without-reading"],
                                     changed=["docs/now.md", "docs/backlog.md", "src/claude.txt", ".mcp.json.bak",
                                              "src/.claude-notes.md"]), [])


    def test_links_and_submodules_where_the_owner_keeps_paths_never_go_in(self):
        link, submodule = check_owner.LINK, check_owner.SUBMODULE
        kept = ["src/payments/*", "*/secrets/*"]
        trees = [("100644", "x", "Firmware/CLAUDE.md"), ("100644", "x", "boards/x/.claude/settings.json")]
        def errors(mode, path):
            return check_owner.link_errors([(mode, "x", path)], kept, trees)
        for mode, path in ((link, ".claude"), (link, ".Claude"), (link, "firmware/.claude"),
                           (link, "CLAUDE.md"), (link, "src/claude.local.md"), (submodule, ".claude"),
                           (link, "docs"), (link, "tools/process"), (link, ".github"), (submodule, "src"),
                           (link, "app/secrets"), (link, "firmware"), (link, "boards"), (link, "boards/x")):
            with self.subTest(mode=mode, path=path):
                found = errors(mode, path)
                self.assertEqual(len(found), 1, found)
                self.assertIn("not even with the owner's approval", found[0])
        self.assertIn("@AGENTS.md", errors(link, "CLAUDE.md")[0])
        self.assertNotIn("@AGENTS.md", errors(link, ".claude")[0])
        for mode, path in ((link, "web/assets/logo.svg"), (link, "docs-old"), (submodule, "vendor/lib"),
                           (link, "config"), (link, "app")):
            with self.subTest(mode=mode, path=path):
                self.assertEqual(errors(mode, path), [])
        self.assertEqual(check_owner.link_errors([("100644", "x", ".claude")]), [])  # a plain file

    def test_rules_may_import_only_plain_files_the_owner_keeps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git_in(root, "init", "-q")
            (root / "firmware").mkdir()
            (root / "firmware/CLAUDE.md").write_bytes(b"Rules \xff\0 see @notes.md\n")
            (root / "notes2.md").symlink_to("src/whatever.md")
            (root / "lib").symlink_to("src")
            head = commit_files(root, {
                "CLAUDE.md": "Read @AGENTS.md and @.claude/rules/style.md. Mail me@example.com. See @missing.md.\n"
                             "Also @notes2.md, @lib/rules.md and @vendor/sdk/RULES.md.\n",
                "AGENTS.md": "See @docs/more.md\n",
                ".claude/rules/style.md": "@docs/rules.md\n",
                ".claude/commands/deploy.md": "Deploy @src/app.py\n",  # not loaded as rules
                "docs/plan.md": "The plan, see @src/app.py\n",  # kept, but not loaded as rules
                "docs/more.md": "More.\n", "docs/rules.md": "Rules.\n", "firmware/notes.md": "Notes.\n",
                "src/app.py": "print()\n", "src/whatever.md": "Agent rules.\n", "src/rules.md": "Agent rules.\n"},
                "imports")
            git_in(root, "update-index", "--add", "--cacheinfo", f"160000,{head},vendor/sdk")
            git_in(root, "commit", "-qm", "submodule")
            saved, check_owner.ROOT = check_owner.ROOT, root
            try:
                entries = check_owner.tree(git_in(root, "rev-parse", "HEAD"))
                unkept = check_owner.import_errors(entries)
                kept = check_owner.import_errors(entries, ["AGENTS.md", "docs/rules.md", "firmware/notes.md"])
            finally:
                check_owner.ROOT = saved
        def short(errors):
            return [error.split(", which")[0].split(":")[0] for error in errors]
        links = ["CLAUDE.md imports lib/rules.md through the symlink lib",
                 "CLAUDE.md imports notes2.md through the symlink notes2.md",
                 "CLAUDE.md imports vendor/sdk/RULES.md through the submodule vendor/sdk"]
        self.assertEqual(short(unkept), [".claude/rules/style.md imports docs/rules.md", "CLAUDE.md imports AGENTS.md",
                                         *links, "firmware/CLAUDE.md imports firmware/notes.md"])
        self.assertIn("add it to \"kept\" in docs/process.json or move it under .claude/", unkept[0])
        self.assertEqual(short(kept), ["AGENTS.md imports docs/more.md", *links])


    def owner_check(self, head_tree, changed, labels, reviews, head_kept=(), text=""):
        """check_owner.main on a pull request with these head tree entries, changed paths, labels and
        reviews, docs/process.json's "kept" empty on the base and head_kept on the head."""
        with tempfile.TemporaryDirectory() as tmp:
            event = Path(tmp) / "event.json"
            event.write_text(json.dumps({"pull_request": {"number": 7, "base": {"sha": "b"}, "head": {"sha": self.HEAD},
                                                          "user": {"login": "agents"}},
                                         "repository": {"full_name": "someone/project"}}))
            with mock.patch.multiple(
                    check_owner, tree=lambda commit: head_tree if commit == self.HEAD else [],
                    changed_files=lambda base, head: changed, agents_account=lambda *args: "own",
                    kept_patterns=lambda commit: list(head_kept) if commit == self.HEAD else [],
                    text_of=lambda object_id: text, released_files=lambda *args: set(),
                    labels=lambda repo, number: labels, reviews=lambda repo, number: reviews), \
                    mock.patch.dict("os.environ", {}, clear=False), contextlib.redirect_stdout(io.StringIO()):
                os.environ.pop("GITHUB_RUN_ID", None)
                return check_owner.main(["check_owner.py", str(event)])

    def test_a_submodule_elsewhere_is_like_any_other_path(self):
        head_tree = [("100644", "x", "src/app.py"), (check_owner.SUBMODULE, "x", "vendor/lib")]
        for changed in (["src/app.py"], ["vendor/lib"]):
            with self.subTest(changed=changed):
                self.assertEqual(self.owner_check(head_tree, changed, ["code", "ok-without-reading"], []), 0)

    def test_the_owners_approval_doesnt_let_a_link_in(self):
        approved = [self.review("APPROVED")]
        self.assertEqual(self.owner_check([], [".claude"], ["plan", "owner-review"], approved), 0)
        self.assertEqual(self.owner_check([(check_owner.LINK, "x", ".claude")], [".claude"],
                                          ["plan", "owner-review"], approved), 1)

    def test_an_import_goes_in_once_the_pull_request_keeps_it(self):
        head_tree = [("100644", "x", "CLAUDE.md"), ("100644", "y", "AGENTS.md")]
        approved = [self.review("APPROVED")]
        args = (head_tree, ["CLAUDE.md", "docs/process.json"], ["plan", "owner-review"], approved)
        self.assertEqual(self.owner_check(*args, text="@AGENTS.md\n"), 1)
        self.assertEqual(self.owner_check(*args, head_kept=["AGENTS.md"], text="@AGENTS.md\n"), 0)

    def test_symlinks_and_submodules_are_read_from_the_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git_in(root, "init", "-q")
            (root / "agentstuff").mkdir()
            (root / ".claude").symlink_to("agentstuff")
            (root / "logo.svg").symlink_to("agentstuff/settings.json")
            commit_files(root, {"agentstuff/settings.json": "{}\n"}, "files")
            git_in(root, "update-index", "--add", "--cacheinfo", "160000," + git_in(root, "rev-parse", "HEAD") + ",vendor/lib")
            git_in(root, "commit", "-qm", "submodule")
            saved, check_owner.ROOT = check_owner.ROOT, root
            try:
                entries = check_owner.tree(git_in(root, "rev-parse", "HEAD"))
            finally:
                check_owner.ROOT = saved
        self.assertEqual(sorted((mode, path) for mode, _, path in entries),
                         [("100644", "agentstuff/settings.json"), ("120000", ".claude"), ("120000", "logo.svg"),
                          ("160000", "vendor/lib")])
        self.assertEqual(len(check_owner.link_errors(entries, trees=entries)), 1)

    def test_the_paths_the_settings_keep_need_owner_review(self):
        kept = ["package.json", "src/payments/*", "*.toml"]
        for name, needs_owner in (("package.json", True), ("src/payments/charge/card.py", True),
                                  ("ruff.toml", True), ("src/app.py", False), ("web/package.json", False)):
            with self.subTest(name=name):
                errors = check_owner.check(["code", "ok-without-reading"], [name], "own", [], self.HEAD, "agents",
                                           kept=kept)
                self.assertEqual(bool(errors), needs_owner, errors)

    def test_the_settings_come_from_the_base_and_owner_only_from_the_owner(self):
        def config(account, kept):
            return json.dumps({"project": {"agents_account": account}, "kept": kept})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git_in(root, "init", "-q")
            empty = commit_files(root, {"docs/process.json": config("", ["package.json"])}, "template")
            owner = commit_files(root, {"docs/process.json": config("owner", [])}, "setup")
            own = commit_files(root, {"docs/process.json": config("own", "not a list")}, "own")
            saved, check_owner.ROOT = check_owner.ROOT, root
            try:
                self.assertEqual(check_owner.kept_patterns(empty), ["package.json"])
                self.assertEqual(check_owner.kept_patterns(own), [])
                self.assertEqual(check_owner.agents_account(empty, owner, "Someone", "someone"), "owner")
                self.assertEqual(check_owner.agents_account(empty, owner, "agents", "someone"), "own")
                self.assertEqual(check_owner.agents_account(empty, owner, "agents", None), "owner")
                self.assertEqual(check_owner.agents_account(owner, own, "agents", "someone"), "owner")
                self.assertEqual(check_owner.agents_account(empty, empty), "own")
            finally:
                check_owner.ROOT = saved

    def test_released_files_need_no_approval_and_the_rest_counts_as_usual(self):
        changed = ["docs/process/rules.md", ".process-lock.json", "docs/backlog.md"]
        def errors(changed, released):
            return check_owner.check(["plan", "ok-without-reading"], changed, "own", [], self.HEAD, "agents",
                                     released=released)
        released = {"docs/process/rules.md", ".process-lock.json"}
        self.assertEqual(errors(changed, released), [])
        self.assertEqual(len(errors(changed, set())), 2)
        self.assertEqual(len(errors(changed, {"docs/process/rules.md"})), 2)
        self.assertEqual(len(errors(changed + ["docs/plan.md"], released)), 2)

    def test_release_copy_compares_with_the_templates_tag_on_its_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            template, project = Path(tmp) / "someone" / "template", Path(tmp) / "project"
            template.mkdir(parents=True)
            project.mkdir()
            git_in(template, "init", "-q", "-b", "main")
            def lock(template, version):
                return json.dumps({"template": template, "version": version})
            commit_files(template, {"docs/process/rules.md": "Old rules.\n",
                                    ".process-lock.json": lock("someone/template", "0.4.0")}, "old release")
            git_in(template, "tag", "v0.4.0")
            commit_files(template, {"docs/process/rules.md": "New rules.\n",
                                    ".process-lock.json": lock("someone/template", "0.5.0")}, "release")
            git_in(template, "tag", "v0.5.0")
            git_in(template, "checkout", "-q", "-b", "trial")
            commit_files(template, {"docs/process/rules.md": "Untried rules.\n",
                                    ".process-lock.json": lock("someone/template", "0.6.0")}, "not merged")
            git_in(template, "tag", "v0.6.0")
            fork = Path(tmp) / "agent" / "fork"
            fork.mkdir(parents=True)
            git_in(fork, "init", "-q", "-b", "main")
            commit_files(fork, {"docs/process/rules.md": "Loosened rules.\n"}, "fork")
            git_in(fork, "tag", "v0.5.0")
            git_in(project, "init", "-q")
            base = commit_files(project, {"docs/process/rules.md": "Old rules.\n",
                                          ".process-lock.json": lock("someone/template", "0.4.0")}, "base")
            faithful = commit_files(project, {"docs/process/rules.md": "New rules.\n",
                                              ".process-lock.json": lock("someone/template", "0.5.0")}, "update")
            changed = ["docs/process/rules.md", ".process-lock.json"]
            edited = commit_files(project, {"docs/process/rules.md": "New rules, loosened.\n"}, "edit")
            forked = commit_files(project, {"docs/process/rules.md": "Loosened rules.\n",
                                            ".process-lock.json": lock("agent/fork", "0.5.0")}, "fork")
            untried = commit_files(project, {"docs/process/rules.md": "Untried rules.\n",
                                             ".process-lock.json": lock("someone/template", "0.6.0")}, "trial")
            back = commit_files(project, {"docs/process/rules.md": "Old rules.\n",
                                          ".process-lock.json": lock("someone/template", "0.4.0")}, "back")
            saved = check_owner.ROOT, owned.TEMPLATE_SOURCE
            check_owner.ROOT, owned.TEMPLATE_SOURCE = project, str(Path(tmp)) + "/{}"
            try:
                released = check_owner.released_files
                self.assertEqual(released(changed, base, faithful, "someone/project"),
                                 {"docs/process/rules.md", ".process-lock.json"})
                self.assertEqual(released(changed, base, edited, "someone/project"), {".process-lock.json"})
                self.assertEqual(released(changed, base, forked, "someone/project"), set())
                self.assertEqual(released(changed, base, faithful, "someone/template"), set())
                self.assertEqual(released(changed, base, untried, "someone/project"), set())  # tag off main
                self.assertEqual(released(changed, faithful, back, "someone/project"), set())  # going back
            finally:
                check_owner.ROOT, owned.TEMPLATE_SOURCE = saved


    def test_a_passing_run_runs_again_the_other_red_runs(self):
        calls = []
        def api(path, method="GET"):
            calls.append((method, path))
            if method == "GET":
                return {"workflow_runs": [{"id": 1}, {"id": 2}, {"id": 3}]}
            if path.endswith("/1/rerun"):
                raise OSError("already running")
            return None
        saved, check_owner.api = check_owner.api, api
        try:
            check_owner.rerun_red("someone/project", self.HEAD, "2")
            check_owner.rerun_red("someone/project", self.HEAD, "2", "process-pr.yml")
        finally:
            check_owner.api = saved
        self.assertEqual([path for method, path in calls if method == "POST"][:2],
                         ["repos/someone/project/actions/runs/1/rerun", "repos/someone/project/actions/runs/3/rerun"])
        self.assertEqual([path.split("?")[0] for method, path in calls if method == "GET"],
                         ["repos/someone/project/actions/workflows/process-owner.yml/runs",
                          "repos/someone/project/actions/workflows/process-pr.yml/runs"])

    def test_rerunning_never_fails_the_check(self):
        def api(path, method="GET"):
            raise OSError("no access")
        saved, check_owner.api = check_owner.api, api
        try:
            check_owner.rerun_red("someone/project", self.HEAD, "2")  # no exception
        finally:
            check_owner.api = saved

    def test_only_a_passing_run_in_ci_runs_others_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            event = Path(tmp) / "event.json"
            event.write_text(json.dumps({"pull_request": {"number": 7, "base": {"sha": "b"}, "head": {"sha": "h"},
                                                          "user": {"login": "agents"}},
                                         "repository": {"full_name": "someone/project"}}))
            saved = {name: getattr(check_owner, name) for name in
                     ("changed_files", "agents_account", "labels", "reviews", "released_files", "rerun_red",
                      "kept_patterns", "tree")}
            reran = []
            check_owner.changed_files = lambda base, head: ["src/app.py"]
            check_owner.agents_account = lambda base, head, author, owner: "own"
            check_owner.kept_patterns = lambda base: []
            check_owner.tree = lambda commit: []
            check_owner.reviews = lambda repo, number: []
            check_owner.released_files = lambda changed, base, head, repo: set()
            check_owner.rerun_red = lambda repo, head, run: reran.append(run)
            try:
                for labels, run_id, expected in ((["code", "ok-without-reading"], "9", ["9"]),
                                                 (["code", "owner-review"], "9", []),
                                                 (["code", "ok-without-reading"], None, [])):
                    reran.clear()
                    check_owner.labels = lambda repo, number, labels=labels: labels
                    with mock.patch.dict("os.environ", {"GITHUB_RUN_ID": run_id} if run_id else {}, clear=False):
                        if not run_id:
                            os.environ.pop("GITHUB_RUN_ID", None)
                        with contextlib.redirect_stdout(io.StringIO()):
                            check_owner.main(["check_owner.py", str(event)])
                    self.assertEqual(reran, expected, (labels, run_id))
            finally:
                for name, value in saved.items():
                    setattr(check_owner, name, value)

    def test_with_the_owners_account_only_the_label_is_checked(self):
        self.assertEqual(self.errors(["owner-review"], account="owner"), [])
        self.assertEqual(len(self.errors(["ok-without-reading"], changed=["docs/plan.md"], account="owner")), 1)


class CommitsCheck(unittest.TestCase):
    STRICT = {"one_line": True, "no_co_authors": True}

    def test_one_short_subject_passes(self):
        self.assertEqual(check_commits.check([("a" * 40, "Add the walkthroughs\n")], self.STRICT), [])

    def test_long_subject_fails(self):
        self.assertTrue(check_commits.check([("a" * 40, "x" * 73)], {}))

    def test_body_and_co_author_pass_by_default(self):
        message = "Subject\n\nA body.\n\nCo-authored-by: Someone <a@b.c>\n"
        self.assertEqual(check_commits.check([("a" * 40, message)], {}), [])

    def test_body_fails_when_one_line_is_asked(self):
        self.assertTrue(check_commits.check([("a" * 40, "Subject\n\nA body.\n")], self.STRICT))

    def test_co_author_fails_when_asked(self):
        errors = check_commits.check([("a" * 40, "Subject\n\nCo-authored-by: Someone <a@b.c>\n")], self.STRICT)
        self.assertTrue(any("Co-authored-by" in error for error in errors))

    def test_conventional_subjects(self):
        rules = {"conventional": True}
        for subject in ("feat: export to CSV", "fix(parser): keep empty lines", "docs!: drop the old guide",
                        "chore(main): release 1.2.0"):
            with self.subTest(subject=subject):
                self.assertEqual(check_commits.check([("a" * 40, subject)], rules), [])
        for subject in ("Add export", "feat:no space", "Feat: capital", "feat (x): space before scope",
                        "fx: typo in the type", 'Revert "feat: export"'):
            with self.subTest(subject=subject):
                self.assertTrue(check_commits.check([("a" * 40, subject)], rules))
        self.assertEqual(check_commits.check([("a" * 40, "Add export")], {}), [])

    def test_unknown_commits_give_a_message(self):
        script = Path(__file__).resolve().parent / "check_commits.py"
        result = subprocess.run([sys.executable, str(script), "0" * 40, "1" * 40], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)


def template_tree(root, version, files):
    """Writes a tree with the template's files at a version and locks it."""
    changelog = f"# Changelog\n\n## {version} — 2026-10-24\n\nA change.\n\n## 0.1.0 — 2026-10-01\n\nFirst.\n"
    for name, text in {"docs/process/CHANGELOG.md": changelog, **files}.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    owned.write_lock(root, "someone/template")


class TemplateFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        template_tree(self.root, "0.2.0", {
            "docs/process/rules.md": "Rules.\n",
            "tools/process/check.py": "print()\n",
            ".github/workflows/process-checks.yml": "name: x\n",
            ".github/workflows/project-build.yml": "name: y\n",
            "docs/plan.md": "The project's.\n",
        })

    def tearDown(self):
        self.tmp.cleanup()

    def test_lock_holds_only_the_templates_files(self):
        lock = owned.read_lock(self.root)
        self.assertEqual(lock["version"], "0.2.0")
        self.assertEqual(sorted(lock["files"]), [
            ".github/workflows/process-checks.yml", "docs/process/CHANGELOG.md", "docs/process/rules.md",
            "tools/process/check.py"])

    def test_untouched_files_pass(self):
        self.assertEqual(owned.check(self.root), [])

    def test_the_release_workflow_is_not_synced_to_projects(self):
        self.assertFalse(owned.is_owned(".github/workflows/template-release.yml"))

    def test_projects_files_may_change(self):
        (self.root / "docs/plan.md").write_text("Changed.\n", encoding="utf-8")
        (self.root / ".github/workflows/project-build.yml").write_text("name: z\n", encoding="utf-8")
        self.assertEqual(owned.check(self.root), [])

    def test_edited_file_fails(self):
        (self.root / "docs/process/rules.md").write_text("Looser rules.\n", encoding="utf-8")
        self.assertTrue(any("rules.md: differs" in e for e in owned.check(self.root)))

    def test_added_file_fails(self):
        (self.root / "tools/process/extra.py").write_text("x\n", encoding="utf-8")
        self.assertTrue(any("extra.py: belongs to the template" in e for e in owned.check(self.root)))

    def test_removed_file_fails(self):
        (self.root / "tools/process/check.py").unlink()
        self.assertTrue(any("check.py: in .process-lock.json but missing" in e for e in owned.check(self.root)))

    def test_broken_lock_gives_a_message(self):
        (self.root / owned.LOCK).write_text("{not json", encoding="utf-8")
        self.assertTrue(any("not valid JSON" in e for e in owned.check(self.root)))

    def test_changelog_ahead_of_lock_fails(self):
        changelog = self.root / "docs/process/CHANGELOG.md"
        changelog.write_text("## 0.3.0 — 2026-10-25\n\n" + changelog.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertTrue(any("says version 0.2.0" in e for e in owned.check(self.root)))


class LockAgainstMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        template_tree(self.root, "0.2.0", {"docs/process/rules.md": "Rules.\n", "docs/plan.md": "Plan.\n"})
        self.base = owned.read_lock(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def change_and_relock(self, version):
        (self.root / "docs/process/rules.md").write_text("Other rules.\n", encoding="utf-8")
        changelog = self.root / "docs/process/CHANGELOG.md"
        if version != "0.2.0":
            changelog.write_text(f"## {version} — 2026-10-25\n\n" + changelog.read_text(encoding="utf-8"),
                                 encoding="utf-8")
        owned.write_lock(self.root, "someone/template")

    def test_projects_own_files_pass(self):
        (self.root / "docs/plan.md").write_text("Changed.\n", encoding="utf-8")
        self.assertEqual(check_lock.check(self.root, self.base), [])

    def test_relocked_change_without_a_new_version_fails(self):
        self.change_and_relock("0.2.0")
        self.assertEqual(owned.check(self.root), [])  # the pull request's own lock agrees
        errors = check_lock.check(self.root, self.base)
        self.assertTrue(any("doesn't move past version 0.2.0" in e for e in errors), errors)

    def test_new_version_passes(self):
        self.change_and_relock("0.3.0")
        self.assertEqual(check_lock.check(self.root, self.base), [])


class DoctorCodeOwners(unittest.TestCase):
    def test_code_owner_review_comes_from_the_pull_request_rule(self):
        self.assertTrue(doctor.code_owner_review([{"type": "pull_request", "parameters": {
            "required_approving_review_count": 0, "require_code_owner_review": True}}]))
        self.assertFalse(doctor.code_owner_review([{"type": "pull_request", "parameters": {}}]))
        self.assertIsNone(doctor.code_owner_review([{"type": "deletion"}]))

    def test_codeowners_must_give_github_to_the_owner_alone(self):
        def wrong(text):
            return doctor.not_owners_alone(text, "Owner")
        self.assertEqual(wrong("# the owner keeps it\n/.github/ @owner  # workflows too\n"), [])
        self.assertEqual(wrong("* @bot\n.github/ @owner\n"), [])
        self.assertEqual(wrong(""), doctor.CODE_OWNED)
        self.assertEqual(wrong("/.github/ @owner @bot\n"), doctor.CODE_OWNED)
        self.assertEqual(wrong("/.github/ @bot\n"), doctor.CODE_OWNED)
        self.assertEqual(wrong("/.github/ @owner\n* @bot\n"), doctor.CODE_OWNED)
        self.assertEqual(wrong("/.github/ @owner\n/.github/workflows/ @bot\n"),
                         [".github/workflows/process-owner.yml", ".github/workflows/x.yml"])
        self.assertEqual(wrong("/.github/ @owner\n/.github/workflows/*.yml\n"),
                         [".github/workflows/process-owner.yml", ".github/workflows/x.yml"])
        self.assertEqual(wrong("/.github/* @owner\n"),
                         [".github/workflows/process-owner.yml", ".github/workflows/x.yml"])
        self.assertEqual(wrong("/.github/ @owner\n/.github/* @bot\n"), [".github/CODEOWNERS"])


class DoctorRulesets(unittest.TestCase):
    def test_approvals_come_from_the_pull_request_rule(self):
        rules = [{"type": "deletion"}, {"type": "pull_request", "parameters": {
            "required_approving_review_count": 1, "dismiss_stale_reviews_on_push": True}}]
        self.assertEqual(doctor.approvals(rules), (1, True))

    def test_the_strictest_of_several_rulesets_counts(self):
        rules = [{"type": "pull_request", "parameters": {"required_approving_review_count": 0}},
                 {"type": "pull_request", "parameters": {"required_approving_review_count": 2,
                                                         "dismiss_stale_reviews_on_push": True}}]
        self.assertEqual(doctor.approvals(rules), (2, True))

    def test_no_pull_request_rule_means_unknown(self):
        self.assertIsNone(doctor.approvals([{"type": "deletion"}]))
        self.assertIsNone(doctor.approvals([]))

    def test_bypassing_is_seen_where_it_can_be_read(self):
        def classic(level):
            return {"protection": {"enabled": True, "required_status_checks": {"enforcement_level": level}}}
        self.assertTrue(doctor.binds_everyone(classic("everyone"), []))
        self.assertFalse(doctor.binds_everyone(classic("non_admins"), [{"type": "pull_request"}]))
        self.assertIsNone(doctor.binds_everyone(classic("everyone"), [{"type": "pull_request"}]))  # only admins see it
        self.assertIsNone(doctor.binds_everyone({}, [{"type": "pull_request"}]))
        self.assertIsNone(doctor.binds_everyone({}, []))


class DoctorIdentity(unittest.TestCase):
    def test_the_account_must_fit_agents_account(self):
        self.assertIsNone(doctor.identity_problem("own", "agents-bot", "Owner"))
        self.assertIn("agents_account is own", doctor.identity_problem("own", "owner", "Owner"))
        self.assertIsNone(doctor.identity_problem("owner", "owner", "Owner"))
        self.assertIn("agents_account is owner", doctor.identity_problem("owner", "agents-bot", "Owner"))


class Update(unittest.TestCase):
    def test_a_release_off_the_templates_main_is_refused_before_anything_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            template = Path(tmp) / "someone" / "template"
            template.mkdir(parents=True)
            git_in(template, "init", "-q", "-b", "main")
            commit_files(template, {"README.md": "The template.\n"}, "start")
            git_in(template, "checkout", "-q", "-b", "trial")
            commit_files(template, {"tools/process/sync.py": "raise SystemExit('ran')\n"}, "not merged")
            git_in(template, "tag", "v0.7.0")
            calls = []
            def run(*args, cwd=update.ROOT):
                if cwd != update.ROOT:  # the template's checkout, made by update.py itself
                    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout
                calls.append(args)
                if args[:2] == ("gh", "repo"):
                    return "someone/project"
                if args[:2] == ("git", "show"):
                    return json.dumps({"template": "someone/template", "version": "0.6.0", "files": {}})
                return ""
            def gh_json(*args):
                return {"tag_name": "v0.7.0"} if "releases/latest" in args[1] else []
            saved = update.run, update.gh_json, owned.TEMPLATE_SOURCE
            update.run, update.gh_json, owned.TEMPLATE_SOURCE = run, gh_json, str(Path(tmp)) + "/{}"
            try:
                with self.assertRaisesRegex(update.Failed, "not on the template's main"):
                    update.main()
            finally:
                update.run, update.gh_json, owned.TEMPLATE_SOURCE = saved
        self.assertFalse([args for args in calls if "checkout" in args or any("sync.py" in a for a in args)], calls)

    def test_the_owner_review_text_fits_why_the_owner_is_asked(self):
        self.assertEqual(update.review(True, False), ("ok-without-reading", update.NO_REVIEW))
        self.assertEqual(update.review(False, True), ("ok-without-reading", update.NO_REVIEW))
        self.assertEqual(update.review(True, True), ("owner-review", update.APPROVE_ONLY))
        text = update.APPROVE_ONLY.format(tag="v0.7.0", template="someone/template")
        self.assertIn("Approve only, no reading needed", text)
        self.assertIn("https://github.com/someone/template/releases/tag/v0.7.0", text)



class Sync(unittest.TestCase):
    def test_project_gets_the_new_version_and_keeps_its_own_files(self):
        with tempfile.TemporaryDirectory() as old, tempfile.TemporaryDirectory() as new:
            project, template = Path(old), Path(new)
            template_tree(project, "0.1.0", {"docs/process/gone.md": "Old.\n", "docs/process/rules.md": "Old.\n",
                                             "docs/plan.md": "The project's.\n"})
            template_tree(template, "0.2.0", {"docs/process/rules.md": "New.\n", "docs/process/added.md": "New.\n"})
            self.assertEqual(sync.sync(template, project), ("0.1.0", "0.2.0"))
            self.assertEqual((project / "docs/process/rules.md").read_text(encoding="utf-8"), "New.\n")
            self.assertTrue((project / "docs/process/added.md").exists())
            self.assertFalse((project / "docs/process/gone.md").exists())
            self.assertEqual((project / "docs/plan.md").read_text(encoding="utf-8"), "The project's.\n")
            self.assertEqual(owned.check(project), [])

    def test_changelog_since_gives_only_newer_entries(self):
        with tempfile.TemporaryDirectory() as folder:
            template = Path(folder)
            template_tree(template, "0.2.0", {})
            entries = sync.changelog_since(template, "0.1.0")
            self.assertIn("## 0.2.0", entries)
            self.assertNotIn("## 0.1.0", entries)


if __name__ == "__main__":
    unittest.main()
