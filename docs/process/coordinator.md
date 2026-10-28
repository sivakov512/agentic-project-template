# The coordinator

## Each session

- **Starts from the repository:** `CLAUDE.md`, `docs/now.md`, `docs/plan.md`, the backlog and the open
  pull requests. Not from memory of earlier chats. Then it brings the tracker in step with them, if the
  project has one.
- **Runs `python3 tools/process/doctor.py`** and deals with what it reports, or tells the owner what
  only the owner can fix.
- **One coordinator session per stage.** At the end of a stage, `docs/now.md` holds everything the next
  session needs.

## Before a gate

Walk the exit list point by point, run the checks, have a reviewer hunt for gaps, and run a cold-start
test: a fresh session given only the repository must say where we are and what comes next exactly as
`docs/now.md` does. Then write out the next stage
([workflow.md](workflow.md#stages-and-gates)) and bring it with the gate.

## The tracker

A project may keep a tracker that mirrors it for the owner: `tracker` in `docs/process.json` names it
(or says `none`), and `docs/plan.md` says how the rules below map onto the tracker's own items. The
coordinator keeps it, the same day as things happen:

- **It mirrors the repository,** never the other way round: no requirement or decision lives only
  there.
- **What waits on the owner is there as the owner's,** with a short checklist: where to click (links),
  what exactly to read or do, why it matters, about how many minutes, and which decisions are asked
  for. While agents work on something, it waits on them.
- **Progress is recorded when results land:** a pull request merged, a gate passed. What the plan did
  not expect (a decision, an obstacle, a risk) is recorded where the owner sees it.
- **It stays brief:** pieces of work, not single actions; facts, not plans.
- **It is checked before every report,** and anything that no longer matches is fixed; the report says
  what changed there ([reports.md](reports.md)).
- **An urgent action by hand** that stops a session right now is not tracked: the coordinator asks the
  owner for it at once in the chat.

## Stop

When the owner says stop, the coordinator starts nothing new, stops the sessions that are running, and
records the stop and its reason in `docs/now.md`. Work resumes only on the owner's word.

## The process itself

When the process gets in the way or misses something, the coordinator proposes a change to the
template ([updates.md](updates.md#changing-the-process)). When `doctor.py` reports a newer process, the
coordinator brings the update as [updates.md](updates.md#getting-a-newer-process) says.
