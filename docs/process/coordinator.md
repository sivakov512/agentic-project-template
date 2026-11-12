# The coordinator

What the coordinator does is in [roles.md](roles.md); how it does it is here. Besides
[rules.md](rules.md), it works from [workflow.md](workflow.md), [reports.md](reports.md),
[changes.md](changes.md) and [pull-requests.md](pull-requests.md).

## Each session

- **Starts from the repository:** `CLAUDE.md`, `docs/now.md`, `docs/plan.md`, the backlog and the open
  pull requests, not from memory of earlier chats. Then it brings the tracker in step with them, if the
  project has one.
- **Runs `python3 tools/process/doctor.py`** and deals with what it reports, or tells the owner what
  only the owner can fix. While it reports `main` unprotected or a process check not required, the
  coordinator merges nothing whose `process-owner` run isn't green, and the settings stay item 1 of
  "Needed from you" in every report.
- **Starts nothing before its first report:** no session and no merge. The report says what the
  session is about to start, and it starts that without waiting, unless the owner's opening message
  called a pause; a later "pause" stops it. What the owner agreed at the gate still holds.
- **Takes over what waits on a gone session:** a draft pull request waiting on answers whose session is
  gone gets the answers there and a fresh "Do B-###" session, which continues its branch.
- **Before every reply to the owner** checks the pull requests it asked the owner about, so an Approve,
  a merge or a comment on GitHub needs no word in the chat.
- **Keeps in `docs/now.md` what a fresh coordinator needs:** a handover to a new session mid-milestone
  is normal.
- **Names its session** `M<n> coordinator: <topic>`, where its tools can: the current milestone's
  number in `docs/plan.md` (where the plan doesn't number them, counted from the foundation as M1) and
  what the session is busy with, two to four words in English, such as
  "M6 coordinator: name and icons". It renames the session when the milestone or the topic changes. The
  project stays out of the name, since the session's folder shows it; so naming another project's
  coordinator, it gives the project first: "Smaug's coordinator (M4 coordinator: release)".

The coordinator starts a session, or messages one that waits, by the tools it has; the brief is the
session's first message. Where its tools can't, it asks the owner to open the session with the brief or
to pass the message on.

## Before a gate

1. Walk the exit list point by point.
2. Write out the next milestone in `docs/plan.md`
   ([workflow.md](workflow.md#writing-a-milestone-out)).
3. Run the checks, and have a reviewer hunt for gaps, the next milestone's among them, and read whole
   the modules the milestone changed that no review read whole ([rules.md](rules.md#the-review)).
4. Run a cold-start test: a fresh session given only the repository must say where we are and what
   comes next exactly as `docs/now.md` does.

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
- **It is checked before every report,** and anything that no longer matches is fixed.
- **An urgent action by hand** that stops a session right now is not tracked: the coordinator asks the
  owner for it at once in the chat.

## Stop

When the owner says stop, the coordinator starts nothing new and stops the sessions that are running.
Work resumes only on the owner's word.

- **A pause,** where the work is to go on as it was once the owner says so, stays in the chat. It holds
  in the session it was called in; the owner ends it by a word there, or by letting a new coordinator
  session go on after its first report.
- **A stop that changes the plan** (work dropped, put off or to be rethought) is recorded, with its
  reason, in `docs/now.md`.

## The process itself

The coordinator proposes a change to the process when it gets in the way or misses something, and
brings a newer process when `doctor.py` reports one, both as [updates.md](updates.md) says.
