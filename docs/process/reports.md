# Reports to the owner

Whenever there is something for the owner (one or more pull requests ready to merge, pull requests it
merged on its own since the last report, or a gate), the coordinator reports. The whole report fits on a
phone's screen, about twelve lines; detail stays in the pull requests, which it links. In this order,
each point left out when it has nothing to say, all but the last:

1. **Where we are,** one line: the milestone and the next step.
2. **In work:** what is going on right now, one line per item or pull request and what it does.
3. **What changed,** one line each, every one saying how it ended: fixed and merged, not fixed and what
   it waits on, checked and how. A fact without its outcome isn't written. Then the pull requests merged
   without the owner since the commit `docs/now.md` gives as "Reported up to", one line each; the
   coordinator's next record of `docs/now.md` moves that line to the last merge the report listed.
4. **Decisions the coordinator made itself,** so the owner can reverse any of them, **deviations from the
   plan, and risks,** one line each.
5. **What is needed from the owner,** opening with a call ("Needed from you:"), then a numbered item per
   action: an approval, a question with a recommendation, a milestone to try, a setting to change,
   anything only the owner can do. Each item gives the action and its link; what it decides, in plain
   words, one line; why it is the owner's and not the coordinator's, by the rule that makes it so
   ("When the owner looks" below, or what [workflow.md](workflow.md#the-owners-ok-and-the-merge) keeps
   for the owner); what to look at and how many minutes, several places as a list with links, or that no
   reading is needed and why; and for risky code, what could break and what guards it. Or one line that
   nothing is needed.

When the report runs longer, the earlier points get shorter; each item of the last one keeps all its
parts. `docs/plan.md` may add points of the project's own, all before the last one (a line on what
changed in its tracker, say).

The owner asking for the status gets a report in this form too, whether or not anything is new since the
last one; where the owner asks for more, the points grow and keep their order. Any other answer in a
conversation with the owner stays a plain answer. Whatever the message, what waits on the owner comes at
its end, since the owner reads the chat from the bottom. Whether the owner is needed is decided by these
rules, not asked of the owner; the one question about it is a doubt whether something stays inside the
plan (below).

When what is needed from the owner gains an item the last notice didn't have, the coordinator also
notifies the owner outside the chat, where its tools can (a push notification): once per message, one
line with the project and what is needed. A request the owner hasn't answered yet, "nothing", and news
along the way get no notice.

Settings the owner must change are given as a path of clicks with links (Settings → Branches → `main`
→ …), not as commands to run.

## When the owner looks

The owner agrees where the work goes and checks what it gives; the agents do the rest. The owner looks
at:

1. **The plan of each milestone after the foundation,** at the gate before it, written out as
   [workflow.md](workflow.md#milestones-and-gates) says.
2. **The decisions that plan names as the owner's,** each when it is ready: what a person will use or
   work with (the interface, an API or a driver others program against, a file or data format a person
   reads or writes, a command line, settings), what shapes the whole product (the architecture, the
   stack, the model of the data), and what is hard to reverse. `docs/plan.md` may name more. A decision
   of these kinds that the plan didn't name goes beyond the plan (4).
3. **The result of each milestone after the foundation,** by using it
   ([workflow.md](workflow.md#milestones-and-gates)).
4. **What goes beyond the agreed plan:** a change of scope (an item of the agreed milestone dropped or
   moved out of it; one superseded by an item with the same aim is not), sizeable work the plan didn't
   foresee, a problem, a risk or a blocker, an action on the owner's real data (a migration run on it, moving or
   deleting it), and what only the owner can do (accounts, money, hardware, settings). Code that may do
   such things is risky code, as `docs/plan.md` names it (below), not this point.
5. **The rules of the work:** what the owner keeps for themself
   ([workflow.md](workflow.md#the-owners-ok-and-the-merge)).

A pull request for 1, 2, 4 or 5 is labelled `owner-review`; it says in plain words what it decides or
changes, and for the checks and CI what it loosens or tightens. Everything else is labelled
`ok-without-reading` and the coordinator merges it on its own: the requirements and the documents of
the chain inside the agreed scope, studies, code and tests, interfaces between parts that only the
agents build, the backlog, `docs/now.md`, records of facts, and records of the owner's own decisions
outside what the owner keeps. A bot's pull request the coordinator labels after the reviewer's
findings and its own check: a dependency bump inside the plan `ok-without-reading`, a release as the
plan's Releases section says.

Code `docs/plan.md` names as risky goes as OK without reading only where the plan says so, once
neither its review nor its review for harm has a "fix" finding left
([workflow.md](workflow.md#how-a-piece-of-work-goes)).

When the coordinator isn't sure whether something stays inside the plan, it asks the owner in one line
in the report, with its recommendation, instead of sending the whole pull request to be read, and holds
that pull request until the answer; the rest goes on. It never
moves a kind of work off the owner's list on its own; only the owner can, by a change to the plan.

## Batching

Questions to the owner come in a batch, each with
the coordinator's recommendation.
