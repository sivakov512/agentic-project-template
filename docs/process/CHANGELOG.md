# Changelog

The newest version first. Each entry says what changed and what projects must do, if anything
([updates.md](updates.md#changing-the-process)).

## 0.5.4 — 2026-11-04

- `coordinator.md`, "Before a gate": a step to write out the next stage in `docs/plan.md`, as
  `workflow.md` says, before the reviewer and the cold-start test, and to give it to the owner with the
  gate. `workflow.md` had the rule; the gate's checklist didn't name it, and a stage written as one line
  went unnoticed.

Projects: nothing to do.

## 0.5.3 — 2026-11-03

- The docs check finds a backlog item whose title opens with inline code (``**B-021** `tool check` …``).
  Before, it saw no item there and said "B-021 is defined nowhere" wherever the ID came up.

Projects: nothing to do.

## 0.5.2 — 2026-11-03

- `process-pr` reads the pull request from the API when it runs, not from the event, has no concurrency
  group, and a passing run runs again the red ones on the same commit, as `process-owner` does. Before, a
  run from the pull request's opening, cancelled by the next event or red for labels not set yet, kept
  the merge waiting ("process-pr is expected") until someone ran it again.

Projects: nothing to do. The update changes `.github/workflows/process-pr.yml`, so with the agents' own
account it goes to the owner. A pull request left with a red `process-pr` run from before 0.5.2 needs a
new commit (a rebase onto `main` will do): running the old run again repeats the old check on the old
event.

## 0.5.1 — 2026-11-03

- `process-owner` reads the pull request's labels when it runs, not from the event that started it, and
  runs the check from the base branch as it is now, not as it was at the pull request's last push. A run
  left red by an earlier event (a review given while the labels were different) stays red until it is
  run again, and now running it again brings it up to date; `pull-requests.md` says how.
- `process-owner` runs have no concurrency group any more: a run cancelled by a newer event counted as
  failed for the merge.
- A passing `process-owner` run runs again the red ones on the same commit. Before, a pull request that
  needed the owner's OK stayed blocked after the Approve: the run from its last push, red for want of
  the OK, still counted until someone ran it again.

Projects: nothing to do. The update changes `.github/workflows/process-owner.yml`, so with the agents'
own account it goes to the owner (`update.py` labels it `owner-review`).

## 0.5.0 — 2026-11-02

- The work goes in increments, each ending with something the owner uses. The first stage is a short
  foundation (for a product that exists, with an inventory and checks where they are missing); each
  later stage is an increment: what the owner gets from it, requirements and design for that scope
  only, the items, the owner using the result in real work, its release. A rebuild goes as a series of
  increments, each leaving the product working. Everything else waits in the list for later, a section
  at the end of `docs/backlog.md` the coordinator keeps without the owner.
- An increment ends with the owner trying it before its gate; the coordinator writes out the next one
  meanwhile. Every stage ends with a gate where the owner agrees the next increment.
- Setting up writes the foundation in full and the increments as a line each; adopting the process
  brings the plan into this shape too.
- The owner looks where the work's direction is decided, not at every step (`reports.md`, "When the
  owner looks"): the plan of each increment; the decisions it names as the owner's (what a person will
  use or work with, what shapes the whole product, what is hard to reverse); the result of each
  increment; what goes beyond the plan; and the rules of the work (`CLAUDE.md`, the plan, the settings,
  CI, the process). A doubt is a one-line question in the report, not a whole pull request to read.
  Agreeing an increment's plan lets the coordinator start the sessions for its items on its own. A
  question holds its pull request until the answer. A change that loosens the project's checks, in
  whatever file, is the owner's. The coordinator checks every review label before merging, labels bots'
  pull requests after its review, and brings `docs/now.md` up to date after merges, several at once.
  Every pull request gets a reviewer but coordinator records of `docs/now.md` or the backlog and plain
  process updates.
- Code: behaviour the code adds or changes is covered by automated tests where the project can run
  them.
- The coordinator merges everything else on its own once checks and reviews pass, and the report lists
  it. A new required check, `process-owner`, holds this: a pull request labelled `owner-review` or with
  no review label, or one that changes `CLAUDE.md`, `docs/plan.md`, `docs/process.json`, anything under
  `.github/` or the template's files, needs the repository owner's approval of its last commit; agents
  never approve. `process-owner` runs the check from `main`'s copy, and with the agents' own account
  `.github/CODEOWNERS` gives the owner `.github/`, so a pull request can't rewrite the check that guards
  it. A process update that is exactly the template's release is the exception (one that changes
  `.github/` still waits for the owner), and
  `update.py` labels it `ok-without-reading`; `process-lock` no longer asks for a label. With the
  agents' own account `process-owner` takes the place of GitHub's required approval.
- Editing a pull request's description or labels reruns only the check of the description and the labels
  (the new `process-pr.yml`), not the documents' check with the tests. The checks keep their
  names, so the required checks don't change.

Projects: in the update pull request, or as the next item, the coordinator brings the plan's stages
into this shape as `workflow.md` says for a project already under way, and the owner reviews it; a
list for later in the plan moves to the section "Later" of `docs/backlog.md`. A project that keeps
`docs/now.md` up to date in each pull request may stop doing so.

The owner, in the repository's settings (Settings → Rules → the ruleset for `main`, or Settings →
Branches): add `process-owner` to the required checks and, where the agents have their own account, set
required approvals to 0 and tick "Require review from Code Owners" and "Dismiss stale pull request
approvals when new commits are pushed"; until then what is OK without reading still waits for an
approval. With the agents' own account, the coordinator adds `.github/CODEOWNERS` as `setup.md`, step
8, says, in the update pull request (which this release's `.github/` changes send to the owner
anyway). Where the
agents work under the owner's account there is no required approval to remove, so the coordinator
merges what is OK without reading from the update on, and `process-owner` guards the label once it is
required. An open pull request gets the check at its next push or label change; until then a required
`process-owner` shows as expected. `doctor.py` says when the settings are done. The description of the
label `ok-without-reading` can be edited to the new one (Issues → Labels).

## 0.4.0 — 2026-11-02

- A review for harm: code that `docs/plan.md` names as risky (it handles a secret, or acts on the
  owner's machine, on infrastructure or on data that can't be restored) gets a second, independent
  review, run at the same time as the usual one. Its reviewer reads no other findings before posting
  its own, hunts for concrete ways the change does harm, and says whether the change is safe to merge
  as is. One fix session answers both reviews. The pull request merges only when neither review has a
  "fix" finding left; one the review for harm still has after its second round goes to the owner.
- Such code is Review, unless the project's plan lets it go as OK without reading after both reviews.

Projects: a project with such code names it in "Owner review" of `docs/plan.md`, with whether it then
goes as OK without reading: a change to the plan the owner reviews, in the update pull request or as
the coordinator's next item. Until then nothing changes. A rule of the project's that only repeats this
one is removed. Open pull requests with code so named get a review for harm before their merge.

## 0.3.0 — 2026-11-02

- The reviewer gives a verdict on three points in every pull request that changes the work: understood
  by a person, fits the design, easy to change. Falling short on any is a "fix" finding.
- Code: every module opens with a plain explanation of what it is for and where it sits in the design;
  everything it offers to others says what it does, its inputs, its results and failures, and its
  errors; a link to a document adds to the explanation, never replaces it. The design document lists
  the code's folders, a new folder goes there before the work that makes it, and a project check fails
  on a folder missing from it.
- A pull request's history is what lands on `main`: fixes are folded into the commits they correct and
  force-pushed with lease; the second round reviews the range-diff from the head the first round
  reviewed to the new one.
- An item found too large once its pull request is open is split on that pull request's branch; the
  first part keeps the ID and goes on there, with the pull request's kind and label unchanged.
- `updates.md` says plainly that in 0.x new rules raise the minor version too.

Projects: a project with code, in the update pull request, names in `docs/plan.md` the document of the
code's design, lists the code's folders there, and adds to its checks the folder check and, where the
language has one, a linter for code comments; if that is too much for one pull request, the
coordinator makes it the next item, before any other code. Open pull requests with code follow the new
rules before their merge ("Fix pull request #N"). Existing modules get their comments when a pull
request changes them. A project without code: nothing to do.

## 0.2.2 — 2026-10-28

- Each stage is written out in `docs/plan.md` at the end of the one before it, from what is known by
  then, with everything it builds on (documents, interfaces, technologies) named and either written
  down already or settled at its start.
  It goes to the owner in the same report as the gate or the stage's last pull requests, so there is
  no new interruption, and the stage starts once it is merged.
- Interfaces between parts that different items build (a data schema, an API, a protocol, a pinout)
  are written down before those items start, once: in a form the parts use directly when there is one
  (a schema file, an API description), otherwise in a document. Leaving one to the code holds only when
  one item builds both sides. The owner reviews them, as stack and architecture.
- Setting up names in the document chain where the interfaces are written; later stages may stay
  brief.

Projects: no change to files; the rules hold from the update on. An item that builds one side of an
interface not yet written waits for an item that writes it; the coordinator adds that item when the
current plan leaves an interface to the code. At the end of the current stage, write out the next one.

## 0.2.1 — 2026-10-25

- The template is under the MIT License. The process files carry the notice in
  `docs/process/README.md`; setting up replaces the template's `LICENSE` with the project's own.

Projects: nothing to do.

## 0.2.0 — 2026-10-25

- Every project decides how it ships and writes it down: `releases` in `docs/process.json` (required
  once set up) and a Releases section in `docs/plan.md`; setting up asks for it. The process
  recommends release-please run with a GitHub App's token for projects that ship, but doesn't impose
  it.
- `commits.conventional`: the commit check can require Conventional Commits subjects.
- `doctor.py` reads the required approvals and their dismissal from rulesets.
- Process updates come from the coordinator: when `doctor.py` reports a newer release, it runs
  `tools/process/update.py`, which opens the update pull request. The weekly workflow and its
  `PROCESS_UPDATE_TOKEN` secret are gone: a project nobody works on needs no update.

Projects: 0.1.x's `update.py` runs only in the old workflow, so bring this update by hand once: on a
branch `process-update-0.2.0` from an up-to-date `main`, run `python3 <template>/tools/process/sync.py
<template> .` with the template checked out at `v0.2.0`, commit, and open the pull request as
`updates.md` says, with the title and description `tools/process/update.py` writes (`BODY` there:
"Backlog item: Process update", the changelog entries, "Behaviour change: None"). In the update pull
request, set `releases` in `docs/process.json` (how the project ships, `not yet: <where it is decided>`,
or `none`) and add the Releases section to `docs/plan.md`; until `releases` is set, `process-docs` fails
on it. If the project's commits follow Conventional Commits, set `commits.conventional`, drop the
project's own check of them, and reword the commits of open pull requests that don't match. If
`doctor.py` now flags the approvals for `main`, ask the owner to fix the ruleset (`setup.md`, step 8).
The `PROCESS_UPDATE_TOKEN` secret, if the project has one, can be deleted.

## 0.1.1 — 2026-10-24

- Every comment and review on pull requests is in the owner's language, agents' to each other
  included: the owner reads them. The repository itself stays in English.
- In the template itself, the coordinator merges after the owner's Approve.

Projects: nothing to do.

## 0.1.0 — 2026-10-24

The process of a running agent-driven project, split into the template's part and the project's.

- Rules for agents, roles, stages and gates, how a piece of work goes, pull requests, reports to the
  owner, changes and decision records, the coordinator, defences, the owner's rules.
- Checks: documents (links, backlog, IDs and coverage set in `docs/process.json`, decision records),
  pull request descriptions, commit messages (stricter rules optional), and the lock of the template's
  files, which changes only by moving to a newer version, with the owner's review.
- `doctor.py`, setting up a project or adopting the process in an existing one, the weekly process
  update.
- The "Behaviour change" section, skipping pull requests opened by GitHub Apps, the limit on pull
  request size, found bugs as items of their own.
- The tracker, if any, is chosen at setup and named in `docs/process.json`.
- Each project chooses whether the agents work under an account of their own or the owner's, and
  whether the coordinator or the owner merges.

Projects: nothing to do.
