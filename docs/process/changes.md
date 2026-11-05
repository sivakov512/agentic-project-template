# Changes, decisions and traceability

## Changes

- The coordinator records the owner's requests and decisions in a "Coordinator record" pull request
  ([workflow.md](workflow.md#how-the-repository-works)). Nobody acts on a requirement that exists only
  in a chat.
- A change is made in the highest document of the chain it touches first, then carried down to the
  backlog. A new need starts where it comes from in the chain.
- Backlog items a change affects are updated, or closed as superseded with a pointer to the new item.
- Facts found by experiment are recorded by the session that finds them
  ([rules.md](rules.md#your-work)). A guess is never presented as a fact.
- Risks and blockers go into the report and the tracker.

## The backlog

`docs/backlog.md` holds every piece of work:

- a top-level line `- [ ] **B-###** Title.`; the pull request that does the work ticks it (`[x]`), and
  it counts as done once that pull request is merged;
- indented lines under it: "Depends on" (items and documents it needs, or "any time") and "Done when"
  (the bar for the work, specific enough for a reviewer to check point by point), with links to the
  documents it depends on;
- items stand under a heading per milestone (`## <milestone>`), in the order of `docs/plan.md`; an
  item belongs to the milestone it stands under;
- items are never deleted: an item that is no longer needed is ticked and marked "Superseded by B-###"
  or "Dropped", with the reason;
- the section "Later" at the end holds what is left out of the milestones so far
  ([workflow.md](workflow.md#the-list-for-later)).

## Decision records

A decision that is hard to reverse gets a record: one per file in `docs/decisions/`,
`NNNN-kebab-case.md`, with its status and date, then Context, Decision, Consequences, and a line in
`docs/decisions/README.md`. Records are never rewritten: a new record supersedes the old one, whose
status becomes "superseded by NNNN".

## Traceability

Every ID is defined in exactly one place, and every reference leads to a definition; CI checks both,
and the form of each ID.

- **Built in:** backlog items `B-###`, defined by a line in `docs/backlog.md`. Decision records are
  checked by their files: the name `NNNN-kebab-case.md`, a number used once, a line in
  `docs/decisions/README.md`; references to them are links, which the link check covers.
- **The project's own kinds** (requirements, scenarios, cases…), where each is defined and the coverage
  rules between them are in `docs/process.json` ([config.md](config.md)); `docs/plan.md` says in words
  what they mean.
