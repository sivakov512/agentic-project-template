#!/usr/bin/env python3
"""Says what is missing in this repository's setup, as a checklist. The coordinator runs it at the start
of every session (docs/process/coordinator.md). Standard library and the gh command line only.

    python3 tools/process/doctor.py               the checklist; exit 1 if anything fails
    python3 tools/process/doctor.py --fix-labels  also create the missing labels
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_docs  # noqa: E402
import check_pr  # noqa: E402
import owned  # noqa: E402

ROOT = HERE.parents[1]
LABELS = {**check_pr.KIND_DESCRIPTIONS, **check_pr.REVIEW_LABELS}
PROJECT_FILES = ["CLAUDE.md", "README.md", "docs/plan.md", "docs/now.md", "docs/backlog.md",
                 "docs/decisions/README.md", check_docs.CONFIG]
PLACEHOLDER = "<!-- template placeholder -->"
REQUIRED_CHECKS = ["process-docs", "process-pr", "process-lock", "process-commits"]


class Report:
    def __init__(self):
        self.failed = 0

    def line(self, ok, text, hint=None):
        mark = {True: "ok  ", False: "FAIL", None: "?   "}[ok]
        print(f"[{mark}] {text}" + (f"\n         {hint}" if hint and ok is not True else ""))
        if ok is False:
            self.failed += 1


def gh(*args):
    """Runs gh; returns (exit code, stdout). The last stderr is kept in gh.stderr."""
    try:
        done = subprocess.run(["gh", *args], cwd=ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        gh.stderr = "gh not found"
        return 127, ""
    gh.stderr = done.stderr
    return done.returncode, done.stdout


def this_repo():
    code, out = gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    return out.strip() if code == 0 else None


def check_files(report):
    try:
        lock = owned.read_lock(ROOT) or {}
    except ValueError:
        lock = {}  # owned.check below reports it
    config = {}
    try:
        config = check_docs.load_config(ROOT)
        report.line(True, f"{check_docs.CONFIG} is valid JSON")
    except ValueError as error:
        report.line(False, f"{check_docs.CONFIG} is valid JSON", str(error))
    project = config.get("project") if isinstance(config, dict) else None
    set_up = project.get("set_up") if isinstance(project, dict) else None
    if isinstance(config, dict):
        for error in check_docs.config_errors(config):
            report.line(False, error)
        tracker = project.get("tracker") if isinstance(project, dict) else None
        if set_up and project.get("agents_account") and project.get("merged_by"):
            account = "their own account" if project["agents_account"] == "own" else "the owner's account"
            report.line(True, f"agents work under {account}; the {project['merged_by']} merges"
                        " (docs/process/workflow.md)")
        if set_up and isinstance(tracker, str) and tracker.strip():
            report.line(True, f"tracker: {tracker}" + ("" if tracker.strip().lower() == "none"
                        else " (keep it in step: docs/process/coordinator.md, \"The tracker\")"))
        checks = config.get("checks")
        if isinstance(checks, list) and checks:
            report.line(any((ROOT / ".github/workflows").glob("project-*.yml")),
                        "a project workflow runs the project's checks in CI",
                        "add .github/workflows/project-checks.yml and ask the owner to make its jobs required")
    for name in PROJECT_FILES:
        path = ROOT / name
        if not path.exists():
            report.line(False, f"{name} exists", "see docs/process/setup.md")
        elif set_up and PLACEHOLDER in path.read_text(encoding="utf-8"):
            report.line(False, f"{name} is filled in", "it still holds the template's placeholder")
    claude = ROOT / "CLAUDE.md"
    if claude.exists():
        report.line("@docs/process/rules.md" in claude.read_text(encoding="utf-8"),
                    "CLAUDE.md imports the process rules", "keep the line @docs/process/rules.md")
    errors = owned.check(ROOT)
    report.line(not errors, "the template's files match the lock", "; ".join(errors[:3]))
    agents_account = project.get("agents_account") if isinstance(project, dict) else None
    return lock, set_up, agents_account


def check_github(report, lock, set_up, fix_labels, agents_account):
    repo = this_repo()
    if not repo:
        report.line(None, "GitHub", "gh can't see this repository: log in to gh to check the GitHub side")
        return
    is_template = repo == lock.get("template")
    report.line(True, f"repository {repo}" + (" (the template itself)" if is_template else ""))
    if not is_template:
        report.line(bool(set_up), "the project is set up", "follow docs/process/setup.md")

    code, out = gh("label", "list", "--limit", "200", "--json", "name", "--jq", ".[].name")
    if code != 0:
        report.line(None, "labels", "can't read labels")
    else:
        missing = [name for name in LABELS if name not in out.split("\n")]
        if missing and fix_labels:
            failed = [name for name in missing if gh("label", "create", name, "--description", LABELS[name])[0] != 0]
            created = [name for name in missing if name not in failed]
            if created:
                report.line(True, "labels created: " + ", ".join(created))
            if failed:
                report.line(False, "labels created", "couldn't create: " + ", ".join(failed))
        else:
            report.line(not missing, "labels for kinds and review",
                        "missing: " + ", ".join(missing) + " (run with --fix-labels)")

    # Readable with read access: the branch (classic protection) and the rules on it (rulesets). How
    # many approvals and whether a new commit dismisses one only an admin can read.
    code, out = gh("api", f"repos/{repo}/branches/main")
    branch = json.loads(out) if code == 0 else {}
    code, out = gh("api", f"repos/{repo}/rules/branches/main")
    rules = json.loads(out) if code == 0 else []
    if not branch:
        report.line(False, "the branch main exists", "the process expects the default branch to be main")
    else:
        protected = bool(branch.get("protected")) or any(
            rule.get("type") in ("pull_request", "required_status_checks") for rule in rules)
        report.line(protected, "main is protected", "the owner protects it (docs/process/setup.md, step 8)")
        contexts = set(((branch.get("protection") or {}).get("required_status_checks") or {}).get("contexts") or [])
        for rule in rules:
            if rule.get("type") == "required_status_checks":
                contexts |= {check.get("context") for check in
                             (rule.get("parameters") or {}).get("required_status_checks", [])}
        missing_checks = [name for name in REQUIRED_CHECKS if name not in contexts]
        report.line(protected and not missing_checks, "the process checks are required for main",
                    "the owner requires them: " + ", ".join(missing_checks))
        if agents_account == "own":
            report.line(None, "approvals for main",
                        "the owner checks: one approval, dismissed by new commits (docs/process/setup.md, step 8)")
        elif agents_account == "owner":
            report.line(None, "no bypassing for main",
                        "the owner checks it is on, or the protection doesn't bind the owner's account"
                        " (docs/process/setup.md, step 8)")

    if not is_template:
        code, out = gh("secret", "list", "--json", "name", "--jq", ".[].name")
        if code == 0:
            report.line("PROCESS_UPDATE_TOKEN" in out.split("\n"), "the PROCESS_UPDATE_TOKEN secret",
                        "the owner adds it (docs/process/updates.md)")
        else:
            report.line(None, "the PROCESS_UPDATE_TOKEN secret",
                        "can't list secrets with this account: the owner checks Settings → Secrets and variables → Actions")

    template = lock.get("template")
    if template:
        code, out = gh("api", f"repos/{template}/releases/latest", "--jq", ".tag_name")
        if code == 0 and re.match(r"^v?\d+\.\d+\.\d+$", out.strip()):
            latest = out.strip().lstrip("v")
            current = lock.get("version", "0.0.0")
            report.line(owned.version_tuple(latest) <= owned.version_tuple(current),
                        f"the process is the newest ({current})",
                        f"{latest} is out: merge the open process update, or run the process-update workflow"
                        " (docs/process/updates.md)")
        else:
            report.line(None, "the newest process", f"can't read releases of {template}")


def main(argv):
    report = Report()
    lock, set_up, agents_account = check_files(report)
    check_github(report, lock, set_up, "--fix-labels" in argv[1:], agents_account)
    print("Nothing missing" if not report.failed else f"{report.failed} thing(s) missing")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
