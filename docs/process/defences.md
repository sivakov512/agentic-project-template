# Defences

What could go wrong and what stops it. The threat is agents' mistakes, not malice. `docs/plan.md` adds the
project's own.

| What goes wrong | What stops it |
|---|---|
| An agreement is lost between chats | The repository is the only source; same-day records; `docs/now.md`; the gate review compares it with the repository |
| Work starts before what it needs exists, or parts built apart don't fit | Exit lists and "Depends on"; interfaces written down before the items on either side |
| A session does more or other than its item, or calls unchecked work done | The brief is the item; the reviewer compares the diff with "Done when" and repeats the evidence |
| Code nobody can follow | Comments on every module; the review's three points; the gate review reads whole modules |
| A defect in risky code gets past one review | A second, independent review for harm |
| Nothing reaches the owner to use | Milestones that each end with something the owner uses in real work |
| Something is forgotten | IDs and coverage, checked by `process-docs` |
| A merge without the owner's OK, or one that loosens the rules or the checks | `process-owner`, run from `main`'s copy and required for `main`; `.github/` reviewed by the owner as code owner; the template's files locked |
| A merge on an old `main` breaks it | `merge.py` merges only when the checks ran on the current `main` |
| A broken process release stops every project | Reverting the update ([updates.md](updates.md#when-a-release-breaks-the-project)) |
| A tag off the template's `main` brings an unapproved process into projects | Projects take only releases whose tag is on the template's `main`; a tag ruleset |
| The agents act as the owner | `doctor.py` fails when `gh` works as the repository's owner |
| A stranger's pull request runs on the owner's own runner | `doctor.py` fails a public repository with `CI_RUNNER` set |
| The owner is swamped, or misses what matters | The owner looks only where they decide something; the rest is listed in reports |
| A question from the owner is taken as an order | Answer and propose, act after a yes |

The checks catch mistakes, not a determined agent: a pull request runs its own copy of the workflows and
scripts. `process-owner` is the exception, since it runs from the base branch's copy, and
`.github/CODEOWNERS` gives the owner its workflow.
