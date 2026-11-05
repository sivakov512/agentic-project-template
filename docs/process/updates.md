# Updating and changing the process

The process lives in one place, the template repository named in `.process-lock.json`. Projects get
it by copy and keep it the same as a released version of the template.

## The lock

`.process-lock.json` holds the template's name, the version of the process, and a hash of every file
that belongs to the template ([README.md](README.md#what-lives-where)).

- `tools/process/check.py` fails when a template file differs from its hash, is missing, or isn't in
  the lock, or when the lock's version isn't the newest in [CHANGELOG.md](CHANGELOG.md). So a template
  file can't be edited in a project by mistake.
- `tools/process/check_lock.py` compares a pull request with `main`'s lock: if it changes the template's
  files, its lock must name a newer version than `main`'s. So the process changes only by moving to a
  newer version, which the owner agreed in the template; `process-owner` lets the template's files in
  without the owner only when they are exactly those of that release, and its tag is on the template's
  `main`.

## Getting a newer process

A project takes a new release of the template when it is worked on: `tools/process/doctor.py`, which the
coordinator runs at the start of every session, says when a newer version is out. The coordinator then
runs `python3 tools/process/update.py` with a clean working tree. It makes a branch
`process-update-X.Y.Z` from `main` as it is on GitHub, copies the template's files at the release (a
release whose tag is not on the template's `main` it refuses before running anything of it),
writes the new lock, and opens a pull request `Plan: update the process to X.Y.Z` with "Backlog item:
Process update", labelled `plan` and `ok-without-reading`, or `owner-review` where it goes to the owner
(below), and the changelog entries since the current version; the checkout stays on that branch. While
any process update pull request is open, it does nothing. A project nobody works on needs no update. A
release may change `.github/workflows/process-*.yml`, so the agents' account's git credentials must be
allowed to change workflow files (a classic token's `workflow` scope, or Workflows: write).

In the same pull request the coordinator does what the entries' "Projects:" lines ask of the project
(a new key in `docs/process.json`, say) and has open work pull requests fixed if the lines say they
break them: it posts on each what to change, as "fix" findings, then starts "Fix pull request #N".

If that changes nothing the owner keeps, the coordinator merges the update on its own once its checks
pass, and the report lists it: `process-owner` lets the template's files in without the owner where
each is exactly as in the release. If it does (the plan, the settings), the pull request is labelled
`owner-review` and goes to the owner, whose review covers only what the project had to do: the owner
agreed each change in the template already. With the agents' own account, an update that changes files
under `.github/` goes to the owner too, since GitHub keeps `.github/` for the owner; `update.py` labels
it `owner-review`, and its "Owner review" says that an Approve is all it needs, no reading.

## When a release breaks the project

If a merged release breaks the project (a check that blocks every pull request, say), the coordinator
reverts the commits the update put on `main` (`git revert`) in one pull request, `Plan: roll the process back to
X.Y.Z`, with "Backlog item: Process update", labelled `plan` and `owner-review`, and tells the owner and
the template's coordinator what broke. `process-lock` refuses a lock going back, so the owner removes
it as a required check for this one merge, and `process-owner` too when it is what broke (Settings >
Rules > Rulesets > the ruleset for `main` > Require status checks to pass > remove it > Save changes;
with classic protection, Settings > Branches > Edit), merges, and adds them back the same way at once.
The coordinator then waits for the release that fixes it rather than taking the broken one again,
though `doctor.py` reports it meanwhile.

## Changing the process

When the process gets in the way or misses something, the change is made in the template, never in a
project. A project's coordinator writes the problem and the change it proposes to the owner; with the
owner's yes it goes to the template as an issue, or as a pull request where the agents may open one.
It links where it came from (the project's pull request or report), so the template's history says why.

In the template, the process files are its documents, and its coordinator changes them itself:

1. A pull request of kind `plan`, labelled `owner-review`, with "Backlog item: Process change", that
   changes the template's files; a reviewer checks it as any other.
2. The same pull request adds an entry at the top of [CHANGELOG.md](CHANGELOG.md): the new version
   (`MAJOR.MINOR.PATCH`; patch for wording, minor for new rules or files, major when projects must change
   something, a new required key in `docs/process.json` included; while the version is 0.x, minor
   stands in for major too, so new rules and changes projects must make both raise the minor), the date, what changed, and a last
   line `Projects: …` saying what projects must do, or `Projects: nothing to do.` A change that can fail
   a project's open pull requests (a new required section, a stricter check) says what to fix in them.
3. It runs `python3 tools/process/lock.py`, which writes `.process-lock.json` for the new version, and
   `python3 tools/process/check.py`.
4. After the owner's OK, the coordinator merges, and nobody tags by hand: the workflow
   `.github/workflows/template-release.yml` tags the last commit the merge put on `main` `vX.Y.Z`, the
   version at the top of the changelog, and makes a GitHub release `X.Y.Z` of it with that entry as its
   notes. Projects pick it up when their coordinators next run `doctor.py`, and trust a tag only when its
   commit is on the template's `main`, so a tag made anywhere else brings nothing in. It does block that
   version's release, though: when the tag exists before the merge, off `main` or without a release,
   the workflow fails red, and the owner deletes the tag (with the ruleset below turned off for it) and
   runs the workflow again. So that a release, once out, is never moved or deleted, the owner keeps a
   tag ruleset: Settings > Rules > Rulesets > New ruleset > New tag ruleset; name `releases`,
   Enforcement status Active, Target tags > Add target > Include by pattern `v*`; tick "Restrict
   updates" and "Restrict deletions" and leave "Restrict creations" off, since the workflow makes the
   tags; no bypass list; Create. The workflow runs only
   where the repository is the template its lock names, so in a project made with "Use this template"
   its copy does nothing.

A fork that becomes a template of its own deletes `.process-lock.json` once and runs `lock.py`, which
then names the fork.

The template's files describe the process only: they never name a project's milestones, documents or tools.
They never write `@` right before a path either: `process-owner` reads that as an import, and fails in
every project where the path is a file the owner doesn't keep.
A rule that fits only one project belongs in that project's `CLAUDE.md` or `docs/plan.md`.
