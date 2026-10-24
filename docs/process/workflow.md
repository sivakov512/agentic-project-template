# How work goes

## How the repository works

- **The repository is the only source of truth.** What is not on `main`, or in an open pull request
  under review, is not decided. Chat history, the tracker, other folders and older copies of the project
  are never a reference ([rules.md](rules.md#where-you-get-information)).
- **Upstream first.** The project's documents depend on each other in the order of the document chain
  in `docs/plan.md`, ending with the backlog and the code ([changes.md](changes.md)).
- **No work without a backlog item.** Pull requests that are not product work say what they are instead
  ([pull-requests.md](pull-requests.md#the-description)).
- **The owner's words become records the same day:** a rule in the plan, a decision record, a change to
  a document, or a backlog item, in a pull request. Until it is merged, the pull request is the record.

## Stages and gates

`docs/plan.md` lists the project's stages: what each delivers, and its exit list. The process holds
them to these rules:

- A stage is finished only when every point of its exit list is true. Every exit list includes: every
  backlog item of the stage is merged, or dropped with a reason.
- An item starts only when everything it depends on is merged and its stage has started. A stage starts
  when the previous one is finished. Items whose "Depends on" says "any time" are the only exception.
- A gate is a stage's end that needs the owner. The coordinator does not bring a gate to the owner while
  any point is open or unchecked, and prepares it as [coordinator.md](coordinator.md#before-a-gate)
  says.

## How a piece of work goes

1. **The item** exists in the backlog ([changes.md](changes.md#the-backlog)) and may start. If a session
   would need more than the item to do it, the coordinator fixes the item first; an item that is clearly
   large is split before a session starts on it.
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
   The coordinator then checks the result personally: the diff against "Done when", the running result.
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
itself, not from a retelling: the Approve on the pull request, or the owner's own words in the chat. The setting-up session counts as the
coordinator for the setup pull request. In the template itself, its owner merges. When the coordinator
quotes the owner's OK in a comment, the quote keeps the owner's words as said.
