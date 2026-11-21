# Setting up a project

For a repository just made from the template: `docs/process.json` on `main` says `"set_up": false`, and
the project's files are still the template's placeholders. The session that finds it so sets the project
up in one pull request. If a branch `setup` or a pull request from it exists, continue there.

## What the owner gives

A brief: what the project is, for whom, and what "done" looks like. Ask what the steps below need and the
brief doesn't answer, in one batch of questions, each with your recommendation. Always ask:

- **the agents' own GitHub account** ([owner.md](owner.md#the-owners-ok)), invited to the repository with
  Write access, not Admin, with a token that may change workflow files. The agents run where only that
  account is signed in: no owner token in `gh`, the credential helper or the environment they can reach;
- **the tracker** that mirrors the project for the owner, or none, and how agents reach it;
- **how the project ships** ([config.md](config.md#releases)), or that it isn't released;
- the owner's language, and the commit rules, if any ([config.md](config.md#commits)).

Push nothing before `gh api user` shows the agents' account. Once the pull request is open, put the
brief, the questions and the answers in a comment on it.

## Steps

1. **Branch** `setup` from `main`, start it with `git commit --allow-empty -m "chore: start the setup"`,
   and open a draft pull request `Plan: set up the project` (`docs(plan): set up the project` with
   Conventional Commits), "Backlog item: Setup", with these steps as a checklist, ticked as they are
   done.
2. **`CLAUDE.md`:** what the project is, in two or three lines, and the project's own rules for agents
   (dangerous operations, hardware, accounts, secrets, house style): a rule every session must keep goes
   here, never only in `docs/plan.md`. Keep the line `@docs/process/rules.md`.
3. **`docs/plan.md`:** every section the placeholder lists. The milestones: the foundation in full, then
   those after it, a line each ([workflow.md](workflow.md#milestones-and-gates)). The document chain as
   short as the project allows, naming where interfaces are written, the design document that lists the
   code's folders ([rules.md](rules.md#code)) and, with a user interface, the design-system document.
4. **`docs/process.json`:** the language, the tracker, how the project ships, the commit rules, the kinds
   of ID and coverage rules ([config.md](config.md)). `checks` stays empty until the project has code;
   the item that adds the first check adds `.github/workflows/project-checks.yml` too.
5. **`docs/backlog.md`:** the first milestone's items ([changes.md](changes.md#the-backlog)).
6. **`docs/now.md`:** the foundation, nothing in work, the first items next.
7. **`README.md`:** what the project is, for a visitor. **`LICENSE`:** the project's license, or none.
8. **GitHub:** `python3 tools/process/doctor.py --fix-labels` creates the two labels. The settings are
   the owner's; list them in the pull request as paths of clicks:
   - Settings → General → Pull Requests: only "Allow squash merging", its default message "Pull request
     title" (in a ruleset for `main` too: Allowed merge methods: Squash only);
   - protect `main` (Settings → Branches, or Rules): changes only through pull requests; required checks
     `process-docs`, `process-pr`, `process-lock`, `process-commits`, `process-owner` and later the
     project's own; no required approvals (`process-owner` asks for the owner's where needed); "Require
     review from Code Owners" and "Dismiss stale pull request approvals when new commits are pushed"; no
     bypassing. The session makes `.github/CODEOWNERS` say `/.github/ @<the owner's login>`;
   - `CI_RUNNER` (Settings → Secrets and variables → Actions → Variables), if the checks run on a
     self-hosted runner: only for a private repository, since every pull request's code runs there;
   - secrets that publish, deploy or mint tokens go into a GitHub Environment limited to `main`, named by
     the job that uses them, which therefore runs on the push to `main`.
9. **Finish:** remove the `<!-- template placeholder -->` lines, set `"set_up": true`, and run
   `check.py` and `doctor.py` until both pass, apart from what waits on the owner.
10. **Review and merge:** the pull request leaves draft labelled `owner-review` and gets the review
    ([reviews.md](reviews.md)); its "Owner review" asks the owner to read the plan and `CLAUDE.md` and to
    do the settings. The session merges it with `merge.py` after the owner's Approve
    ([workflow.md](workflow.md#the-merge)); the next session is the coordinator.

## Adopting the process in an existing project

The project's coordinator does it when the owner asks, from the template's latest release, on a branch
`setup`, in one pull request (kind `plan`, `owner-review`, "Backlog item: Setup"), asking the questions
above that the project doesn't answer yet. Open work pull requests stay open and get the template's
sections once it merges.

1. Run `python3 <template>/tools/process/sync.py <template> .` from a checkout of the release tag: it
   brings the template's files and the lock. Copy the placeholders the project lacks.
2. Remove from the project's `CLAUDE.md` and plan what the process files now say; keep the project's own
   rules there. Bring the plan into milestones ([workflow.md](workflow.md#a-project-already-under-way)).
3. Move the documents where the process expects them, and the backlog into the `B-###` form;
   `docs/now.md` keeps a table from old numbers to new. If the default branch isn't `main`, the owner
   renames it. If the renumbering makes the pull request too large, it goes first in one of its own.
4. Write `docs/process.json` as in step 4, with `ids_ignore` for frozen documents and `"set_up": true`.
5. Remove the project's old copies of what the template does; its own checks move to
   `.github/workflows/project-*.yml`, with job names that don't start with `process-`.
6. Run `check.py` and `doctor.py` until both pass, and ask the owner for the settings of step 8.
