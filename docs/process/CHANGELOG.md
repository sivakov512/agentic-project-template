# Changelog

The newest version first. Each entry says what changed and what projects must do, if anything
([updates.md](updates.md#changing-the-process)).

## 0.7.0 — 2026-11-05

From an independent review of 0.6.0 and the owner's decisions on it.

Merging and pull requests:

- Squash merge. `main` gets one commit per pull request, its subject the pull request's title and
  " (#N)", its body empty; the coordinator merges with the REST API (`workflow.md`, step 7). On the
  branch, fixes are plain new commits and nothing pushed is rewritten; a conflict is resolved by
  merging `main` into the branch, and resolving it is not a review round. A second-round reviewer
  reads `git diff <reviewed> <new>`, or with a merge of `main` in between, `git log -p --first-parent
  --remerge-diff`.
- The title is the future commit subject: `process-commits` checks it against the commit rules, the
  " (#N)" counted in its 72 characters, instead of the branch's commits. It keeps its name, moves into
  `process-pr.yml` so a title edit runs it again, and reads the pull request only. `one_line` and
  `no_co_authors` in `docs/process.json` are still accepted and do nothing.
- One label: the review label, `owner-review` or `ok-without-reading`; other labels are not read. The
  kind is in the title: `Plan:`, `Spec:`, `Research:`, `Code:`, or with Conventional Commits
  `docs(plan): ...`, `docs(spec): ...`, `docs(research): ...`, and `feat`, `fix`, `refactor` and the
  like for code. `update.py` titles its pull request `chore: ...` there.
- A pull request whose "Backlog item" is `Coordinator record` or `Process update` needs only "Backlog
  item", "What changed" and "Owner review"; `update.py` writes just those. `check_pr.py` also takes a
  bare "None" in "Not done and open questions" and a Coordinator record that names several items.
- A passing `process-pr` or `process-owner` runs again only the failed jobs of the red runs on the same
  commit.

Reviews:

- Every review posts one comment of the same shape: its name and the head, its sections, the findings
  marked fix or drop, and a last line "Ready to merge as is: yes" or "no" (`rules.md`, "Every review").
- An architecture review for a pull request that changes the architecture or a contract between parts,
  with the contributor test, and a UI review for one that changes what a person sees and uses
  (`rules.md`, "If you are the reviewer"). A project with a user interface keeps a design-system
  document in its chain. `workflow.md` step 5 says which pull requests get which reviews; the
  coordinator decides, and the plan may name more.
- Risky code, architecture and contract changes, UI changes, and decisions of the owner's kinds the plan
  didn't name are offered to the owner once their reviews have no "fix" finding left: one item of
  "Needed from you" with what it does, the reviews and checks passed, what is worth a look and that it
  may be skipped, and the question whether to stop such offers until the milestone's end; after a stop
  the coordinator merges that kind and lists it. A stop is a line in `docs/now.md` until the milestone
  ends; what the plan names as the owner's has no stop option (`reports.md`, "Reviewed work offered to
  the owner").
- A reviewer's "fix" for a problem the pull request didn't cause and its item doesn't cover is marked
  "outside the item": the fixing session lists it under "Not done and open questions", and the
  coordinator makes it an item. A loosened check or a too weak review label is a "fix".
- A pull request with no item has a bar for its reviewer: `setup.md` and the owner's answers for Setup,
  its description and `updates.md` for a Process change, the owner's words and the documents above for
  a Coordinator record.
- `workflow.md` step 5, "Review and checks", opens with the two pull requests that need no reviewer.
  The coordinator may close a finding of an ordinary review that rests on something untrue or
  contradicts the item or the plan, with the reason, and reports it as its own decision; findings of
  the review for harm stay its reviewer's, and the review for harm wins when reviews disagree.
- The owner's remarks on an open pull request go to a work session as "fix" findings quoting the owner,
  with one review of the fix (and one review for harm of it for risky code), outside the two-round cap.

What the owner keeps:

- The owner also keeps `.claude/` folders, `.mcp.json`, and `CLAUDE.md` and `CLAUDE.local.md` in any
  folder, names compared whatever their case. A new optional key `kept` in `docs/process.json` lists
  patterns of paths the owner keeps too, read from the base branch: the configuration of the project's
  checks and anything else the owner names (`config.md`). Two things fail `process-owner` whatever the
  approvals: a symlink or submodule at a kept path or at a folder on the way to one; and rules Claude
  Code loads by itself (a `CLAUDE.md` or `CLAUDE.local.md` in any folder, `.claude/rules/`), or the
  files they import in turn, that import (an `@` before the path) a symlink, a submodule, a path through
  one, or a file the owner doesn't keep. Commands, skills, agents and other documents may import
  anything.
- What the owner keeps is defined once, in `workflow.md`, "The owner's OK and the merge": the files CI
  holds, with the process update exception, and any change that loosens a check.
- `process-owner` takes `agents_account` from the pull request itself only while the base has none
  (setting up), and `owner` there only when the pull request's author is the repository's owner.

Releases of the template and updates:

- The template's releases are made by its workflow `template-release.yml` on merge to `main`, not by
  hand; it fails red when the version's tag exists already off `main` or without a release. The owner
  keeps a tag ruleset on `v*`. Projects don't get the workflow, and its copy in a project does nothing.
- A release counts only when its tag is on the template's `main`: `process-owner` lets in no files of
  another, and `update.py` stops before running anything of it.
- "When a release breaks the project" (`updates.md`): the coordinator reverts the update's commit in a
  pull request for the owner, who removes `process-lock` (and `process-owner`, if it is what broke) as
  a required check for that one merge.
- An update `update.py` sends to the owner because of `.github/` says in "Owner review" that an Approve
  is all it needs, and why GitHub asks.
- The template's files never write an `@` right before a path, since `process-owner` would read it as
  an import in every project.

The coordinator, the plan and setup:

- One rule for recording the owner's words, in `workflow.md`: what the owner decides or asks for becomes
  a record the same day, quoting the owner's words as said; a choice the words didn't make is reported
  as the coordinator's decision. What holds only for the session (a pause, an answer) stays in the chat.
- Rules every session keeps live in `CLAUDE.md` only, since work sessions and reviewers read only the
  parts of `docs/plan.md` their item leads them to. The plan placeholder's section "The owner's rules"
  becomes "Working with the owner"; a project may keep its own name and anchor.
- A coordinator session starts no session and no merge before its first report and the owner's
  answer to it; it takes over drafts whose sessions are gone; `docs/now.md` always holds what a fresh
  coordinator needs. It starts or messages sessions by the tools it has, or asks the owner, and checks
  the pull requests it asked the owner about before every reply.
- While `main` is unprotected or a process check isn't required, the coordinator merges nothing whose
  `process-owner` run isn't green, and the settings stay first in "Needed from you".
- Before a merge the checks have run on the current `main`: if `main` moved, the pull request is closed
  and reopened, which keeps the owner's Approve. A red `main` is fixed first, on an item of its own for
  code. A wrong merge is reverted in a pull request that names the item, takes its kind and label, and
  reopens the item; its reviewer checks only the revert.
- Dropping or moving out an item of the agreed milestone is a change of scope, the owner's.
- `docs/now.md` gets "Reported up to", the commit the last report covered, so the list of merges without
  the owner survives a new session.
- Setup: the account question first, and step 1 only once it is answered; the agents' own account
  recommended, run where only their account is signed in; no bypassing in both modes; squash-only merge
  settings; secrets that publish, deploy or mint tokens in an Environment limited to `main`, with
  publishing on the push to `main`, or also on release tags `v*` where a tag ruleset stops the agents'
  account from creating, moving or deleting them; a warning on `CI_RUNNER`. The README says what each
  account choice costs, what the owner will be asked, and that the repository is in English.
- `doctor.py` fails when gh works as the repository's owner with `agents_account` `own`, or as someone
  else with `owner`; when the repository is public and `CI_RUNNER` is set; when classic protection
  lets admins past its checks; and when the merge settings, or a ruleset's allowed merge methods, don't
  give squash only. With rulesets, whose bypass list only an admin can read, it reminds the owner to
  check it. `--fix-labels` creates only the review labels.
- Backlog items stand under a heading per milestone. A work session reads its item and the documents it
  links, and looks further up the chain only for a question they leave.

Projects: in this order.

1. Before the update: a symlink or submodule at a kept path (a `CLAUDE.md -> AGENTS.md`, say) becomes a
   plain `CLAUDE.md` that imports `AGENTS.md` (an `@` before the name), and a `CLAUDE.md`,
   `CLAUDE.local.md` or `.claude/rules/` file that imports a file the owner doesn't keep gets that file
   into `kept`, or imports a plain file instead; otherwise every pull request fails `process-owner`
   after the update. This may also go in the update itself.
2. Where `docs/process.json` asks for Conventional Commits, the coordinator retitles the update
   `chore: update the process to 0.7.0`, or its `process-commits` stays red.
3. In the update: the rules every session must keep move from `docs/plan.md` to `CLAUDE.md` (the plan
   may keep its section's name and anchor); `docs/now.md` gets a line "Reported up to: <commit>";
   backlog items go under a heading per milestone; a project that keeps its own architecture or UI
   review rules in `CLAUDE.md` drops them. These changes make the update go to the owner.
4. The coordinator asks the owner, in one request with the update's Approve, for Settings > General >
   Pull Requests: untick "Allow merge commits" and "Allow rebase merging", tick "Allow squash merging",
   default commit message "Pull request title"; where a ruleset protects `main`, Settings > Rules >
   Rulesets > the ruleset for `main` > Require a pull request before merging > Allowed merge methods:
   Squash only; and no bypassing for `main` ("Do not allow bypassing the above settings", or no bypass
   list), with the agents' own account too. From then on nothing merges by rebase.
5. Once `doctor.py` shows the settings, the coordinator merges the update first, by squash with the
   command of `workflow.md`, step 7.
6. The coordinator deals with what `doctor.py` now fails: the agents sign gh and git in as the account
   `agents_account` names, or the owner corrects the setting; on `CI_RUNNER` in a public repository the
   owner deletes the variable or makes the repository private. With the agents' own account, it makes
   sure the owner's login is not reachable where the agents run (`gh auth status`, the credential
   helper, the environment) and tells the owner if it is.
7. The owner moves secrets that publish, deploy or mint tokens into an Environment limited to `main`,
   together with a pull request in which the jobs that use them name the Environment and publish on the
   push to `main`, or on release tags `v*` that a tag ruleset keeps from the agents' account
   (`setup.md`, step 8); one without the other fails the release.
8. Where the project asks for Conventional Commits, each open pull request is retitled as a
   Conventional Commits subject, or its `process-commits` turns red on its next event. Their kind
   labels do no harm; the owner may delete `plan`, `spec`, `research` and `code` (Issues > Labels).
9. `kept` is optional: when the project has check configuration, the coordinator proposes its patterns
   to the owner in the pull request that adds the first of it.
## 0.6.0 — 2026-11-05

- A report to the owner fits on a phone's screen, about twelve lines, detail left in the pull requests.
  Its points: where we are; what is in work now; what changed, each with how it ended (a fact without
  its outcome isn't written), then the pull requests merged without the owner; decisions made alone,
  deviations and risks; and last, what is needed from the owner. That opens with a call and gives a
  numbered item per action, each with its link, what it decides, why it is the owner's, what to look at
  and for how long (or why no reading is needed), and for risky code what could break and what guards
  it; or one line that nothing is needed. Points with nothing to say are left out, all but the last.
  When a report runs longer, the earlier points get shorter, never an item of the last one.
- The report's line on the tracker is gone: `docs/plan.md` may add points of the project's own, the
  tracker's among them, before the last one; `coordinator.md` and the `docs/plan.md` placeholder say so.
  What waits on the owner in the tracker carries what the report's last point gives, instead of a
  checklist of its own.
- The owner asking for the status gets a report in this form, even with nothing new. Any other answer in
  a conversation stays a plain answer, and any message ends with what waits on the owner, if something
  does.
- Whether the owner is needed is decided by the rules, not asked of the owner; the one question about it
  is a doubt whether something stays inside the plan.
- A new item in what is needed from the owner also gets a notice outside the chat (a push), once, never
  for a repeat or for "nothing".
- `setup.md`: a tool that opens pull requests for releases runs with a GitHub App's token, as
  `pull-requests.md` already required.
- `coordinator.md`, "Stop": a pause the owner calls, with the work to go on as it was, stays in the chat
  and holds in the session it was called in, until the owner's word there or a new coordinator session;
  only a stop that changes the plan is recorded in `docs/now.md`. The owner closed a pull request that
  recorded a pause: "it's not permanent, just paused for now".
- Tried on the four projects' coordinators on 2026-11-03 to 2026-11-05 at the owner's request. From the
  trial the owner asked for the outcome of each point, the reason the owner is needed and what to look
  at, the work in progress, a short report, and the same report when asking for the status; with that,
  the owner had it made a rule.
- One word for a piece of the plan: milestone. The foundation is the first milestone, and each one after
  it ends with something the owner uses; "stage" and "increment" are gone from the process, and
  `workflow.md`'s section is now "Milestones and gates". The owner asked for it: two words confused the
  coordinators, and "milestone" is the common term in project management. Inside a milestone the work is
  still backlog items.

Projects: to keep a line on the tracker in reports, the coordinator proposes it to the owner in
`docs/plan.md`, section Tracker. A release tool that opens pull requests with the agents' token moves to
a GitHub App the owner makes. The project renames "stage" and "increment" to "milestone" in its own
documents (`docs/plan.md` with its section "Stages", `docs/now.md`, `docs/backlog.md`, `CLAUDE.md`) and
points its links to `workflow.md#stages-and-gates` at `#milestones-and-gates`, or the docs check fails
on them; that is in the update's pull request, which then goes to the owner, since `docs/plan.md` is the
owner's.

## 0.5.4 — 2026-11-04

- `coordinator.md`, "Before a gate": a step to write out the next stage in `docs/plan.md`, as
  `workflow.md` says, before the reviewer and the cold-start test, and to give it to the owner with the
  gate. `workflow.md` had the rule; the gate's checklist didn't name it, and a stage written as one line
  went unnoticed.
- What a written-out stage holds is said once, in `workflow.md`: what it delivers (for an increment,
  what the owner gets and what is in and out), its big steps, the owner's part and the decisions it
  brings to the owner, its risks, its exit list, and what it builds on. `reports.md` (the owner looks at
  the plan of each increment) and the `docs/plan.md` placeholder link there instead of listing parts of
  it, each a different part.
- Wording that no longer matched the process: the README says an update comes to the owner only where it
  changes what the owner keeps; `updates.md` says `update.py` picks the review label; the docstrings of
  `sync.py` (run by `update.py`), `check_docs.py` (it also checks `docs/process.json`) and
  `check_owner.py` (whose release vouches for an update).

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
