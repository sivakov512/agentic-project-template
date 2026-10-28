# Setting up a project

For a repository just made from the template: `docs/process.json` on `main` says `"set_up": false`,
and the project's files are still the template's placeholders ([README.md](README.md#what-lives-where)).
The session that finds it so sets the project up in one pull request.

**If a branch `setup` or a pull request from it exists,** setting up has started: continue there. Its
description lists the steps, ticked as they are done, and the owner's answers are in its comments.

## What the owner gives

A brief: what the project is, for whom, and what "done" looks like. A few lines in the first message,
or a link to a document. Ask what the steps below need and the brief doesn't answer, in the chat, in
one batch of questions, each with your recommendation; write nothing into the plan until the owner has
answered. Once the setup pull request is open (step 1), put the brief, the questions and the answers in
a comment on it, so a session that continues the setup has them.

Always ask, whatever the brief says:

- **whose account the agents work under, and who merges**
  ([workflow.md](workflow.md#the-owners-ok-and-the-merge)). Ask this first: step 1 already pushes, so
  `git` and `gh` must be signed in as that account before it;
- **which tracker mirrors the project for the owner,** or that there is none; whether the project is in
  it yet; and how agents reach it (a connector, a skill, a token), which the owner grants. If the
  project isn't in it yet, `tracker` names the tracker and says "project to be created";
- **how the project ships** (what is released, versions, how it is built and published, who starts
  it), or that it isn't released ([config.md](config.md#releases));
- the owner's language, and the commit rules, if any ([config.md](config.md#commits)).

## Steps

1. **Branch** `setup` from `main`, start it with `git commit --allow-empty -m "chore: start the setup"`, and
   open a draft pull request titled `Plan: set up the project`, "Backlog item: Setup", with the steps
   below as a checklist in its description. Tick each step there when it is done.
2. **`CLAUDE.md`:** replace the placeholder text with what the project is, in two or three lines, and
   the project's own rules for agents (dangerous operations, hardware, accounts, secrets, anything every
   session must know). Keep the line `@docs/process/rules.md`.
3. **`docs/plan.md`:** fill in every section the placeholder lists. The first stage is usually
   requirements or research; keep the document chain as short as the project allows, and name in it
   where the interfaces between parts are written
   ([workflow.md](workflow.md#how-the-repository-works)). Stages after the first may stay brief: each
   is written out at the end of the one before it.
4. **`docs/process.json`:** the owner's language, the tracker, how the project ships, the agents'
   account and who merges, the commit rules, the kinds of ID and coverage rules
   ([config.md](config.md)). `checks` stays empty until
   the project has code; the item that adds the first check also adds
   `.github/workflows/project-checks.yml` that runs it in CI. Leave `set_up` false until step 9.
5. **`docs/backlog.md`:** the first stage's items ([changes.md](changes.md#the-backlog)).
6. **`docs/now.md`:** where the work stands: stage 1, nothing in work, the first items next.
7. **`README.md`:** what the project is, for a visitor; one paragraph is enough. **`LICENSE`** is the
   template's: replace it with the project's license, or remove it if the owner wants none. The
   process files keep their own notice in `docs/process/README.md`.
8. **GitHub:** `python3 tools/process/doctor.py --fix-labels` creates the labels. The repository's
   settings are the owner's: list them in the pull request as paths of clicks.
   - Settings → General: allow only "Rebase merging".
   - Settings → Branches (or Rules): protect `main`, with changes only through pull requests and the
     checks `process-docs`, `process-pr`, `process-lock` and `process-commits` required (the project's
     own jobs too, once they exist). With the agents' own account, also one approval, dismissed by new
     commits. With the owner's account, no required approvals (untick "Require approvals": nobody can
     approve their own pull request, so nothing would merge) and no bypassing ("Do not allow bypassing
     the above settings", or no bypass list in a ruleset), because the owner's account is an admin and
     the protection wouldn't bind it otherwise.
   - Settings → Secrets and variables → Actions → Variables: `CI_RUNNER`, if the checks should run on a
     self-hosted runner.
   - The secrets the project itself needs, if any are known yet.
9. **Finish:** remove the `<!-- template placeholder -->` lines, set `"set_up": true`, run
   `python3 tools/process/check.py` and `python3 tools/process/doctor.py`, and go on only when both pass,
   apart from what waits on the owner.
10. **Review and report:** the pull request leaves draft, labelled `plan` and `owner-review`; a reviewer
    checks it against the steps above and the owner's answers, as it would an item's "Done when"; its
    "Owner review" asks the owner to read the plan and `CLAUDE.md` and to do the list from step 8.
11. **Merge** as the project chose ([workflow.md](workflow.md#the-owners-ok-and-the-merge)). The next
    session is the coordinator; if the project is still to be created in the tracker, its first job is
    to create it and write its ID into `tracker` in a coordinator record.

## Adopting the process in an existing project

For a project that already runs a process of its own and moves onto the template. Its coordinator does
it when the owner asks, under the project's current rules, reading the template at its latest release.
It asks the questions of "What the owner gives" that the project's files don't answer yet, and works on
a branch `setup`, continued as above. One pull request, kind `plan`, `owner-review`, "Backlog item:
Setup"; the copied template files count as generated, and if the rest would pass the size limit
([rules.md](rules.md#your-work)), the renumbering of the backlog goes first in a pull request of its
own. Work pull requests open at the move stay open: once it is merged, their descriptions get the
template's sections they lack.

1. With the template checked out at its latest release tag, run `python3 <template>/tools/process/sync.py
   <template> .`: it brings the template's files and the lock. Copy the project placeholders from the
   same checkout where the project has no such file yet ([README.md](README.md#what-lives-where)).
2. Split the project's rules: what the process files now say is removed from the project's `CLAUDE.md`
   and plan; what is the project's own stays, under the sections of the `docs/plan.md` placeholder.
   `CLAUDE.md` keeps the project's rules and imports `@docs/process/rules.md`.
3. Move the project's documents where the process expects them, and its backlog into the `B-###` form,
   renumbered if it used another prefix; `docs/now.md` keeps a table from old numbers to new, the old
   ones written as code if their prefix is still one of the project's kinds, so the ID check leaves
   them alone. If the default branch isn't `main`, the owner renames it (Settings → General → Default
   branch).
4. Write `docs/process.json` as in step 4 of setting up, with the project's checks, `ids_ignore` for
   frozen documents and `"set_up": true`. Remove the `<!-- template placeholder -->` lines.
5. Remove the project's old copies of what the template now does: its docs, pull request and commit
   checks and their workflow. Its own checks (tests, builds) move to `.github/workflows/project-*.yml`,
   with job names that don't start with `process-`.
6. Run `python3 tools/process/check.py` and `python3 tools/process/doctor.py` until both pass, apart
   from what waits on the owner, and ask the owner for the settings of step 8 of setting up.
