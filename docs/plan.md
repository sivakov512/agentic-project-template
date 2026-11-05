<!-- template placeholder -->
# Plan

The contract for how this project is made. It changes only through a pull request the owner reviews.
How the process itself works is in [the process](process/README.md); this plan holds only what is this
project's. Where the work stands right now is in [now.md](now.md).

Setting up fills in every section below ([process/setup.md](process/setup.md)).

## Goal

What the project makes, for whom, and when the goal is met.

## Document chain

The project's documents from the top down to the backlog and the code, each with what it holds and the
IDs it defines (they are also in `docs/process.json`), where the interfaces between parts are
written, and, with code, which document describes the code's design and lists its folders. A change starts in the highest one it touches.

## Milestones

The foundation, then the milestones that each end with something the owner uses, all written out as
[the process's rules for milestones](process/workflow.md#milestones-and-gates) say. The milestones not
started yet are a line each until they are written out. What is left out of them waits in the list for
later at the end of the backlog.

## Facts

Where facts found by experiment are recorded, and in what form.

## Owner review

What, beyond [the process's list](process/reports.md#when-the-owner-looks), the owner looks at in
this project. Which code is risky, if any (it handles a secret, or acts on the owner's
machine, on infrastructure or on data that can't be restored), so it gets a review for harm, and
whether it then comes to the owner rather than merging after its reviews.

## Tracker

How the tracker named in `docs/process.json` is kept: how
[the process's rules](process/coordinator.md#the-tracker) map onto its own items (milestones, tasks,
problems or whatever it calls them), how agents reach it, and whether reports to the owner carry a line
on what changed there ([reports.md](process/reports.md)). Or "none".

## Releases

How the project ships, strictly enough that every session does it the same way: what is released
(an app, a package, a deployed service, documents), how versions are numbered, what builds and
publishes a release and where, and who or what starts it. Or "not yet", with where it will be
decided; or "none", with the reason. The short form is `releases` in `docs/process.json`.

## Defences

What could go wrong in this project, beyond [the process's list](process/defences.md), and what stops
it.

## Working with the owner

How the owner wants the coordinator to work with them: how much to disturb them, what to build and not
to build, each with its reason. A rule every session must keep (house style, say) goes in `CLAUDE.md`,
not here: work sessions and reviewers read only the parts of the plan their item leads them to.
