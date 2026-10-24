# The process

How work goes in a repository where agents do the work and the owner decides. This folder comes from
the template and is the same in every project made from it. A change to the process goes to the
template ([updates.md](updates.md)); in a project, these files are locked.

The process files (this folder, `tools/process/`, `.github/pull_request_template.md` and
`.github/workflows/process-*.yml`) are from
[agentic-project-template](https://github.com/sivakov512/agentic-project-template), copyright (c) 2026
Nikita Sivakov, under the MIT License.

## What lives where

| What | Where | Whose |
|---|---|---|
| How the process works | `docs/process/`, `tools/process/`, `.github/pull_request_template.md`, `.github/workflows/process-*.yml` | the template |
| Which version of the process this is | `.process-lock.json` | written by `lock.py` in the template and copied by the update |
| What the project is, and its own rules for agents | `CLAUDE.md`, which imports [rules.md](rules.md) | the project |
| Goal, document chain, stages, where facts go, the owner's rules for this project | `docs/plan.md` | the project |
| Where the work stands | `docs/now.md` | the project |
| The work | `docs/backlog.md` | the project |
| Decisions | `docs/decisions/` and its `README.md` | the project |
| Settings the process reads | `docs/process.json` ([config.md](config.md)) | the project |
| A visitor's introduction | `README.md` | the project |
| The project's license | `LICENSE` | the project |
| What git ignores | `.gitignore` | the project |
| The project's own CI | `.github/workflows/project-*.yml` | the project |

The template ships a placeholder for each of the project's files. The process expects the default
branch to be `main`.

## Read in this order

1. [rules.md](rules.md): rules for every agent. `CLAUDE.md` imports it, so every session has it.
2. [roles.md](roles.md): owner, coordinator, work session, reviewer.
3. [workflow.md](workflow.md): stages and gates, and how one piece of work goes from item to merge.
4. [pull-requests.md](pull-requests.md): kinds, labels, the description, the checks.
5. [reports.md](reports.md): what the owner gets told, and what needs the owner's review.
6. [changes.md](changes.md): how requests and decisions are recorded, the backlog, decision records,
   IDs and coverage.
7. [coordinator.md](coordinator.md): the coordinator's protocol, the tracker, stopping.
8. [defences.md](defences.md): what could go wrong and what stops it.

Setting up a project, or adopting the process in an existing one: [setup.md](setup.md). Getting a newer
process, or changing it: [updates.md](updates.md). What changed between versions:
[CHANGELOG.md](CHANGELOG.md).
