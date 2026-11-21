# How work goes

## How the repository works

- **The repository is the only source of truth.** What is not on `main`, or in an open pull request
  under review, is not decided.
- **Upstream first.** The project's documents depend on each other in the order of the document chain in
  `docs/plan.md`, ending with the backlog and the code. A change starts in the highest document it
  touches ([changes.md](changes.md)).
- **Interfaces before the work on either side.** Where different items build parts that meet (a data
  schema, an API, a protocol, a file format, a pinout), the meeting point is written down, with every
  name, field and limit the sides rely on, before those items start: once, where the document chain
  says, in a form the parts are built or checked against when there is one (a schema file, an API
  description). Only when one item builds both sides may it be left to the code.
- **No work without a backlog item.** Pull requests that are not product work say what they are instead
  ([pull-requests.md](pull-requests.md#the-description)).
- **What the owner decides or asks for becomes a record the same day:** a rule in the plan, a decision
  record, a change to a document, or a backlog item, in a pull request that quotes the owner's words
  ([changes.md](changes.md)). A choice the words didn't make is the coordinator's, and its next report
  names it. What holds only for the session (a pause, an answer to a question) stays in the chat.

## Milestones and gates

The work goes in milestones, which `docs/plan.md` lists:

- **The foundation,** the first milestone, once and short: what the product is for and for whom, the
  owner's main scenarios, the limits; research only where a decision can't be made without it; the
  technologies and the frame of the design only as far as the next milestone needs; for a product that
  ships, how it is released and how the owner tries work before it is released
  ([config.md](config.md#releases)). For a product that exists already, it also lists what the product
  does and makes sure there are checks (tests, for code) that it still does it, for the parts the next
  milestone touches; each later milestone does the same for the parts it touches.
- **The milestones after it,** one after another, each ending with something the owner uses in their
  real work: a build, a document, a board. The first one of a new product is its smallest version the
  owner can use, in the form they will use it. For a product that exists, each milestone leaves it
  working, a rebuild included.

### Writing a milestone out

Each milestone is written out in `docs/plan.md` at the end of the one before it, concrete enough to write
its items from:

- what it delivers: after the foundation, what the owner gets from it, and what is in and out;
- its big steps, its risks, and the decisions it will bring to the owner ([owner.md](owner.md));
- the modules it will build or change, which the gate review reads whole;
- everything it builds on (documents, interfaces, technologies), each written down already or settled at
  the milestone's start, before the work that depends on it;
- its exit list, which always includes that every item of the milestone is merged or dropped with a
  reason, and after the foundation that the owner has used the result in real work and it is released as
  `docs/plan.md` says.

### Starting and finishing

- An item starts only when everything it depends on is merged and its milestone has started; an item
  whose "Depends on" says "any time" may start whenever. A milestone starts when the one before is
  finished and its written-out plan is merged.
- A milestone is finished only when every point of its exit list is true. After the foundation it ends
  in this order, while the coordinator writes out the next one:
  1. The coordinator runs the result end to end and gives it to the owner to try, with the steps, as the
     Releases section of `docs/plan.md` says. Work in progress may be tried the same way.
  2. What must be fixed for the result to do its job is fixed in this milestone and tried again; the
     rest goes to the next milestone or the list for later.
  3. Once the owner says the result is fine, the release goes out. Where the release itself is the try,
     it went out at step 1.
  4. The owner uses the release in real work; what that finds goes out as a fix release or to the next
     milestone.

  Releases may go out within the milestone too, each once the owner has said the build they tried is
  fine. Where the project doesn't ship (`releases` is `none`), steps 3 and 4 are using the result.
- **A gate** ends every milestone: the owner accepts what it delivered and agrees the plan of the next
  one, which lets the coordinator start its work without asking again. The coordinator brings no gate
  while any point of the exit list is open ([coordinator.md](coordinator.md#before-a-gate)).

### A project already under way

A project adopting the process brings its plan into it: what is done stays as it is; a current part that
already ends with something the owner uses becomes a milestone, one that doesn't is cut to what the next
milestone needs and closes the foundation; later parts become milestones, a line each. Backlog items left
outside go to the list for later; an open pull request left outside is the owner's to keep or close.

### The list for later

The section "Later" at the end of `docs/backlog.md` holds what is left out of the milestones so far, a
line each. Moving work of the agreed milestone there is a change of scope, which goes to the owner
([owner.md](owner.md)). A backlog item moved there is dropped with the reason "moved to the list for
later"; a milestone takes work back from there as new items.

## How a piece of work goes

1. **The item** exists in the backlog ([changes.md](changes.md#the-backlog)) and may start. If a session
   would need more than the item to do it, the coordinator fixes the item first, and splits one that is
   clearly too large. One found too large once its pull request is open is split on its branch: the first
   part keeps the ID and the pull request, with a narrower "Done when"; the other parts get new IDs.
2. **The brief** is "Do B-###" and nothing else.
3. **Questions first** ([rules.md](rules.md#your-work)): the coordinator answers in the draft pull
   request, and asks the owner what is the owner's to decide.
4. **The work,** on the item's branch. The session marks the pull request ready when it is done, or, with
   the reviews in draft, says so on it.
5. **Reviews and checks.**
   - **Which reviews.** Every pull request gets the review ([reviews.md](reviews.md)), except a
     coordinator record that changes only `docs/now.md` or the backlog, a process update that only brings
     the template's release, and the next milestone's plan, which gets the gate review instead. The
     review for harm, the architecture review and the UI review come on top for the pull requests they
     are for, each by another reviewer, in the same rounds. `docs/plan.md` may ask for more. A change to
     risky code made after its review for harm goes back to that review, and the coordinator never makes
     one itself.
   - **Fixes.** One work session ("Fix pull request #N") fixes the findings of all the reviews.
   - **Two rounds at most:** a full review, then, only if it had "fix" findings, a review of the fix.
     Small leftovers after that (wording, a link) the coordinator fixes itself; anything in the product
     goes back to a work session. If blocking problems remain, the coordinator stops, rethinks the item
     and tells the owner. `docs/plan.md` may allow more rounds of the review for harm, up to a number it
     names; the report names each such round.
   - **Closing a finding.** A finding of the review for harm is closed only by its reviewer. A finding of
     another review that contradicts the item or the plan, or rests on something untrue, the coordinator
     may close, with the reason in a comment on the pull request; the next report names it. Where reviews
     ask for opposite things, the review for harm wins.
   - **The coordinator's own check:** that the reviews covered every point of "Done when", and that the
     review label is right ([owner.md](owner.md#the-review-label)).
6. **The owner,** where the pull request needs them ([owner.md](owner.md)), gets it in the report
   ([coordinator.md](coordinator.md#the-report)). The owner's remarks the coordinator posts on the pull
   request as "fix" findings, quoting the owner, after first recording any that change a document above
   it, and starts "Fix pull request #N"; that fix gets a review of the fix by each review the change
   needs, and a second round if that one has "fix" findings.
7. **The merge** ("The merge" below).
8. **After the merge** the coordinator brings `docs/now.md` up to date in a coordinator record, several
   merges in one, before its next report, and records the merge in the tracker, if there is one.

**A wrong merge** is reverted in a pull request that names the original item, takes its kind and label,
and unticks the item, which reopens it. Its reviewer checks only that it reverts that one commit and
that its checks pass.

### Reviews in draft

Where the project's `CLAUDE.md` asks for them, so that slow CI doesn't run on every push while the
reviews go on:

- the slow jobs of the project's own workflows skip draft pull requests
  (`if: github.event.pull_request.draft == false`), and those workflows run on `ready_for_review` too,
  which `check.py` checks;
- the work session leaves its finished pull request in draft and says on it that the work is done at its
  last commit;
- the reviews and their fixes go on the draft, and the coordinator marks it ready once no "fix" finding
  is left; a review that needs CI's result (a UI review of screenshots taken in CI) comes after that, in
  the same round. `CLAUDE.md` may hold the draft longer, until the owner has tried a local build, say;
- a red check once the pull request is ready is a "fix" finding; its fix gets one review of the fix,
  outside the two rounds, since that CI ran only now.

Slow CI then usually runs twice: once when the pull request is ready, and again when `main` has moved
before the merge.

### The merge

A pull request merges with green checks, no "fix" finding left, and the owner's OK where it is needed
([owner.md](owner.md#the-owners-ok)). The coordinator merges with

    python3 tools/process/merge.py <N> <commit>

naming the last commit reviewed and approved. It makes one squash commit on `main`, its subject the pull
request's title and number, its body empty. It refuses any other commit, and merges only when the checks
ran on `main` as it is now: GitHub tests a pull request on its merge into `main`, which it makes again
only some time after `main` moves, so a run may test an old `main`. The process checks note the commit
of `main` each run tests, and only runs from the first that tested the current `main` count. When there
are none, `merge.py` waits until GitHub has merged the pull request on the current `main`, then closes
and reopens it, which runs the checks
again and keeps the owner's Approve, at most once for each commit of `main`; the coordinator runs it
again once they finish. Every workflow that runs on pushes runs on `reopened` for this
([pull-requests.md](pull-requests.md#the-checks-ci-runs)). If `merge.py` fails on an error of its own,
the coordinator merges by no other means and reports it.

- **Order.** Work pull requests with green checks merge before the coordinator's own records, so that
  `main` doesn't move under them needlessly.
- **Conflicts.** `main` is merged into the branch only when it conflicts: a work session does it as a
  "fix" finding ("merge `main` in, conflict in X"), and a reviewer looks only at how it resolved them.
- **A red `main`** is fixed first: a document by the coordinator, code by a work session on an item the
  coordinator writes for it. That pull request merges ahead of the rest; the others wait.
- If the owner says no, the pull request stays open, and the owner's remarks go as step 6 says.
