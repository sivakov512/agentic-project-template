# The owner's part

The owner agrees where the work goes and checks what it gives; the agents do the rest. Whether the owner
is needed is decided by the rules below, not asked of the owner, except when the coordinator isn't sure
whether something stays inside the plan.

## When the owner looks

The owner looks at:

1. **The plan of each milestone after the foundation,** at the gate before it.
2. **The decisions that plan names as the owner's,** each when it is ready. A plan names among them what
   a person will use or work with (the interface, an API or a driver others program against, a file or
   data format a person reads or writes, a command line, settings), what shapes the whole product (the
   architecture, the stack, the model of the data), and what is hard to reverse.
3. **The result of each milestone after the foundation,** by trying it and then using the release
   ([workflow.md](workflow.md#starting-and-finishing)).
4. **What goes beyond the agreed plan:** a change of scope (an item of the agreed milestone dropped or
   moved out of it; one replaced by an item with the same aim is not), sizeable work the plan didn't
   foresee, a problem, a risk or a blocker, an action on the owner's real data (moving, deleting or
   migrating it), and what only the owner can do (accounts, money, hardware, settings).
5. **The rules of the work:** what the owner keeps ("The owner's OK" below).
6. **Reviewed risky code, changes to the architecture or to a contract between parts, and decisions of
   the kinds in point 2 that the plan didn't name,** once their reviews have no "fix" finding left,
   unless `docs/plan.md` says they go without the owner.

`docs/plan.md`, in its section "Owner review", may add to this list or take point 6 off it, in whole or
in part. When the owner says to stop asking about something, or to ask again, the coordinator records it
there the same day; the pull request needs only the owner's Approve, and the rule holds from its merge.
Points 1 to 5 stay with the owner whatever the plan says.

When the coordinator isn't sure whether something stays inside the plan, it asks the owner in one line in
the report, with its recommendation, and holds that pull request until the answer.

## The review label

Every pull request carries one of two labels, which follows its strictest part:

- `owner-review`: it does one of the things in the list above. It says in plain words what it decides or
  changes, and for the checks and CI what it loosens or tightens.
- `ok-without-reading`: everything else: the requirements and the documents of the chain inside the
  agreed scope, studies, code and tests, the backlog, `docs/now.md`, records of facts, and records of the
  owner's own decisions outside what the owner keeps.

A bot's pull request the coordinator labels after its review: a dependency bump inside the plan or a
release goes `ok-without-reading`, a release merging once the owner has said the build they tried is
fine; where the release itself is the try, it merges before the try, and goes `owner-review` when it acts
on the owner's real data.

## The owner's OK

The agents work under a GitHub user account of their own, a collaborator with Write access, not Admin,
in a repository of the owner's personal account. The owner's OK is the owner's Approve on GitHub of the
pull request's last commit; the check `process-owner`, required for `main`, sees to it, and a commit
pushed after the Approve needs a new one. Before merging, the coordinator checks the Approve itself, not
from a retelling.

**A pull request needs the owner's OK** when it is labelled `owner-review`, has no label yet, or changes
what the owner keeps:

- the files CI holds for the owner: `CLAUDE.md` and `CLAUDE.local.md` in any folder, any `.claude/`
  folder, `.mcp.json`, `docs/plan.md`, `docs/process.json` and the paths its `kept` names
  ([config.md](config.md#kept)), anything under `.github/`, and the template's files and lock. The
  exception is a process update whose files are exactly those of the template's release, `.github/`
  aside ([updates.md](updates.md#getting-a-newer-process)). Rules Claude Code loads by itself (a
  `CLAUDE.md` or `CLAUDE.local.md`, `.claude/rules/`) never import (an `@` before the path) a file the
  owner doesn't keep;
- any change that loosens the project's checks, in whatever file (a test removed or skipped, a lint rule
  or a threshold eased), which the label and the reviewers catch.

The rest the coordinator merges on its own once the checks are green and the reviews have no "fix"
finding left; the next report lists it, and the owner can have any of it reverted. The owner may also
merge on GitHub themselves.

The owner discusses a pull request in its comments on GitHub; the coordinator answers there.
