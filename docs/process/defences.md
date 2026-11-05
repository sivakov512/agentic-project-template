# Defences

What could go wrong, what stops it, and where that is enforced. `docs/plan.md` adds the project's own.

| What goes wrong | What stops it | Enforced by |
|---|---|---|
| An agreement is lost between chats | The repository is the only source; same-day records; `docs/now.md` | The rules, the cold-start test |
| A milestone or item starts before its inputs exist | Exit lists; an item starts only when its dependencies are merged and its milestone has started | The coordinator, the reviewer |
| Parts built by different items don't fit, or a milestone finds what it builds on missing | Interfaces written down before the items on either side; each milestone written out at the end of the one before | The coordinator, the reviewer, the owner at the gate |
| Code nobody can follow or maintain | Comments on every module and on what it offers; the reviewer's three-point verdict | The reviewer, the project's lint |
| `main`'s history fills with review rounds | One squash commit per pull request | The merge settings, which `doctor.py` checks; `process-commits` for the title |
| Work goes into documents, and nothing reaches the owner to use | Milestones that each end with something the owner uses in real work | The plan, the coordinator, the owner at the gate |
| Something is forgotten | IDs and coverage | `process-docs` |
| A session does something other than its item, or more | The brief is the item; a reviewer compares the diff with "Done when" | The rules, the reviewer |
| "Done" without proof | Evidence someone can repeat, which the reviewer repeats; the coordinator checks the result itself | The reviewer, the coordinator |
| A refactor quietly changes behaviour | "Behaviour change" in every pull request, with steps to try it | The reviewer, the owner |
| A session loosens the rules or the checks, or widens its own permissions | What the owner keeps needs the owner's OK; the template's files are locked | `process-docs`, `process-lock` and `process-owner` against mistakes, the owner and the coordinator against the rest ([pull-requests.md](pull-requests.md#what-the-checks-cant-stop)) |
| A tag made or moved off the template's `main` brings an unapproved process into projects | Projects trust a release only when its tag is on the template's `main`; a workflow tags on merge; a tag ruleset stops tags being moved or deleted | `check_owner.py`, `update.py`, the owner's ruleset |
| A broken release stops every project | Reverting the update ([updates.md](updates.md#when-a-release-breaks-the-project)) | The coordinator, the owner |
| The agents act as the owner, or the owner's account merges past the checks | `doctor.py` fails when gh's account doesn't fit `agents_account` or classic protection lets admins past its checks, and asks the owner to check a ruleset's bypass list | The coordinator |
| A stranger's pull request runs on the owner's own runner | `doctor.py` fails a public repository with `CI_RUNNER` set | The coordinator |
| The process drifts apart between projects | One template; the lock; `doctor.py` reports a newer release | CI, the coordinator |
| A defect in risky code gets past one review | A second, independent review for harm | The coordinator, the reviewers |
| Reviewers share the authors' blind spots | "Done when" is written before the work; reviewers look for problems; the owner tries the result | The plan, the reviewer, the owner |
| A merge without the owner's OK | `main` takes changes only through pull requests; one that needs the owner's OK only with the owner's Approve of its last commit | `process-owner`, required for `main` and run from `main`'s copy, and code owners' review of `.github/`; with the owner's account, the rules ([workflow.md](workflow.md#the-owners-ok-and-the-merge)) |
| The owner is swamped, or misses what matters | The owner's OK only where they decide something; the rest merged by the coordinator and listed in reports | The coordinator, `process-owner` |
| A question from the owner is taken as an order | Answer and propose, act after a yes | The rules |
| The setup is broken and nobody notices | `doctor.py` at the start of every coordinator session | The coordinator |
