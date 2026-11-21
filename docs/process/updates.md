# Updating and changing the process

The process lives in one place, the template repository named in `.process-lock.json`. Projects get it by
copy and keep it the same as a released version of the template.

## The lock

`.process-lock.json` holds the template's name, the version of the process, and a hash of every file that
belongs to the template ([README.md](README.md#what-lives-where)).

- `check.py` fails when a template file differs from its hash, is missing or isn't in the lock, or when
  the lock's version isn't the newest in [CHANGELOG.md](CHANGELOG.md).
- `check_lock.py` fails a pull request that changes the template's files without moving the lock to a
  newer version than `main`'s.
- `process-owner` lets the template's files in without the owner only when they are exactly those of a
  release whose tag is on the template's `main`.

## Getting a newer process

A project takes a new release when it is worked on; `doctor.py` says when one is out.

1. The coordinator runs `python3 tools/process/update.py` with a clean working tree. It makes a branch
   `process-update-X.Y.Z` from `main` on GitHub, copies the template's files at the release (refusing one
   whose tag is not on the template's `main`), writes the lock, opens the pull request ("Backlog item:
   Process update") with the changelog entries since the current version, and leaves the checkout on that
   branch. It may force-push that branch, its own, the one exception to "no force push". While a process
   update pull request is open, it does nothing. The agents' token must be allowed to change workflow
   files.
2. In the same pull request the coordinator does what the entries' "Projects:" lines ask. A step that
   needs a decision of the owner's goes in a pull request of its own, after the update merges. Where the
   lines say open pull requests break, it posts on each what to change, as "fix" findings.
3. If that changes nothing the owner keeps, the coordinator merges the update once its checks pass and
   its review, if it needs one, has no "fix" finding left. Otherwise (the plan, the settings, files under
   `.github/`) it goes to the owner labelled `owner-review`, the owner's review covering only what the
   project had to do; for files under `.github/` alone, an Approve is all it needs.

## When a release breaks the project

1. The coordinator reverts the update's commit in one pull request, `Plan: roll the process back to
   X.Y.Z`, "Backlog item: Process update", labelled `owner-review`, which also records in `docs/now.md`:
   "Process: stays on X.Y.Z; A.B.C broke <what>; take the release after it". It tells the owner and the
   template's coordinator what broke.
2. `process-lock` refuses a lock going back, so the owner removes it from the required checks for this
   one merge, and `process-owner` too when that is what broke (Settings → Rules → Rulesets → the ruleset
   for `main` → Require status checks to pass), merges, and adds them back at once.
3. The coordinator waits for the release that fixes it, and removes the line from `docs/now.md` in the
   update that takes it.

## Changing the process

A change to the process is made in the template, never in a project. A project's coordinator writes the
problem and the change it proposes to the owner; with the owner's yes it goes to the template as an issue
or a pull request.

In the template, its coordinator changes the process files itself:

1. A pull request of kind `plan`, labelled `owner-review`, "Backlog item: Process change", reviewed as any
   other.
2. It adds an entry at the top of [CHANGELOG.md](CHANGELOG.md): the version, the date, what changed, and
   a last line `Projects: …` saying what projects must do, or `Projects: nothing to do.` A change that
   can fail open pull requests says what to fix in them. Versions are `MAJOR.MINOR.PATCH`: patch for
   wording, minor for new rules or files, major when projects must change something; while the version is
   0.x, minor stands in for major.
3. It runs `python3 tools/process/lock.py` and `python3 tools/process/check.py`.
4. After the owner's Approve it merges. The workflow `template-release.yml` then tags the merge `vX.Y.Z`
   and makes a GitHub release with the changelog entry as its notes; nobody tags by hand.

### Release tags

- Projects trust a tag only when its commit is on the template's `main`. A tag made before the merge
  blocks the release: the workflow fails, and the owner deletes the tag and runs the workflow again.
- A tag ruleset keeps releases from being moved or deleted: Settings → Rules → Rulesets → New tag
  ruleset, name `releases`, Active, target pattern `v*`, "Restrict updates" and "Restrict deletions" on,
  "Restrict creations" off, no bypass list.
- The workflow runs only where the repository is the template its lock names. A fork that becomes a
  template of its own deletes `.process-lock.json` once and runs `lock.py`.

### What the template's files hold

- The process only: never a project's milestones, documents or tools.
- Never an `@` right before a path: `process-owner` reads that as an import.
