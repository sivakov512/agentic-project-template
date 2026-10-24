# Changes, decisions and traceability

## Changes

- An owner request or decision is recorded the same day
  ([workflow.md](workflow.md#how-the-repository-works)), by the coordinator, in a pull request marked
  "Coordinator record". Nobody acts on a requirement that
  exists only in a chat.
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
- items are never deleted: an item that is no longer needed is ticked and marked "Superseded by B-###"
  or "Dropped", with the reason.

## Decision records

A decision that is hard to reverse gets a record: one per file in `docs/decisions/`,
`NNNN-kebab-case.md`, with its status and date, then Context, Decision, Consequences, and a line in
`docs/decisions/README.md`. Records are never rewritten: if we change our mind, a new record supersedes
the old one and the old one's status becomes "superseded by NNNN".

## Traceability

Every ID is defined in exactly one place, and every reference must lead to a definition. CI checks both,
and rejects IDs in the wrong form.

- **Built in:** backlog items `B-###`, defined by a line in `docs/backlog.md`. Decision records are
  checked by their files: the name `NNNN-kebab-case.md`, a number used once, a line in
  `docs/decisions/README.md`; references to them are links, which the link check covers.
- **The project's own kinds** (requirements, scenarios, cases…) and where each is defined are in
  `docs/process.json`, with the coverage rules between them: for example, every requirement names its
  source, every scenario has steps. [config.md](config.md) says how to write them; `docs/plan.md` says
  in words what they mean.
- Text that looks like an ID but isn't one is written as code (`` `S3` ``), which the check skips.
