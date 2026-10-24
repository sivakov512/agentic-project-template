# Changelog

The newest version first. Each entry says what changed and what projects must do, if anything
([updates.md](updates.md#changing-the-process)).

## 0.2.1 — 2026-10-25

- The template is under the MIT License. The process files carry the notice in
  `docs/process/README.md`; setting up replaces the template's `LICENSE` with the project's own.

Projects: nothing to do.

## 0.2.0 — 2026-10-25

- Every project decides how it ships and writes it down: `releases` in `docs/process.json` (required
  once set up) and a Releases section in `docs/plan.md`; setting up asks for it. The process
  recommends release-please run with a GitHub App's token for projects that ship, but doesn't impose
  it.
- `commits.conventional`: the commit check can require Conventional Commits subjects.
- `doctor.py` reads the required approvals and their dismissal from rulesets.
- Process updates come from the coordinator: when `doctor.py` reports a newer release, it runs
  `tools/process/update.py`, which opens the update pull request. The weekly workflow and its
  `PROCESS_UPDATE_TOKEN` secret are gone: a project nobody works on needs no update.

Projects: 0.1.x's `update.py` runs only in the old workflow, so bring this update by hand once: on a
branch `process-update-0.2.0` from an up-to-date `main`, run `python3 <template>/tools/process/sync.py
<template> .` with the template checked out at `v0.2.0`, commit, and open the pull request as
`updates.md` says, with the title and description `tools/process/update.py` writes (`BODY` there:
"Backlog item: Process update", the changelog entries, "Behaviour change: None"). In the update pull
request, set `releases` in `docs/process.json` (how the project ships, `not yet: <where it is decided>`,
or `none`) and add the Releases section to `docs/plan.md`; until `releases` is set, `process-docs` fails
on it. If the project's commits follow Conventional Commits, set `commits.conventional`, drop the
project's own check of them, and reword the commits of open pull requests that don't match. If
`doctor.py` now flags the approvals for `main`, ask the owner to fix the ruleset (`setup.md`, step 8).
The `PROCESS_UPDATE_TOKEN` secret, if the project has one, can be deleted.

## 0.1.1 — 2026-10-24

- Every comment and review on pull requests is in the owner's language, agents' to each other
  included: the owner reads them. The repository itself stays in English.
- In the template itself, the coordinator merges after the owner's Approve.

Projects: nothing to do.

## 0.1.0 — 2026-10-24

The process of a running agent-driven project, split into the template's part and the project's.

- Rules for agents, roles, stages and gates, how a piece of work goes, pull requests, reports to the
  owner, changes and decision records, the coordinator, defences, the owner's rules.
- Checks: documents (links, backlog, IDs and coverage set in `docs/process.json`, decision records),
  pull request descriptions, commit messages (stricter rules optional), and the lock of the template's
  files, which changes only by moving to a newer version, with the owner's review.
- `doctor.py`, setting up a project or adopting the process in an existing one, the weekly process
  update.
- The "Behaviour change" section, skipping pull requests opened by GitHub Apps, the limit on pull
  request size, found bugs as items of their own.
- The tracker, if any, is chosen at setup and named in `docs/process.json`.
- Each project chooses whether the agents work under an account of their own or the owner's, and
  whether the coordinator or the owner merges.

Projects: nothing to do.
