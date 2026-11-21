#!/usr/bin/env python3
"""The coordinator's merge of a pull request (docs/process/workflow.md, step 7): a squash merge of its last
commit, its subject the title and the number, its body empty, made only when every check ran on the base
as it is now. GitHub tests a pull request on its merge into the base, which it makes again only some time
after the base moves, so a green run may have tested an old base (check_base.py). When the base moved
after the last runs, or a run failed on an old base, this waits until GitHub has merged the pull request
on the new base, then closes and reopens the pull request, which runs the checks again and keeps the
owner's Approve; the coordinator runs it again once they finish. Rules on GitHub (reviews, required
checks) still decide whether the merge goes through. Standard library and gh only.

    python3 tools/process/merge.py <number>

It exits 0 when it merged, 1 when it didn't, saying why and what comes next.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_base  # noqa: E402

# How long to wait for GitHub to merge the pull request again on the new base, and how often to look.
WAIT_SECONDS = 180
POLL_SECONDS = 5
GOOD = {"success", "skipped", "neutral"}


class Failed(Exception):
    pass


def gh(*args):
    done = subprocess.run(["gh", *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise Failed(f"gh {' '.join(args[:2])}: {done.stderr.strip() or done.stdout.strip()}")
    return done.stdout


def api(path, *args):
    return json.loads(gh("api", path, *args) or "null")


def latest_runs(runs):
    """The newest run of each workflow, from GitHub's list of workflow runs."""
    newest = {}
    for run in runs:
        known = newest.get(run["workflow_id"])
        if known is None or run["created_at"] > known["created_at"]:
            newest[run["workflow_id"]] = run
    return list(newest.values())


def decide(runs, base_time, stale_base):
    """What to do, with the reason: ("merge", ""), ("wait", why), ("rerun", why) or ("red", why).
    runs: the newest run of each workflow on the pull request's last commit; base_time: when the base
    branch got its current commit (ISO 8601, as GitHub gives it); stale_base: whether a run failed on an
    old base (check_base.TITLE)."""
    if not runs:
        return "wait", "no checks have run on the last commit yet"
    running = [run["name"] for run in runs if run["status"] != "completed"]
    if running:
        return "wait", "still running: " + ", ".join(sorted(running))
    old = [run["name"] for run in runs if run["created_at"] < base_time]
    if old:
        return "rerun", "the base moved after these ran: " + ", ".join(sorted(old))
    if stale_base:
        return "rerun", "a run tested an old base"
    red = [run["name"] for run in runs if run["conclusion"] not in GOOD]
    if red:
        return "red", "failed: " + ", ".join(sorted(red))
    return "merge", ""


def stale_base(repo, head):
    """Whether the newest process-docs run on head failed on an old base, by its annotation."""
    found = api(f"repos/{repo}/commits/{head}/check-runs?check_name=process-docs&per_page=100")
    checks = sorted(found.get("check_runs", []), key=lambda check: check.get("started_at") or "")
    if not checks or checks[-1].get("conclusion") != "failure":
        return False
    notes = api(f"repos/{repo}/check-runs/{checks[-1]['id']}/annotations")
    return any(note.get("title") == check_base.TITLE for note in notes or [])


def wait_for_merge_on(repo, number, base_sha):
    """Waits until GitHub's merge of the pull request is on base_sha; False if it isn't in time, or if the
    pull request conflicts with the base."""
    deadline = time.monotonic() + WAIT_SECONDS
    while True:
        pull = api(f"repos/{repo}/pulls/{number}")
        if pull.get("mergeable") is False:
            return False
        merge = pull.get("merge_commit_sha")
        if merge and api(f"repos/{repo}/commits/{merge}")["parents"][0]["sha"] == base_sha:
            return True
        if time.monotonic() > deadline:
            return False
        time.sleep(POLL_SECONDS)


def main(argv):
    if len(argv) != 2 or not argv[1].isdigit():
        print("usage: python3 tools/process/merge.py <number>")
        return 2
    number = argv[1]
    try:
        repo = gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
        pull = api(f"repos/{repo}/pulls/{number}")
        if pull["state"] != "open" or pull.get("draft"):
            print(f"Not merged: pull request #{number} is {'a draft' if pull.get('draft') else pull['state']}.")
            return 1
        head, base = pull["head"]["sha"], pull["base"]["ref"]
        base_sha = api(f"repos/{repo}/git/ref/heads/{base}")["object"]["sha"]
        base_time = api(f"repos/{repo}/commits/{base_sha}")["commit"]["committer"]["date"]
        runs = api(f"repos/{repo}/actions/runs?head_sha={head}&event=pull_request&per_page=100")
        action, why = decide(latest_runs(runs.get("workflow_runs", [])), base_time, stale_base(repo, head))
        if action == "wait":
            print(f"Not merged: {why}. Run this again when the checks finish.")
            return 1
        if action == "red":
            print(f"Not merged: {why}. A red check is a \"fix\" finding (docs/process/workflow.md, step 5).")
            return 1
        if action == "rerun":
            if not wait_for_merge_on(repo, number, base_sha):
                print(f"Not merged: {why}, and GitHub hasn't merged the pull request on {base} at "
                      f"{base_sha[:8]} within {WAIT_SECONDS} s; if it conflicts with {base}, a work session "
                      f"merges {base} in (docs/process/workflow.md, step 7). Otherwise run this again later.")
                return 1
            gh("api", "-X", "PATCH", f"repos/{repo}/pulls/{number}", "-f", "state=closed")
            gh("api", "-X", "PATCH", f"repos/{repo}/pulls/{number}", "-f", "state=open")
            print(f"Not merged yet: {why}. The pull request was closed and reopened, so the checks run "
                  f"again on {base} at {base_sha[:8]}; run this again when they finish.")
            return 1
        gh("api", "-X", "PUT", f"repos/{repo}/pulls/{number}/merge", "-f", "merge_method=squash",
           "-f", f"sha={head}", "-f", f"commit_title={pull['title']} (#{number})", "-f", "commit_message=")
        print(f"Merged pull request #{number} at {head[:8]} on {base} at {base_sha[:8]}.")
        return 0
    except Failed as error:
        print(f"Not merged: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
