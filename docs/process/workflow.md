# How work goes

## How the repository works

- **The repository is the only source of truth.** What is not on `main`, or in an open pull request
  under review, is not decided. Chat history, the tracker, other folders and older copies of the project
  are never a reference ([rules.md](rules.md#where-you-get-information)).
- **Upstream first.** The project's documents depend on each other in the order of the document chain
  in `docs/plan.md`, ending with the backlog and the code ([changes.md](changes.md)).
- **Interfaces before the work on either side.** Where different items build parts that meet (a data
  schema, an API, a protocol, a file format, a pinout, a document's structure), the meeting point is
  written down, with every name, field and limit the sides rely on, before those items start. It is
  written once, where the document chain says: in a form the parts use directly when there is one (a
  schema file, an API description), so the work is built from it or checked against it and can't drift
  from it; otherwise in a document. Documents above it explain it in plain words and link to it.
  Leaving it to the code holds only when one item builds both sides.
- **No work without a backlog item.** Pull requests that are not product work say what they are instead
  ([pull-requests.md](pull-requests.md#the-description)).
- **The owner's words become records the same day:** a rule in the plan, a decision record, a change to
  a document, or a backlog item, in a pull request. Until it is merged, the pull request is the record.

## Stages and gates

The work goes in increments, each ending with something the owner uses: a build, a document, a board,
whatever the project makes. `docs/plan.md` lists the project's stages, each with what it delivers and
its exit list:

- **The foundation,** the first stage, once and short: what the product is for and for whom, the
  owner's main scenarios, the limits; research only where a decision can't be made without it; the
  technologies and the frame of the design only as far as the first increment needs. For a product that
  exists already, it also holds an inventory of what the product does and checks that it still does it
  (tests, for code), where these don't exist yet.
- **Increments,** one stage each, one after another. An increment says what the owner gets from it in
  their real work: something they can do that they couldn't, or, for a step of a rebuild, a part of the
  product they use running on the rebuilt part, checked. Everything else goes to the plan's list for
  later. Inside it: the requirements and research for that scope only, the design and the interfaces
  for it, and the items that build it. The first increment of a new product is its smallest version
  the owner can use; for a product that exists, each increment changes the working product, and a
  rebuild goes as a series of increments, each leaving it working.

The process holds the stages to these rules:

- A stage is finished only when every point of its exit list is true. Every exit list includes: every
  backlog item of the stage is merged, or dropped with a reason. An increment's also includes: the
  owner has used it in real work, and it is released as `docs/plan.md` says.
- Each stage is written out at the end of the one before it, from what is known by then: what the
  stage delivers and its exit list in `docs/plan.md`, concrete enough to write its items from. It names
  everything the stage builds on (documents, interfaces, the technologies it uses), each either
  decided and written down already or settled at the stage's start,
  before the work that depends on it. This change to the plan goes to the owner in the same report as
  the gate.
- An item starts only when everything it depends on is merged and its stage has started. A stage starts
  when the previous one is finished and its own written-out plan is merged. Items whose "Depends on"
  says "any time" are the only exception.
- An increment ends in this order: the coordinator runs the result end to end and gives it to the
  owner ready to try, with the steps; the owner uses it in real work and says what came up; what must
  be fixed for it to do its job is fixed in this increment, the rest goes to the next one or the list
  for later. While the owner tries it, the coordinator writes out the next increment and adds what
  comes up.
- A gate is a stage's end, and every stage ends with one: the owner accepts what the stage delivered
  and agrees the next increment. The coordinator does not bring a gate to the owner while any point is
  open or unchecked, and prepares it as [coordinator.md](coordinator.md#before-a-gate) says.
- The list for later in `docs/plan.md` holds what is left out of the increments so far, so nothing is
  lost. A backlog item moved there is dropped with the reason "moved to the list for later"; an
  increment takes its work back from there as new items.

## How a piece of work goes

1. **The item** exists in the backlog ([changes.md](changes.md#the-backlog)) and may start. If a session
   would need more than the item to do it, the coordinator fixes the item first; an item that is clearly
   large is split before a session starts on it. One found too large once its pull request is open is
   split on that pull request's branch: the coordinator commits the split to `docs/backlog.md` there,
   the first part keeps the ID with a narrower "Done when" and goes on in the same pull request, and the
   other parts get new IDs. The split follows from the work: it changes neither the pull request's kind
   nor its review label ([pull-requests.md](pull-requests.md#kind-and-labels)), and the report names it
   among the coordinator's own decisions.
2. **The brief** is the item's ID: "Do B-###". Nothing else; everything the session needs is in the
   repository.
3. **Questions first:** the session opens a draft pull request with its plan and questions, and the
   coordinator answers there, bringing the owner in when a question is the owner's to decide
   ([rules.md](rules.md#your-work)).
4. **The work,** on the item's branch and pull request. Then the pull request leaves draft.
5. **The checks.** CI passes, and a reviewer ("Review pull request #N") posts its findings
   ([rules.md](rules.md#if-you-are-the-reviewer)). A work session ("Fix pull request #N") fixes them.
   **At most two rounds:** a full review, then, only if it had "fix" findings, a review of the fix
   alone; small leftovers of the second round (wording, a link) the coordinator fixes itself, anything
   in the product goes back to a work session. If blocking problems remain after that, the coordinator
   stops, rethinks the item (its approach or its size) and tells the owner.
   A pull request with code that `docs/plan.md` names as risky also gets a review for harm ("Review
   pull request #N for harm"), run at the same time by another reviewer
   ([rules.md](rules.md#if-you-are-the-reviewer)). One "Fix pull request #N" fixes the findings of both.
   Any change to the risky code after the review for harm, from a fix of either review or later, goes
   back to it before the merge, even when its own first round had no "fix" finding, and the coordinator
   never makes such a change itself. A finding of the review for harm is closed only when its
   reviewer says so: if one is still open after its second round, the coordinator neither fixes it
   itself nor merges, but stops and tells the owner. The pull request merges only when neither review
   has a "fix" finding left.
   The coordinator then checks the result personally: the diff against "Done when", the running result,
   and that the commits read as the steps they are ([rules.md](rules.md#git-and-github)).
6. **The report to the owner** ([reports.md](reports.md)). The owner reviews and discusses the pull
   request in its comments on GitHub, or in the chat when agents work under the owner's account; the
   coordinator answers where the owner wrote.
7. **The merge,** only after the owner's OK, by rebase ("The owner's OK and the merge" below). When the
   merge changes where the work stands, the coordinator adds the commit that brings `docs/now.md` up to
   date before it asks for the OK, so the owner agrees to exactly what is merged. If the owner says no,
   the pull request stays open, and the owner's remarks are handled like any other change
   ([changes.md](changes.md)).
8. **After the merge,** whoever merged, the coordinator records it in the tracker, if the project has
   one. The owner tells the coordinator in the chat what was done on GitHub (an Approve, a merge), and
   the coordinator also re-reads the open pull requests at the start of each session.

## The owner's OK and the merge

Each project chooses, in `docs/process.json`, how this works for it; the choice is the owner's
([config.md](config.md#project)).

**Whose account the agents work under** (`agents_account`):

- `own`: a GitHub user account of the agents' own (a user account, not a GitHub App, whose pull
  requests would skip the description check), a collaborator with Write access, not Admin, so the
  protection binds it. Their work carries their name, and the owner's OK is an Approve on GitHub. GitHub
  itself then holds the gate: `main` takes nothing without the owner's Approve, and a new commit
  dismisses it.
- `owner`: the owner's account. The work carries the owner's name. Nobody can approve their own pull
  request, and a comment on GitHub can't show whether the owner or an agent wrote it, so the owner's OK
  is the owner's word in the chat, which the coordinator quotes in a comment on the pull request before
  merging. The gate is then the rules, not GitHub: `main` still takes changes only through pull requests
  with green checks, but nothing but the rules stops an agent from merging.

**Who merges** (`merged_by`):

- `coordinator`: the coordinator merges once the owner's OK is there; the owner only says yes.
- `owner`: the owner merges. With the agents' own account the owner approves and merges; with the
  owner's account the merge itself is the OK.

Either way agents never merge without the owner's OK, and a commit pushed after the OK needs the OK
again (with the agents' own account GitHub sees to that). Before merging, the coordinator checks the OK
itself, not from a retelling: the Approve on the pull request, or the owner's own words in the chat.
When the coordinator quotes the owner's OK in a comment, the quote keeps the owner's words as said. The
setting-up session counts as the coordinator for the setup pull request. In the template itself, the
coordinator merges after the owner's Approve, as in a project with the agents' own account.
