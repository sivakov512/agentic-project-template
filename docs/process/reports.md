# Reports to the owner

Whenever there is something for the owner (one or more pull requests ready to merge, pull requests it
merged on its own since the last report, or a gate), the coordinator reports, in this order:

1. **Where we are:** the stage and the next step.
2. **Summary:** two or three lines on what was done and why.
3. **How it was checked.**
4. **Decisions the coordinator made itself,** one line each, so the owner can reverse any of them.
5. **Deviations from the plan, and risks,** if any.
6. **What is needed from the owner:** for each pull request that needs the owner's OK (labelled
   `owner-review`, or a bot's with no review label), what to look at, a link and how many minutes; the questions, each with a recommendation; then the pull requests merged
   without the owner, one line each.
7. **The tracker:** one line on what changed there, if the project has one.

Settings the owner must change are given as a path of clicks with links (Settings → Branches → `main`
→ …), not as commands to run.

## When the owner looks

The owner agrees where the work goes and checks what it gives; the agents do the rest. The owner looks
at:

1. **The plan of each increment,** at the gate before it: what the owner gets, what is in and out, the
   big steps, which decisions it will bring to the owner, and its risks.
2. **The decisions that plan names as the owner's,** each when it is ready: what a person will use or
   work with (the interface, an API or a driver others program against, a file or data format a person
   reads or writes, a command line, settings), what shapes the whole product (the architecture, the
   stack, the model of the data), and what is hard to reverse. `docs/plan.md` may name more. A decision
   of these kinds that the plan didn't name goes beyond the plan (4).
3. **The result of each increment,** by using it ([workflow.md](workflow.md#stages-and-gates)).
4. **What goes beyond the agreed plan:** a change of scope, sizeable work the plan didn't foresee, a
   problem, a risk or a blocker, an action on the owner's real data (a migration run on it, moving or
   deleting it), and what only the owner can do (accounts, money, hardware, settings). Code that may do
   such things is risky code (below), not this point.
5. **The rules of the work:** what the owner keeps for themself
   ([workflow.md](workflow.md#the-owners-ok-and-the-merge)): `CLAUDE.md`, the plan, the settings and the
   commands of the checks, CI and the process, and any change that loosens the project's checks,
   whatever file it is in (a test removed or skipped, a lint rule or a threshold eased). The template's
   files a process update brings exactly as in the template's release are the exception: the owner
   agreed them in the template.

A pull request for 1, 2, 4 or 5 is labelled `owner-review`; it says in plain words what it decides or
changes, and for the checks and CI what it loosens or tightens. Everything else is labelled
`ok-without-reading` and the coordinator merges it on its own: the requirements and the documents of
the chain inside the agreed scope, studies, code and tests, interfaces between parts that only the
agents build, the backlog, `docs/now.md`, records of facts, and records of the owner's own decisions
outside what the owner keeps. A bot's pull request the coordinator labels after its review: a
dependency bump inside the plan `ok-without-reading`, a release as the plan's Releases section says.

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
