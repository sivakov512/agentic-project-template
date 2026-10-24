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
  files, its lock must name a newer version than `main`'s, and it must be labelled `owner-review`. So the
  process changes only by moving to a newer version, and the owner sees it.

## Getting a newer process

A project takes a new release of the template when it is worked on: `tools/process/doctor.py`, which
the coordinator runs at the start of every session, says when a newer version is out. The coordinator
then runs `python3 tools/process/update.py` with a clean working tree. It makes a branch
`process-update-X.Y.Z` from `main` as it is on GitHub, copies the template's files at the release,
writes the new lock, and opens a pull request `Plan: update the process to X.Y.Z` with "Backlog item:
Process update", labelled `plan` and `owner-review`, and the changelog entries since the current
version; the checkout stays on that branch. While any process update pull request is open, it does
nothing. A project nobody works on needs no update. A release may change
`.github/workflows/process-*.yml`, so the agents' account's git credentials must be allowed to change
workflow files (a classic token's `workflow` scope, or Workflows: write).

In the same pull request the coordinator does what the entries' "Projects:" lines ask of the project
(a new key in `docs/process.json`, say), has open work pull requests fixed if the lines say they break
them ("Fix pull request #N"), and brings it to the owner. The owner reviewed each change in the
template already, so the report says only what the project had to do, or that it had nothing to do.

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
   stands in for major), the date, what changed, and a last
   line `Projects: …` saying what projects must do, or `Projects: nothing to do.` A change that can fail
   a project's open pull requests (a new required section, a stricter check) says what to fix in them.
3. It runs `python3 tools/process/lock.py`, which writes `.process-lock.json` for the new version, and
   `python3 tools/process/check.py`.
4. After the owner's OK and the merge, the template's coordinator tags the last commit the merge
   put on `main` `vX.Y.Z` and makes a GitHub release of it with the changelog entry as its notes
   (`gh release create vX.Y.Z --notes "…"`). Projects pick it up when their coordinators next run
   `doctor.py`.

A fork that becomes a template of its own deletes `.process-lock.json` once and runs `lock.py`, which
then names the fork.

The template's files describe the process only: they never name a project's stages, documents or tools.
A rule that fits only one project belongs in that project's `CLAUDE.md` or `docs/plan.md`.
