# Defences

What could go wrong, what stops it, and where that is enforced. `docs/plan.md` adds the project's own.

| What goes wrong | What stops it | Enforced by |
|---|---|---|
| An agreement is lost between chats | The repository is the only source; same-day records; `docs/now.md`; sessions start from the repository | The rules, the cold-start test |
| A stage or item starts before its inputs exist | Exit lists; items start only when their dependencies are merged and their stage has started | The coordinator, the reviewer |
| Parts built by different items don't fit, or a stage finds what it builds on missing | Interfaces written in a document before the items on either side; each stage written out at the end of the one before, with what it builds on named | The coordinator, the reviewer, the owner at the gate |
| Something is forgotten | IDs and coverage | CI (`process-docs`) |
| A session does something other than its item, or more | The brief is the item; a reviewer compares the diff with "Done when"; a session stops when its item is unclear | The rules, the reviewer |
| "Done" without proof | The pull request asks for evidence someone can repeat; the reviewer repeats it; the coordinator checks the result personally | The reviewer, the coordinator (CI only checks the section is there) |
| A refactor quietly changes behaviour | "Behaviour change" in every pull request, with steps to try it | The reviewer, the owner (CI only checks the section's form) |
| A session loosens the rules or the checks | Changes to the plan, `CLAUDE.md` and the process need the owner's review; the template's files are locked; changes to checks and CI are reported with what they loosen | CI (`process-docs`, `process-lock`) against mistakes, the owner and the coordinator against the rest ([pull-requests.md](pull-requests.md#the-checks-ci-runs)) |
| The process drifts apart between projects | One template; the lock; `doctor.py` reports a newer release at every coordinator session | CI, the coordinator |
| Reviewers share the authors' blind spots | "Done when" is written before the work; reviewers look for problems; the owner tries the result | The plan, the reviewer, the owner |
| A merge without the owner's OK | `main` takes changes only through pull requests; with the agents' own account, only with the owner's Approve, dismissed by a new commit | GitHub branch protection; with the owner's account, the rules ([workflow.md](workflow.md#the-owners-ok-and-the-merge)) |
| The owner is swamped, or misses what matters | Reports with Review or OK without reading; the owner's part fixed for each stage | The coordinator |
| A question from the owner is taken as an order | Answer and propose, act after a yes | The rules |
| The setup is broken and nobody notices | `doctor.py` at the start of every coordinator session | The coordinator |
