# The process

How work goes in a repository where agents do the work and the owner decides. This folder comes from
the template and is the same in every project made from it; in a project, these files are locked
([updates.md](updates.md)).

The process files (this folder, `tools/process/`, `.github/pull_request_template.md` and
`.github/workflows/process-*.yml`) are from
[agentic-project-template](https://github.com/sivakov512/agentic-project-template), copyright (c) 2026
Nikita Sivakov, under the MIT License.

## What lives where

| What | Where | Whose |
|---|---|---|
| How the process works | `docs/process/`, `tools/process/`, `.github/pull_request_template.md`, `.github/workflows/process-*.yml` | the template |
| Which version of the process this is | `.process-lock.json` | written by `lock.py` in the template and copied by the update |
| The template's own releases; in a project its copy does nothing ([updates.md](updates.md#changing-the-process)) | `.github/workflows/template-release.yml` | the template, not in the lock |
| What the project is, and the rules every session of it keeps | `CLAUDE.md`, which imports [rules.md](rules.md) | the project |
| Goal, document chain, milestones, where facts go, and the rest the coordinator needs about the project | `docs/plan.md` | the project |
| Where the work stands | `docs/now.md` | the project |
| The work | `docs/backlog.md` | the project |
| Decisions | `docs/decisions/` and its `README.md` | the project |
| Settings the process reads | `docs/process.json` ([config.md](config.md)) | the project |
| A visitor's introduction | `README.md` | the project |
| The project's license | `LICENSE` | the project |
| What git ignores | `.gitignore` | the project |
| The project's own CI | `.github/workflows/project-*.yml` | the project |
| Who reviews what GitHub keeps for the owner | `.github/CODEOWNERS` ([setup.md](setup.md), step 8) | the project |

The template ships a placeholder for each of the project's files. The process expects the default
branch to be `main`.

## Who reads what

Every session has [rules.md](rules.md), which `CLAUDE.md` imports and which tells it its role and what
to read for it. The rest: [coordinator.md](coordinator.md), [setup.md](setup.md), [roles.md](roles.md),
[workflow.md](workflow.md) (milestones, gates, how a piece of work goes, the merge),
[pull-requests.md](pull-requests.md), [reports.md](reports.md), [changes.md](changes.md) (requests,
decisions, the backlog, IDs), [defences.md](defences.md) (what could go wrong and what stops it),
[config.md](config.md) (`docs/process.json`), [updates.md](updates.md), [CHANGELOG.md](CHANGELOG.md).
