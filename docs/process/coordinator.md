# The coordinator

What the coordinator does is in [roles.md](roles.md); how it does it is here and in what this file
links. Besides [rules.md](rules.md), it works from [workflow.md](workflow.md) (milestones and gates, how
a piece of work goes, the merge), [reports.md](reports.md) (what it tells the owner),
[changes.md](changes.md) (recording the owner's words, the backlog, decisions) and
[pull-requests.md](pull-requests.md).

## Each session

- **Starts from the repository:** `CLAUDE.md`, `docs/now.md`, `docs/plan.md`, the backlog and the open
  pull requests. Not from memory of earlier chats. Then it brings the tracker in step with them, if the
  project has one.
- **Runs `python3 tools/process/doctor.py`** and deals with what it reports, or tells the owner what
  only the owner can fix.
- **One coordinator session per milestone.** At the end of a milestone, `docs/now.md` holds everything
  the next session needs.

## Before a gate

Walk the exit list point by point and write out the next milestone in `docs/plan.md`: a milestone left
as one line gives its sessions nothing to work from. Then run the checks, have a reviewer hunt for gaps,
the next milestone's among them, and run a cold-start test: a fresh session given only the repository
must say where we are and what comes next exactly as `docs/now.md` does. The next milestone goes to the
owner in the same report as the gate. How a milestone is written out, how it ends, with the owner trying
it, and when the next one is written out: [workflow.md](workflow.md#milestones-and-gates).

## The tracker

A project may keep a tracker that mirrors it for the owner: `tracker` in `docs/process.json` names it
(or says `none`), and `docs/plan.md` says how the rules below map onto the tracker's own items. The
coordinator keeps it, the same day as things happen:

- **It mirrors the repository,** never the other way round: no requirement or decision lives only
  there.
- **What waits on the owner is there as the owner's,** each with what the report's last point gives
  for it ([reports.md](reports.md)). While agents work on something, it waits on them.
- **Progress is recorded when results land:** a pull request merged, a gate passed. What the plan did
  not expect (a decision, an obstacle, a risk) is recorded where the owner sees it.
- **It stays brief:** pieces of work, not single actions; facts, not plans.
- **It is checked before every report,** and anything that no longer matches is fixed; the report says
  what changed there if `docs/plan.md` asks for it ([reports.md](reports.md)).
- **An urgent action by hand** that stops a session right now is not tracked: the coordinator asks the
  owner for it at once in the chat.

## Stop

When the owner says stop, the coordinator starts nothing new and stops the sessions that are running.
Work resumes only on the owner's word. A pause, where the work is to go on as it was once the owner says
so, stays in the chat: it holds in the session it was called in, and the owner ends it by a word there
or by starting a new coordinator session. Only a stop that changes the plan (work dropped, put off or to
be rethought) is recorded, with its reason, in `docs/now.md`.

## The process itself

When the process gets in the way or misses something, the coordinator proposes a change to the
template ([updates.md](updates.md#changing-the-process)). When `doctor.py` reports a newer process, the
coordinator brings the update as [updates.md](updates.md#getting-a-newer-process) says.
