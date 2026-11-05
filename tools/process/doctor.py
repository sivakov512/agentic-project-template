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
REQUIRED_CHECKS = ["process-docs", "process-pr", "process-lock", "process-commits", "process-owner"]
# With the agents' own account .github/CODEOWNERS gives the owner .github/, where the workflow of
# process-owner is: it runs the check from the base branch's copy, so the workflow is all a pull request could change
# to get round it (docs/process/setup.md, step 8). Paths there that must fall to the owner alone:
CODE_OWNED = [".github/CODEOWNERS", ".github/workflows/process-owner.yml", ".github/workflows/x.yml"]


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


def approvals(rules):
    """(required approvals, dismissed by new commits) as GitHub applies them, the strictest of the
    rulesets' pull request rules; None when no ruleset has one (classic protection, which only an admin
    can read)."""
    found = [rule.get("parameters") or {} for rule in rules if rule.get("type") == "pull_request"]
    if not found:
        return None
    return (max(int(p.get("required_approving_review_count", 0)) for p in found),
            any(bool(p.get("dismiss_stale_reviews_on_push")) for p in found))


def binds_everyone(branch, rules):
    """Whether main's protection lets nobody past it, the owner and admins included: False when classic
    protection leaves admins out of its required checks; True when it binds everyone and no ruleset is on
    main; None otherwise, since only an admin can read a ruleset's bypass list. branch: GitHub's answer
    for the branch; rules: the rules of the rulesets on main."""
    protection = branch.get("protection") or {}
    level = (protection.get("required_status_checks") or {}).get("enforcement_level")
    if protection.get("enabled") and level == "non_admins":
        return False
    return True if protection.get("enabled") and level == "everyone" and not rules else None


def identity_problem(agents_account, login, owner):
    """What is wrong with gh's account (login) for agents_account, or None when it fits. Under their own
    account the agents must not hold the owner's, which GitHub lets approve and merge as the owner; under
    the owner's, they work as the owner (docs/process/workflow.md, "The owner's OK and the merge")."""
    same = login.lower() == owner.lower()
    if agents_account == "own" and same:
        return (f"gh works as the repository's owner {login}, but agents_account is own: sign gh and git in"
                " as the agents' account, where the owner's isn't signed in")
    if agents_account == "owner" and not same:
        return f"gh works as {login}, but agents_account is owner: the agents work as {owner}, or the setting is own"
    return None


def code_owner_review(rules):
    """Whether a ruleset's pull request rule asks for the code owners' review; None when no ruleset has a
    pull request rule."""
    found = [rule.get("parameters") or {} for rule in rules if rule.get("type") == "pull_request"]
    return any(bool(p.get("require_code_owner_review")) for p in found) if found else None


def codeowners_pattern(pattern):
    """A CODEOWNERS pattern (gitignore-like) as a regular expression for a path from the repository's root."""
    anchored = pattern.startswith("/") or "/" in pattern.rstrip("/")
    body = re.escape(pattern.strip("/")).replace(r"\*\*", ".*").replace(r"\*", "[^/]*").replace(r"\?", "[^/]")
    # "dir/*" covers the files in dir, not those in its folders; anything else covers what is under it too.
    return re.compile(("^" if anchored else "^(.*/)?") + body + ("$" if pattern.endswith("/*") else "(/.*)?$"))


def not_owners_alone(text, owner):
    """The paths of CODE_OWNED whose owners in a CODEOWNERS file are not the owner alone: the last rule
    that matches a path decides it, as GitHub reads the file."""
    rules = []
    for line in text.splitlines():
        words = line.split("#", 1)[0].split()
        if words:
            rules.append((codeowners_pattern(words[0]), [word.lower() for word in words[1:]]))
    wrong = []
    for path in CODE_OWNED:
        owners = next((owners for pattern, owners in reversed(rules) if pattern.match(path)), [])
        if owners != ["@" + owner.lower()]:
            wrong.append(path)
    return wrong


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
    code, out = gh("api", f"repos/{repo}", "--jq", "{type: .owner.type, private: .private}")
    about = json.loads(out) if code == 0 else {}
    if agents_account != "owner" and about:
        report.line(about.get("type") == "User", "the repository belongs to the owner's personal account",
                    "process-owner counts only the repository owner's approval, and an organisation"
                    " gives nobody that (docs/process/workflow.md, \"The owner's OK and the merge\")")
    # The template's coordinator works as the agents' own account.
    account = agents_account or ("own" if is_template else None)
    code, out = gh("api", "user", "--jq", ".login")
    if account and code == 0 and about.get("type") == "User":
        problem = identity_problem(account, out.strip(), repo.split("/")[0])
        report.line(not problem, f"gh works as {out.strip()}, as agents_account {account} asks", problem)
    elif account:
        report.line(None, "gh's account fits agents_account", "can't tell gh's account from the repository's owner")
    if about.get("private") is False:
        code, out = gh("api", f"repos/{repo}/actions/variables", "--jq", ".variables[].name")
        report.line(None if code != 0 else "CI_RUNNER" not in out.split(),
                    "no self-hosted runner for a public repository",
                    "with CI_RUNNER set, anyone's pull request runs on that runner: the owner deletes the variable"
                    " (Settings > Secrets and variables > Actions > Variables) or makes the repository private")
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

    # Readable with read access: the branch (classic protection) and the rules on it (rulesets). Approval
    # settings come from the rulesets; under classic protection only an admin can read them.
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
        # process-owner asks for the owner's approval where it is needed; a required approval on top of it
        # would stop the coordinator from merging what is OK without reading.
        reviews = approvals(rules)
        if reviews is None:
            report.line(None, "no required approvals for main",
                        "the owner checks: process-owner asks for approvals where needed (docs/process/setup.md, step 8)")
        elif reviews[0] > 0:
            report.line(None if agents_account != "owner" else False, "no required approvals for main",
                        f"the ruleset asks {reviews[0]} approval(s): "
                        + ("nobody can approve their own pull request, so nothing would merge"
                           if agents_account == "owner" else
                           "pull requests OK without reading still wait for the owner")
                        + " (docs/process/setup.md, step 8)")
        if agents_account != "owner":
            owner = repo.split("/")[0]
            codeowners = ROOT / ".github/CODEOWNERS"
            text = codeowners.read_text(encoding="utf-8") if codeowners.exists() else ""
            report.line(not not_owners_alone(text, owner), f".github/CODEOWNERS gives .github/ to @{owner} alone",
                        f"its last rule for .github/ must be \"/.github/ @{owner}\" (docs/process/setup.md, step 8)")
            report.line(code_owner_review(rules), "main requires the code owners' review",
                        "the owner ticks \"Require review from Code Owners\" (docs/process/setup.md, step 8)")
            report.line(None if reviews is None else reviews[1], "approvals are dismissed by new commits",
                        "the owner ticks \"Dismiss stale pull request approvals when new commits are pushed\""
                        " (docs/process/setup.md, step 8)")
        # Bypassing would let the owner's account, or anyone holding it, merge past process-owner.
        report.line(binds_everyone(branch, rules), "no bypassing for main",
                    "the owner checks it: an empty bypass list in the ruleset, or \"Do not allow bypassing the"
                    " above settings\" in classic protection (docs/process/setup.md, step 8)")

    template = lock.get("template")
    if template:
        code, out = gh("api", f"repos/{template}/releases/latest", "--jq", ".tag_name")
        if code == 0 and re.match(r"^v?\d+\.\d+\.\d+$", out.strip()):
            latest = out.strip().lstrip("v")
            current = lock.get("version", "0.0.0")
            report.line(owned.version_tuple(latest) <= owned.version_tuple(current),
                        f"the process is the newest ({current})",
                        f"{latest} is out: run python3 tools/process/update.py, or merge the open process update"
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
