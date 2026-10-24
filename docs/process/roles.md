# Roles

| Who | Does |
|---|---|
| Owner | The customer: wants the result, asks questions and gives remarks, which may land anywhere. Reviews what matters, gives an OK on the rest, says yes to each pull request (or merges it), can stop any work at any time. Not disturbed by default. |
| Coordinator | Runs the plan like a product manager: keeps the documents, the backlog, `docs/now.md` and the tracker; writes backlog items; starts work sessions and reviewers and checks what they deliver; is the expert: weighs every owner remark on its merit and says where it agrees, where it belongs elsewhere and where it disagrees, with the reason; decides routine questions inside what the owner agreed; when something matters, makes sure the owner looks at it and says why; reports to the owner; merges after the owner's OK, unless the owner merges. Does not write product code. |
| Work session | Does exactly one backlog item and opens one pull request for it. |
| Reviewer | A separate session that checks a pull request against its item and the documents above it. Its job is to find problems, not to approve. |

[rules.md](rules.md) tells a session which of these it is.

Work sessions are separate agent sessions that the coordinator starts, each with a one-line brief as
its first message (in Claude Code, a new session in this repository). A reviewer is an agent the
coordinator runs with a fresh context, apart from the work session, with the brief "Review pull request
#N" (a new session, or a subagent that starts with no context of its own).

## Where things are

| What | Where |
|---|---|
| Plan, rules, specs, decisions, backlog | this repository, `main` |
| Where the work stands now | `docs/now.md` |
| Work in progress | pull requests, one per backlog item, on a branch `b-###-short-name` |
| A reviewer's findings | a comment on the pull request it reviewed |
| The owner's review, discussion and OK of a pull request | its comments and an Approve on GitHub; with the owner's account, the chat ([workflow.md](workflow.md#the-owners-ok-and-the-merge)) |
| Reports to the owner | the coordinator's chat with the owner |
| Progress, and what waits on the owner | the tracker, if any ([coordinator.md](coordinator.md#the-tracker)) |
