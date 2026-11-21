# Changes, decisions and traceability

## Changes

- The coordinator records the owner's requests and decisions in a "Coordinator record" pull request
  ([workflow.md](workflow.md#how-the-repository-works)). Nobody acts on a requirement that exists only in
  a chat.
- A change is made first in the highest document of the chain it touches, then carried down to the
  backlog. A new need starts where it comes from in the chain.
- Backlog items a change affects are updated, or closed as superseded with a pointer to the new item.
- A guess is never presented as a fact.

## The backlog

`docs/backlog.md` holds every piece of work:

- a top-level line `- [ ] **B-###** Title.`; the pull request that does the work ticks it (`[x]`), and it
  counts as done once that pull request is merged;
- indented lines under it: "Depends on" (items and documents it needs, or "any time") and "Done when"
  (the bar for the work, specific enough for a reviewer to check point by point), with links to the
  documents it depends on;
- items stand under a heading per milestone (`## <milestone>`), in the order of `docs/plan.md`;
- items are never deleted: one no longer needed is ticked and marked "Superseded by B-###" or "Dropped",
  with the reason;
- the section "Later" at the end holds what is left out of the milestones so far
  ([workflow.md](workflow.md#the-list-for-later)).

## Decision records

A decision that is hard to reverse gets a record: one per file in `docs/decisions/`,
`NNNN-kebab-case.md`, with its status and date, then Context, Decision, Consequences, and a line in
`docs/decisions/README.md`. Records are never rewritten: a new record supersedes the old one, whose
status becomes "superseded by NNNN".

## Traceability

Every ID is defined in exactly one place, and every reference leads to a definition; CI checks both, and
the form of each ID.

- **Built in:** backlog items `B-###`, defined by a line in `docs/backlog.md`. Decision records are
  checked by their files: the name, a number used once, a line in `docs/decisions/README.md`.
- **The project's own kinds** (requirements, scenarios, cases…): where each is defined and the coverage
  rules between them are in `docs/process.json` ([config.md](config.md)); `docs/plan.md` says in words
  what they mean.
