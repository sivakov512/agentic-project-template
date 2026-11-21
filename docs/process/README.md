# The process

How work goes in a repository where agents do the work and the owner decides. This folder comes from the
template and is the same in every project made from it; in a project, these files are locked
([updates.md](updates.md)).

The process files (this folder, `tools/process/`, `.github/pull_request_template.md` and
`.github/workflows/process-*.yml`) are from
[agentic-project-template](https://github.com/sivakov512/agentic-project-template), copyright (c) 2026
Nikita Sivakov, under the MIT License.

## Roles

| Who | Does |
|---|---|
| Owner | The customer: wants the result, asks questions and gives remarks, looks at what matters and approves it ([owner.md](owner.md)), can stop any work at any time. Not disturbed by default. |
| Coordinator | Runs the plan like a product manager: keeps the documents, the backlog and `docs/now.md`; writes backlog items; starts work sessions and reviewers and checks what they deliver; weighs every remark of the owner's on its merit and says where it agrees and where not, with the reason; decides routine questions inside what the owner agreed; reports to the owner and merges. Does not write product code. |
| Work session | Does exactly one backlog item in one pull request. |
| Reviewer | Checks a pull request against its item and the documents above it, to find problems, not to approve. |

Work sessions are separate agent sessions the coordinator starts, each with a one-line brief as its first
message. A reviewer is an agent the coordinator runs with a fresh context, apart from the work session,
with the brief of one review ([reviews.md](reviews.md)).

## Who reads what

Every session has [rules.md](rules.md), which `CLAUDE.md` imports and which tells it its role and what to
read for it:

- a work session: [rules.md](rules.md) and [pull-requests.md](pull-requests.md);
- a reviewer: [reviews.md](reviews.md);
- the coordinator: [coordinator.md](coordinator.md), [workflow.md](workflow.md) (milestones, how a piece
  of work goes, the merge), [owner.md](owner.md) (what goes to the owner), [changes.md](changes.md)
  (records, the backlog, IDs) and [pull-requests.md](pull-requests.md); [config.md](config.md)
  (`docs/process.json`) and [updates.md](updates.md) when it needs them;
- the session setting a project up: [setup.md](setup.md);
- the template's coordinator: [updates.md](updates.md#changing-the-process) and the coordinator's files
  where they apply.

[defences.md](defences.md) lists what could go wrong and what stops it; [CHANGELOG.md](CHANGELOG.md),
what changed in each version.

## What lives where

| What | Where | Whose |
|---|---|---|
| The process | `docs/process/`, `tools/process/`, `.github/pull_request_template.md`, `.github/workflows/process-*.yml` | the template |
| Which version of the process this is | `.process-lock.json` | written by `lock.py` in the template, copied by the update |
| The template's own releases; in a project its copy does nothing | `.github/workflows/template-release.yml` | the template, not in the lock |
| What the project is, and the rules every session of it keeps | `CLAUDE.md`, which imports [rules.md](rules.md) | the project |
| Goal, document chain, milestones, where facts go, what the owner looks at | `docs/plan.md` | the project |
| Where the work stands | `docs/now.md` | the project |
| The work | `docs/backlog.md` | the project |
| Decisions | `docs/decisions/` and its `README.md` | the project |
| Settings the process reads | `docs/process.json` ([config.md](config.md)) | the project |
| A visitor's introduction, the license, what git ignores | `README.md`, `LICENSE`, `.gitignore` | the project |
| The project's own CI | `.github/workflows/project-*.yml` | the project |
| Who reviews what GitHub keeps for the owner | `.github/CODEOWNERS` ([setup.md](setup.md), step 8) | the project |
| Work in progress | a pull request per backlog item, on a branch `b-###-short-name` | |
| A reviewer's findings, the owner's review and Approve | the pull request's comments and reviews | |
| Reports to the owner | the coordinator's chat with the owner | |

The template ships a placeholder for each of the project's files. The default branch is `main`.
