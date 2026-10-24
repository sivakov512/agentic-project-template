"""Tests for the process checks. Run: python3 -m unittest discover -s tools/process -p "test_*.py"."""

import json
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_commits  # noqa: E402
import check_docs  # noqa: E402
import check_lock  # noqa: E402
import check_pr  # noqa: E402
import doctor  # noqa: E402
import owned  # noqa: E402
import sync  # noqa: E402

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
    "project": {"set_up": True, "owner_language": "English", "tracker": "none", "agents_account": "own",
                "merged_by": "coordinator"},
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

Stage two needs it.

## How it was checked

`python3 tools/process/check.py`: passed.

## Docs updated

None, nothing else changed.

## Owner review

Not needed: text for machines.

## Not done and open questions

None at all.
"""


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
            ({"project": {**CONFIG["project"], "merged_by": ""}}, "merged_by must be set"),
            ({"project": {**CONFIG["project"], "agents_account": "bot"}}, "agents_account must be own or owner"),
            ({"ids_ignore": "docs/a.md"}, "ids_ignore must be a list"),
            ({"commits": {"one_line": "yes"}}, "commits must be an object of true or false"),
            ({"commits": {"signed": True}}, "knows only one_line and no_co_authors"),
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
        workflow = (TEMPLATE.parents[1] / ".github/workflows/process-checks.yml").read_text(encoding="utf-8")
        self.assertEqual(sorted(re.findall(r"^  (process-[a-z]+):", workflow, re.MULTILINE)),
                         sorted(doctor.REQUIRED_CHECKS))

    def test_template_and_check_agree(self):
        self.assertEqual(list(check_pr.sections(TEMPLATE.read_text())), check_pr.SECTIONS)

    def test_missing_section_fails(self):
        body = GOOD_BODY.replace("## Why\n\nStage two needs it.\n", "")
        self.assertIn("section \"Why\" is missing", self.errors(body))

    def test_section_with_next_to_nothing_fails(self):
        body = GOOD_BODY.replace("Stage two needs it.", "-")
        self.assertIn("section \"Why\" says next to nothing", self.errors(body))

    def test_unknown_backlog_item_fails(self):
        body = GOOD_BODY.replace("B-002 Second.", "B-042 Something.")
        self.assertIn("\"Backlog item\": B-042 is not in docs/backlog.md", self.errors(body))

    def test_two_backlog_items_fail(self):
        body = GOOD_BODY.replace("B-002 Second.", "B-001 and B-002.")
        self.assertTrue(any("belongs to one" in error for error in self.errors(body)))

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
            return subprocess.run([sys.executable, str(script), str(event), *more], capture_output=True, text=True)

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

    def test_body_and_event_together_are_refused(self):
        result = self.run_check({"draft": False}, "--body", "x.md")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)


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
        self.assertEqual(check_lock.check(self.root, self.base, []), [])

    def test_relocked_change_without_a_new_version_fails(self):
        self.change_and_relock("0.2.0")
        self.assertEqual(owned.check(self.root), [])  # the pull request's own lock agrees
        errors = check_lock.check(self.root, self.base, ["owner-review"])
        self.assertTrue(any("doesn't move past version 0.2.0" in e for e in errors), errors)

    def test_new_version_with_owner_review_passes(self):
        self.change_and_relock("0.3.0")
        self.assertEqual(check_lock.check(self.root, self.base, ["plan", "owner-review"]), [])

    def test_new_version_without_owner_review_fails(self):
        self.change_and_relock("0.3.0")
        errors = check_lock.check(self.root, self.base, ["plan", "ok-without-reading"])
        self.assertTrue(any("owner-review" in e for e in errors), errors)


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
