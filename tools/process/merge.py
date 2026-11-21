#!/usr/bin/env python3
"""The coordinator's merge of a pull request (docs/process/workflow.md#the-merge): a squash merge of
the commit that was reviewed and approved, its subject the title and the number, its body empty, made
only when every check ran after the base got its current commit.

GitHub tests a pull request on its merge into the base, which it makes again only some time after the
base moves. When the base moved after the last runs, or no run came at all, this waits until GitHub has
merged the pull request on the new base, then closes and reopens it, which runs the checks again (every
workflow on pull requests runs on `reopened`, docs/process/pull-requests.md) and keeps the owner's
Approve; the coordinator runs it again once they finish. It reopens at most once for each commit of the
base: if that didn't help, it stops and says what is still wrong. It reads the runs of pull request and
review events, so a review that dismisses the owner's Approve counts. Rules on GitHub (reviews, required
checks) still decide whether the merge goes through. Standard library and gh only.

    python3 tools/process/merge.py <number> <commit>

<commit> is the last commit reviewed and approved; it refuses when the pull request's last commit is
another. It exits 0 when it merged, 1 when it didn't, saying why and what comes next, 2 on wrong arguments.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

# How long to wait for GitHub to merge the pull request again on the new base, and how often to look.
WAIT_SECONDS = 180
POLL_SECONDS = 5
# How long after a push, or a reopening, runs may take to appear.
START_GRACE = timedelta(minutes=10)
GOOD = {"success", "skipped", "neutral"}
EVENTS = {"pull_request", "pull_request_review"}
# The workflow of the owner's OK (check_owner.py): red alone, it waits for the owner's Approve.
OWNER_WORKFLOW = "process-owner"


class Failed(Exception):
    pass


def gh(*args):
    done = subprocess.run(["gh", *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise Failed(f"gh {' '.join(args[:3])}: {done.stderr.strip() or done.stdout.strip()}")
    return done.stdout


def api(path, *args):
    return json.loads(gh("api", path, *args) or "null")


def when(text):
    """A GitHub timestamp as an aware datetime, or None."""
    return datetime.fromisoformat(text.replace("Z", "+00:00")) if text else None


def latest_runs(runs):
    """The newest run of each workflow from pull request and review events, from GitHub's list of runs."""
    newest = {}
    for run in runs:
        if run.get("event") not in EVENTS:
            continue
        known = newest.get(run["workflow_id"])
        if known is None or (run["created_at"], run["id"]) > (known["created_at"], known["id"]):
            newest[run["workflow_id"]] = run
    return list(newest.values())


def decide(runs, base_time, pushed_at, reopened_at, now):
    """What to do, with the reason: ("merge", ""), ("wait", why), ("rerun", why), ("stop", why),
    ("cancelled", why) or ("red", why).
    runs: the newest run of each workflow on the pull request's last commit; base_time: when the base
    branch got its current commit; pushed_at: when the last commit was pushed, or None; reopened_at: when
    the pull request was last reopened, or None; now: the current time. Times are aware datetimes."""
    reopened_here = reopened_at is not None and reopened_at >= base_time
    just_reopened = reopened_here and now - reopened_at < START_GRACE
    if not runs:
        why = "no checks have run on the last commit"
        if just_reopened:
            return "wait", why + " since it was reopened"
        if reopened_here:
            return "stop", why + ", even after reopening it on this base"
        if pushed_at is None or now - pushed_at < START_GRACE:
            return "wait", why + " yet"
        return "rerun", why
    running = sorted(run["name"] for run in runs if run["status"] != "completed")
    if running:
        return "wait", "still running: " + ", ".join(running)
    if just_reopened and any(when(run["created_at"]) < reopened_at for run in runs):
        return "wait", "the checks haven't all started again since the pull request was reopened"
    old = sorted(run["name"] for run in runs if when(run["created_at"]) < base_time)
    if old:
        why = "the base moved after these ran: " + ", ".join(old)
        if not reopened_here:
            return "rerun", why
        return "stop", why + ", even after reopening it on this base"
    cancelled = sorted(run["name"] for run in runs if run["conclusion"] == "cancelled")
    if cancelled:
        return "cancelled", ", ".join(cancelled) + " cancelled"
    red = sorted(run["name"] for run in runs if run["conclusion"] not in GOOD)
    if red:
        return "red", "failed: " + ", ".join(red)
    return "merge", ""


def moved_at(repo, branch, sha):
    """When branch got commit sha: the push GitHub records for it, or the commit's own date if the record
    names another commit."""
    pushes = api(f"repos/{repo}/activity?ref=refs/heads/{branch}&per_page=1") or []
    if pushes and pushes[0].get("after") == sha:
        return when(pushes[0]["timestamp"])
    return when(api(f"repos/{repo}/commits/{sha}")["commit"]["committer"]["date"])


def last_event(repo, number, name):
    """When the pull request last had the issue event name (reopened, say), or None."""
    times = []
    for page in range(1, 11):
        events = api(f"repos/{repo}/issues/{number}/events?per_page=100&page={page}") or []
        times += [when(event["created_at"]) for event in events if event.get("event") == name]
        if len(events) < 100:
            break
    return max(times) if times else None


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


def reopen(repo, number):
    """Closes and reopens the pull request; raises Failed, saying it is left closed, if reopening fails."""
    gh("api", "-X", "PATCH", f"repos/{repo}/pulls/{number}", "-f", "state=closed")
    for attempt in range(3):
        try:
            gh("api", "-X", "PATCH", f"repos/{repo}/pulls/{number}", "-f", "state=open")
            return
        except Failed as error:
            if attempt == 2:
                raise Failed(f"pull request #{number} is left CLOSED, reopen it now: gh api -X PATCH "
                             f"repos/{repo}/pulls/{number} -f state=open ({error})")
            time.sleep(POLL_SECONDS)


def red_message(why):
    """What merge says of red checks, why being decide's reason ("failed: " and the workflows' names):
    when only the owner's OK is red, the owner's Approve is what is missing, otherwise a check to fix."""
    if why == "failed: " + OWNER_WORKFLOW:
        return (f"Not merged: {why}. The owner's Approve of the last commit is missing or not yet checked; "
                f"run this again after it.")
    return (f"Not merged: {why}. Fix the red check: it is a \"fix\" finding "
            f"(docs/process/workflow.md, step 5).")


def merge(repo, number, commit):
    pull = api(f"repos/{repo}/pulls/{number}")
    if pull["state"] != "open" or pull.get("draft"):
        return 1, f"Not merged: pull request #{number} is {'a draft' if pull.get('draft') else pull['state']}."
    head, base = pull["head"]["sha"], pull["base"]["ref"]
    if not head.startswith(commit):
        return 1, (f"Not merged: the last commit of pull request #{number} is {head[:8]}, not {commit[:8]}, "
                   f"the one reviewed and approved.")
    base_sha = api(f"repos/{repo}/git/ref/heads/{base}")["object"]["sha"]
    runs = api(f"repos/{repo}/actions/runs?head_sha={head}&per_page=100")
    action, why = decide(latest_runs(runs.get("workflow_runs", [])), moved_at(repo, base, base_sha),
                         moved_at(repo, pull["head"]["ref"], head),
                         last_event(repo, number, "reopened"), datetime.now(timezone.utc))
    if action == "wait":
        return 1, f"Not merged: {why}. Run this again when the checks finish."
    if action == "cancelled":
        return 1, f"Not merged: {why}: run them again (gh run rerun <id>), then run this again."
    if action == "red":
        return 1, red_message(why)
    if action == "stop":
        return 1, (f"Not merged: {why}. Reopening again won't help: a workflow that doesn't run on "
                   f"`reopened` must get it in the project's .github/workflows "
                   f"(docs/process/pull-requests.md); otherwise say so in the report.")
    if action == "rerun":
        if not wait_for_merge_on(repo, number, base_sha):
            return 1, (f"Not merged: {why}, and GitHub hasn't merged the pull request on {base} at "
                       f"{base_sha[:8]} within {WAIT_SECONDS} s; if it conflicts with {base}, a work "
                       f"session merges {base} in (docs/process/workflow.md#the-merge). Otherwise run this "
                       f"again later.")
        reopen(repo, number)
        return 1, (f"Not merged yet: {why}. The pull request was closed and reopened, so the checks run "
                   f"again on {base} at {base_sha[:8]}; run this again when they finish.")
    gh("api", "-X", "PUT", f"repos/{repo}/pulls/{number}/merge", "-f", "merge_method=squash",
       "-f", f"sha={head}", "-f", f"commit_title={pull['title']} (#{number})", "-f", "commit_message=")
    return 0, f"Merged pull request #{number} at {head[:8]} on {base} at {base_sha[:8]}."


def main(argv):
    if len(argv) != 3 or not argv[1].isdigit() or len(argv[2]) < 7:
        print("usage: python3 tools/process/merge.py <number> <commit reviewed and approved>")
        return 2
    try:
        repo = gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
        code, message = merge(repo, argv[1], argv[2])
    except Failed as error:
        code, message = 1, f"Not merged: {error}"
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
