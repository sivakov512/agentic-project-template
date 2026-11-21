# The coordinator

The coordinator runs the plan like a product manager ([README.md](README.md#roles)). Besides this file it
works from [workflow.md](workflow.md), [owner.md](owner.md), [changes.md](changes.md) and
[pull-requests.md](pull-requests.md).

## Each session

- **Starts from the repository:** `CLAUDE.md`, `docs/now.md`, `docs/plan.md`, the backlog and the open
  pull requests, not from memory of earlier chats; then brings the tracker in step, if there is one.
- **Runs `python3 tools/process/doctor.py`** and deals with what it reports, or tells the owner what only
  the owner can fix. While it reports `main` unprotected or a process check not required, the coordinator
  merges nothing whose `process-owner` run isn't green, and the settings stay first in "Needed from you".
- **Starts nothing before its first report:** no session and no merge. The report says what it is about
  to start, and it starts that without waiting, unless the owner's opening message called a pause.
- **Takes over what waits on a gone session:** a draft, or a pull request with "fix" findings no fix
  comment has answered, gets a fresh session with the same brief, which continues its branch; open
  questions are answered first. A draft whose session said the work is done goes to its reviews. One
  whose session stopped and reported waits for the coordinator's decision.
- **Before every reply to the owner** checks the pull requests it asked the owner about, so an Approve or
  a comment on GitHub needs no word in the chat.
- **Keeps in `docs/now.md` what a fresh coordinator needs:** a handover mid-milestone is normal.
- **Names its session** `M<n> coordinator: <topic>` where its tools can: the current milestone's number
  (counted from the foundation as M1 where the plan doesn't number them) and two to four words in English
  on what it is busy with. It renames the session when either changes.

The coordinator starts a session, or messages one that waits, by the tools it has; the brief is the
session's first message. Where its tools can't, it asks the owner to open the session with the brief.

## The report

Whenever there is something for the owner (pull requests to look at, pull requests merged since the last
report, a gate), the coordinator reports. The report fits on a phone's screen, about twelve lines, and
links the pull requests for detail. In this order, each point but the last left out when it has nothing
to say:

1. **Where we are,** one line: the milestone and the next step.
2. **In work:** one line per item or pull request in work.
3. **What changed,** one line each, saying how it ended: merged, waiting on what, checked how. Then the
   pull requests merged without the owner since the commit `docs/now.md` gives as "Reported up to", one
   line each; the next record of `docs/now.md` moves that line to the last merge the report listed.
4. **Decisions the coordinator made itself,** so the owner can reverse any of them, **deviations from the
   plan, and risks,** one line each.
5. **Needed from you:** a numbered item per action only the owner can take (an approval, a question, a
   result to try, a setting), questions each with the coordinator's recommendation. Each item gives the
   action and its link, what it decides in one line, why it is the owner's ([owner.md](owner.md)), and
   what to look at and for how many minutes, or that no reading is needed and why; for risky code, what
   could break and what guards it. Or one line that nothing is needed.

`docs/plan.md` may add points of the project's own, before the last one. The owner asking for the status
gets a report in this form. Any other answer stays a plain answer, with what waits on the owner at its
end.

When "Needed from you" gains an item, the coordinator also notifies the owner outside the chat, where its
tools can: one line with the project and what is needed.

Settings the owner must change are given as a path of clicks (Settings → Branches → `main` → …), not as
commands.

## Before a gate

1. Write out the next milestone in `docs/plan.md` ([workflow.md](workflow.md#writing-a-milestone-out)).
2. Tick the exit list in the description of that plan's pull request, each point with its evidence: a
   link, or the owner's words with their date. The owner's word that they used the release in real work
   is asked in "Needed from you".
3. Start the gate review ([reviews.md](reviews.md#the-gate-review)) on that pull request, naming the
   modules the milestone built or changed; at the plan's last milestone, on the coordinator record that
   brings `docs/now.md` up to date. Its findings are fixed where they belong before the gate: `docs/now.md`
   in a coordinator record, an open point of the exit list by finishing it, the plan in its pull request;
   the rest become backlog items.

## The tracker

A project may keep a tracker that mirrors it for the owner: `tracker` in `docs/process.json` names it, or
says `none`, and `docs/plan.md` says how it maps onto the tracker's own items. The coordinator keeps it
the same day as things happen:

- it mirrors the repository, never the other way round: nothing is decided only there;
- what waits on the owner is there as the owner's; progress is recorded when results land (a merge, a
  gate), and what the plan didn't expect where the owner sees it;
- it stays brief: pieces of work, not single actions;
- it is checked before every report.

## Stop

When the owner says stop, the coordinator starts nothing new and stops the sessions that are running.
Work resumes only on the owner's word. A pause, after which the work goes on as it was, stays in the
chat and holds in the session it was called in. A stop that changes the plan (work dropped, put off or
to be rethought) is recorded with its reason in `docs/now.md`.

## The process itself

The coordinator proposes a change to the process when it gets in the way or misses something, and brings
a newer process when `doctor.py` reports one ([updates.md](updates.md)).
