<!-- template placeholder -->
# agentic-project-template

A repository template for projects where AI agents do the work and a person decides: the agents plan,
build, review and report through pull requests, and nothing reaches `main` without the owner's OK.
The process is written down in the repository, so any fresh agent session can pick up the work from the
files alone, and it is checked in CI.

## Start a project

1. **Use this template** on GitHub to make a new repository.
2. Choose the account the agents work under: one of their own, invited as a collaborator with Write
   access (it accepts the invitation), so you approve their pull requests on GitHub; or yours, so you
   give your OK in the chat. Either way, you or the coordinator merge
   ([docs/process/workflow.md](docs/process/workflow.md#the-owners-ok-and-the-merge)).
3. Open an agent session (Claude Code) in it, signed in to `git` and `gh` as that account, and write
   what the project is, in a few lines.
4. The agent sees the project is not set up, follows [docs/process/setup.md](docs/process/setup.md) and
   brings one pull request with the plan, the first backlog and a short list of settings for you.

## What is in it

- [`docs/process/`](docs/process/README.md): the process. Roles (owner, coordinator, work session,
  reviewer), how one piece of work goes from a backlog item to a merged pull request, what the owner
  reviews and what only needs an OK, decision records, IDs and coverage.
- `tools/process/`: checks of the documents, pull requests and commits; `doctor.py`, which says what
  the setup is missing; `update.py`, which brings a newer process into a project.
- Placeholders for the project's own files: `CLAUDE.md`, `docs/plan.md`, `docs/now.md`,
  `docs/backlog.md`, `docs/decisions/`, `docs/process.json`.

## Updates

Projects keep the template's files as a released version, locked by hash. When a newer release is out,
the project's coordinator brings it as a pull request; changes to the process are made here, never in
a project ([docs/process/updates.md](docs/process/updates.md)).

This file is the project's: setting up replaces it.
