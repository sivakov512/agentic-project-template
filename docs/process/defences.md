# Defences

What could go wrong, what stops it, and where that is enforced. `docs/plan.md` adds the project's own.

| What goes wrong | What stops it | Enforced by |
|---|---|---|
| An agreement is lost between chats | The repository is the only source; same-day records; `docs/now.md`; sessions start from the repository | The rules, the cold-start test |
| A stage or item starts before its inputs exist | Exit lists; items start only when their dependencies are merged and their stage has started | The coordinator, the reviewer |
| Parts built by different items don't fit, or a stage finds what it builds on missing | Interfaces written down once, before the items on either side; each stage written out at the end of the one before, with what it builds on named | The coordinator, the reviewer, the owner at the gate |
| Code nobody can follow or maintain | Comments on every module and on what it offers; the reviewer's verdict on understood, fits the design, easy to change | The reviewer, the project's lint |
| `main`'s history fills with review rounds | Fixes are folded into the commits they correct before the merge | The rules, the coordinator |
| Work goes into documents, and nothing reaches the owner to use | Increments, each ending with something the owner uses in real work; requirements and design only for the current increment | The plan, the coordinator, the owner at the gate |
| Something is forgotten | IDs and coverage | CI (`process-docs`) |
| A session does something other than its item, or more | The brief is the item; a reviewer compares the diff with "Done when"; a session stops when its item is unclear | The rules, the reviewer |
| "Done" without proof | The pull request asks for evidence someone can repeat; the reviewer repeats it; the coordinator checks the result personally | The reviewer, the coordinator (CI only checks the section is there) |
| A refactor quietly changes behaviour | "Behaviour change" in every pull request, with steps to try it | The reviewer, the owner (CI only checks the section's form) |
| A session loosens the rules or the checks | Changes to the plan, `CLAUDE.md`, the process, the commands of the checks and CI need the owner's OK; the template's files are locked; a change that loosens the checks, in whatever file, needs the owner's OK | CI (`process-docs`, `process-lock`, `process-owner`) against mistakes, the owner and the coordinator against the rest ([pull-requests.md](pull-requests.md#the-checks-ci-runs)) |
| The process drifts apart between projects | One template; the lock; `doctor.py` reports a newer release at every coordinator session | CI, the coordinator |
| A defect in risky code (a leaked secret, a broken machine) gets past one review | A second, independent review for harm of the code `docs/plan.md` names as risky | The coordinator, the reviewers |
| Reviewers share the authors' blind spots | "Done when" is written before the work; reviewers look for problems; the owner tries the result | The plan, the reviewer, the owner |
| A merge without the owner's OK | `main` takes changes only through pull requests; one that needs the owner's OK, and every one that changes the plan, `CLAUDE.md`, the settings, CI or the process (a process update's files that are exactly the template's release aside), only with the owner's Approve of its last commit | CI (`process-owner`), required for `main` by GitHub; with the owner's account, the rules ([workflow.md](workflow.md#the-owners-ok-and-the-merge)) |
| The owner is swamped, or misses what matters | The owner's OK only where they decide something; the rest merged by the coordinator and listed in reports; the owner's part fixed for each stage | The coordinator, CI (`process-owner`) |
| A question from the owner is taken as an order | Answer and propose, act after a yes | The rules |
| The setup is broken and nobody notices | `doctor.py` at the start of every coordinator session | The coordinator |
