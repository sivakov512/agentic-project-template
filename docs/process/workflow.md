# How work goes

## How the repository works

- **The repository is the only source of truth.** What is not on `main`, or in an open pull request
  under review, is not decided ([rules.md](rules.md#where-you-get-information)).
- **Upstream first.** The project's documents depend on each other in the order of the document chain
  in `docs/plan.md`, ending with the backlog and the code ([changes.md](changes.md)).
- **Interfaces before the work on either side.** Where different items build parts that meet (a data
  schema, an API, a protocol, a file format, a pinout, a document's structure), the meeting point is
  written down, with every name, field and limit the sides rely on, before those items start. It is
  written once, where the document chain says: in a form the parts are built from or checked against
  when there is one (a schema file, an API description), otherwise in a document; documents above it
  explain it in plain words and link to it. Only when one item builds both sides may it be left to the
  code.
- **No work without a backlog item.** Pull requests that are not product work say what they are instead
  ([pull-requests.md](pull-requests.md#the-description)).
- **What the owner decides or asks for becomes a record the same day:** a rule in the plan, a decision
  record, a change to a document, or a backlog item, in a pull request, which is the record until it is
  merged ([changes.md](changes.md)). Its description quotes the owner's words as said next to what it
  records; a choice the words didn't make is a decision of the coordinator's, which the next report
  names ([reports.md](reports.md), point 4). What holds only for the session (a pause, an answer to a
  question) stays in the chat ([coordinator.md](coordinator.md#stop)).

## Milestones and gates

The work goes in milestones, which `docs/plan.md` lists:

- **The foundation,** the first milestone, once and short: what the product is for and for whom, the
  owner's main scenarios, the limits; research only where a decision can't be made without it; the
  technologies and the frame of the design only as far as the next milestone needs. For a product that
  exists already, it also holds an inventory of what the product does and checks that it still does it
  (tests, for code), where these don't exist yet, for the parts the next milestone touches; each later
  milestone adds them for the parts it touches.
- **The milestones after it,** one after another, each ending with something the owner uses: a build, a
  document, a board, whatever the project makes. Each says what the owner gets from it in their real
  work: something they can do that they couldn't, or, for a step of a rebuild, a part of the product
  they use running on the rebuilt part, checked. Inside it: the requirements, research, design and
  interfaces for that scope only, and the items that build it; everything else goes to the list for
  later. The first milestone after the foundation of a new product is its smallest version the owner can
  use. For a product that exists, each milestone changes the working product, and a rebuild goes as a
  series of milestones, each leaving it working.

### Writing a milestone out

Each milestone is written out at the end of the one before it, from what is known by then, in
`docs/plan.md`, concrete enough to write its items from:

- what it delivers (after the foundation, what the owner gets from it, and what is in and out);
- its big steps;
- the owner's part and the decisions it will bring to the owner
  ([reports.md](reports.md#when-the-owner-looks));
- its risks;
- everything it builds on (documents, interfaces, the technologies it uses), each either decided and
  written down already or settled at the milestone's start, before the work that depends on it;
- its exit list, which always includes that every backlog item of the milestone is merged or dropped
  with a reason, and after the foundation that the owner has used the milestone in real work and it is
  released as `docs/plan.md` says.

This change to the plan goes to the owner in the same report as the gate.

### Starting and finishing

- An item starts only when everything it depends on is merged and its milestone has started; an item
  whose "Depends on" says "any time" may start whatever its dependencies and milestone. A milestone starts when the previous one is
  finished and its own written-out plan is merged.
- A milestone is finished only when every point of its exit list is true.
- A milestone after the foundation ends in this order: the coordinator runs the result end to end and
  gives it to the owner ready to try, with the steps; the owner uses it in real work and says what came
  up; what must be fixed for it to do its job is fixed in this milestone, the rest goes to the next one
  or the list for later. Meanwhile the coordinator writes out the next milestone.
- **A gate** ends every milestone: the owner accepts what the milestone delivered and agrees the next
  one. Agreeing it lets the coordinator start the work sessions and reviewers for its items without
  asking again; where its tool starts a session only on the owner's word, the coordinator asks for that
  word together with the plan. The coordinator brings no gate to the owner while any point of the exit
  list is open or unchecked, and prepares it as [coordinator.md](coordinator.md#before-a-gate) says.

### A project already under way

A project adopting the process, or taking this shape in an update, brings its plan into it:

- what of the old plan is done stays as it is;
- a current part that already ends with something the owner uses becomes a milestone and stays; one
  that doesn't is cut to what the next milestone needs and closes the foundation;
- the parts after it become milestones, a line each, with the rest in the list for later;
- backlog items left outside go to the list for later; an open pull request left outside is the owner's
  to keep or close.

### The list for later

The section "Later" at the end of `docs/backlog.md` holds what is left out of the milestones so far, a
line each; the coordinator adds to it in a coordinator record. Moving work of the agreed milestone there
is a change of scope ([reports.md](reports.md#when-the-owner-looks), point 4). A backlog item moved there
is dropped with the reason "moved to the list for later"; a milestone takes its work back from there as
new items.

## How a piece of work goes

1. **The item** exists in the backlog ([changes.md](changes.md#the-backlog)) and may start. If a session
   would need more than the item to do it, the coordinator fixes the item first; an item that is clearly
   large is split before a session starts on it. One found too large once its pull request is open is
   split on its branch: the coordinator commits the split to `docs/backlog.md` there; the first part
   keeps the ID, with a narrower "Done when", and the pull request, its kind and its label; the other
   parts get new IDs. The report names the split among the coordinator's own decisions. The review of
   the last part reads whole what the parts built ([rules.md](rules.md#the-review)).
2. **The brief** is "Do B-###" and nothing else.
3. **Questions first** ([rules.md](rules.md#your-work)): the coordinator answers in the draft pull
   request, bringing the owner in when a question is the owner's to decide.
4. **The work,** on the item's branch and pull request. Then the pull request leaves draft.
5. **Review and checks.**
   - **Which reviews.** Every pull request gets the review, but two: a coordinator record that changes
     only `docs/now.md` or the backlog (its section "Later" included), and a process update that only
     brings the template's release. A process update whose step 2 also changes project files
     ([updates.md](updates.md#getting-a-newer-process)) gets the review of those changes, against the
     release's "Projects:" steps in the changelog. The review for harm, the architecture review and the UI review come
     on top for the pull requests they are for ([rules.md](rules.md#if-you-are-the-reviewer)), each by
     another reviewer, in the same rounds. The coordinator decides which reviews a pull request gets, by
     these rules and any more `docs/plan.md` names.
   - **Fixes.** One work session ("Fix pull request #N") fixes the findings of all the reviews. The pull
     request merges only with CI green and no "fix" finding left.
   - **At most two rounds:** a full review, then, only if it had "fix" findings, a review of the fix
     alone. Small leftovers of the second round (wording, a link) the coordinator fixes itself; anything
     in the product goes back to a work session. If blocking problems remain after that, the coordinator
     stops, rethinks the item (its approach or its size) and tells the owner.
   - **Risky code.** Any later change to it goes back to the review for harm before the merge, and the
     coordinator never makes such a change itself. If a finding of the review for harm is still open
     after its second round, or a change to the risky code would need a third round, the coordinator
     neither fixes it nor merges, but stops and tells the owner.
   - **Closing a finding.** A finding of the review for harm is closed only by its reviewer. A finding of
     another review that contradicts the item or the plan, or rests on something untrue about the code,
     the coordinator may close, with the reason in a comment on the pull request; the next report names
     it among the coordinator's own decisions. Where reviews ask for opposite things, the review for
     harm wins.
   - **The coordinator's own check:** the diff against "Done when", the running result, and the review
     label against [reports.md](reports.md#when-the-owner-looks) and the decisions the milestone's plan
     gave the owner, corrected if needed. Risky code and decisions of the owner's kinds are then offered
     to the owner ([reports.md](reports.md#reviewed-work-offered-to-the-owner)).
6. **The report to the owner** ([reports.md](reports.md)). The owner discusses the pull request in its
   comments on GitHub, or in the chat when agents work under the owner's account; the coordinator
   answers where the owner wrote. It posts the owner's remarks on the pull request as "fix" findings,
   quoting the owner, after recording first any that change a document above it
   ([changes.md](changes.md)), and starts "Fix pull request #N". That round gets one review of the fix by
   each review the change needs (step 5), outside the two rounds of step 5; what it still finds goes as
   in step 5's second round.
7. **The merge,** by squash: `main` gets one commit, its subject the pull request's title and its
   number, its body empty.
   - After the owner's OK where it is needed ("The owner's OK and the merge" below), the coordinator
     merges with `gh api -X PUT repos/{owner}/{repo}/pulls/<N>/merge -f merge_method=squash -f sha=<the
     last commit> -f commit_title="<the title> (#<N>)" -f commit_message=`. `sha` makes GitHub refuse
     the merge if a commit came after the one checked and approved.
   - The owner, merging on GitHub, keeps what GitHub offers, which the repository's settings make the
     same ([setup.md](setup.md), step 8).
   - If the owner says no, the pull request stays open, and the owner's remarks go as step 6 says.
   - When merges change where the work stands, the coordinator brings `docs/now.md` up to date
     afterwards in a coordinator record, several merges in one, before its next report.
   - **The base.** The checks must have run on the current `main`. If `main` has a commit newer than
     their last runs, the coordinator closes and reopens the pull request, which runs them again on it
     and keeps the owner's Approve (re-running an old run tests its old base).
   - **Conflicts.** `main` is merged into the branch only when it conflicts. A conflict goes to a work
     session as a "fix" finding ("merge `main` in, conflict in X") with "Fix pull request #N". A merge of
     `main` that only resolves conflicts doesn't count as a review round: a reviewer, for risky code the
     reviewer for harm, looks only at how it resolved them ([rules.md](rules.md#every-review)).
   - **A red `main`** is fixed first: a document by the coordinator in a coordinator record, code by a
     work session on an item the coordinator writes for it. That pull request merges ahead of the rest;
     the others wait until `main` is green, and their sessions don't fix it in their own pull requests.
8. **After the merge,** whoever merged, the coordinator records it in the tracker, if the project has
   one.

**A wrong merge** is reverted in a pull request that names the original item in "Backlog item", takes
its kind and review label, and unticks the item in the backlog, which reopens it. Its reviewer checks
only that it reverts that merge's one commit and nothing else and that its checks pass.

## The owner's OK and the merge

**What the owner keeps for themself** is of two kinds:

- the files CI holds for the owner: `CLAUDE.md` and `CLAUDE.local.md` in any folder, any `.claude/`
  folder, `.mcp.json`, `docs/plan.md`, `docs/process.json` and the paths its `kept` names
  ([config.md](config.md#kept)), anything under `.github/`, and the template's files and lock.
  - The one exception is a process update's files that are exactly as in the template's release,
    `.github/` aside with the agents' own account ([updates.md](updates.md#getting-a-newer-process)).
  - A symlink or submodule at any of these paths, or at a folder on the way to one, never goes in,
    approved or not.
  - Nor do rules Claude Code loads by itself (a `CLAUDE.md` or `CLAUDE.local.md` in any folder,
    `.claude/rules/`) that import (an `@` before the path) a file the owner doesn't keep, or a symlink
    or submodule. A `CLAUDE.md` that should say what `AGENTS.md` says imports it, with `AGENTS.md` in
    `kept`;
- any change that loosens the project's checks, whatever file it is in (a test removed or skipped, a
  lint rule or a threshold eased), which only the label and the coordinator hold.

**Which pull requests need the owner's OK:** those labelled `owner-review`, those with no review label
(a bot's, until the coordinator labels it), and every one that changes what the owner keeps. One
labelled `ok-without-reading` that changes none of it the coordinator merges on its own, once its
checks are green, its reviews have no "fix" finding left and the coordinator's own check (step 5) is
done; the next report lists it ([reports.md](reports.md)), and the owner can have any of them reverted.

How the OK works is the owner's choice, in `docs/process.json` ([config.md](config.md#project)):

**Whose account the agents work under** (`agents_account`):

- `own`: a GitHub user account of the agents' own (not a GitHub App), a collaborator with Write
  access, not Admin. The repository then belongs to the owner's personal account, not an organisation:
  `process-owner` counts only the repository owner's approval. The owner's OK is the owner's Approve on
  GitHub of the pull request's last commit, which `process-owner`, required for `main`, checks.
- `owner`: the owner's account. The owner's OK is the owner's word in the chat, since a comment on
  GitHub could be an agent's; the coordinator quotes it in a comment on the pull request before
  merging. `main` still takes changes only through pull requests with green checks, but nothing but the
  rules stops an agent from merging.

**Who merges** (`merged_by`):

- `coordinator`: the coordinator merges once the owner's OK is there; the owner only says yes.
- `owner`: the owner merges. With the agents' own account the owner approves and merges; with the
  owner's account the merge itself is the OK.

Either way:

- Agents never merge a pull request that needs the owner's OK without it, and a commit pushed after the
  OK needs the OK again (with the agents' own account `process-owner` sees to that).
- Before merging, the coordinator checks the OK itself, not from a retelling: the Approve on the pull
  request, or the owner's own words in the chat, quoted as said.
- The setting-up session counts as the coordinator for the setup pull request. In the template itself,
  the coordinator merges after the owner's Approve, as in a project with the agents' own account.
