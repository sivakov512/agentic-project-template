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

## Who reads what

Every session has [rules.md](rules.md): `CLAUDE.md` imports it, and it tells a session its role.

| Role | Reads |
|---|---|
| Work session | its backlog item and every document it links; [pull-requests.md](pull-requests.md) |
| Reviewer | the pull request's item and the documents it links |
| Coordinator | [coordinator.md](coordinator.md), which names the rest |
| Setting up a project | [setup.md](setup.md) |
| The template's coordinator | [updates.md](updates.md#changing-the-process) |

The rest, for reference: [roles.md](roles.md) (who does what), [workflow.md](workflow.md) (stages,
gates, how a piece of work goes, the merge), [pull-requests.md](pull-requests.md),
[reports.md](reports.md), [changes.md](changes.md) (requests, decisions, the backlog, IDs),
[defences.md](defences.md) (what could go wrong and what stops it), [config.md](config.md)
(`docs/process.json`), [updates.md](updates.md) (getting a newer process),
[CHANGELOG.md](CHANGELOG.md) (what changed between versions).
