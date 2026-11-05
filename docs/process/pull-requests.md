# Pull requests

## Kind, title and label

- **Its kind is its purpose,** not every file it touches: changes that follow from the work (the backlog
  tick or the split of its own item, `docs/now.md`, links) don't count. A pull request with two purposes
  is two pull requests.
- **The title** follows the commit rules ([config.md](config.md#commits)) and shows the kind: it starts
  with the kind's prefix, or, where they ask for Conventional Commits, with the type and scope that show
  the kind:

  | Kind | Title starts with | With Conventional Commits | For |
  |---|---|---|---|
  | `plan` | `Plan:` | `docs(plan):` | the plan, rules for agents, the process, the commands of the checks, and CI |
  | `spec` | `Spec:` | `docs(spec):` | what the product must do and how it looks: the documents of the chain above the code |
  | `research` | `Research:` | `docs(research):` | studies, facts found by experiment |
  | `code` | `Code:` | `feat:`, `fix:`, `refactor:` and the like | the code of the tools (the code the checks run among it) and of the product |

  `update.py` titles a process update by the commit rules: `Plan: ...`, or `chore: ...` under
  Conventional Commits. A coordinator record takes the kind of
  what it records: `plan` for `docs/now.md`, the backlog and the plan, `spec` for a document of the
  chain, and a decision record the kind of what it decides.
- **One label:** `owner-review` or `ok-without-reading`, which follows the strictest part of the pull
  request ([reports.md](reports.md#the-review-label)). Other labels are not read.

## The description

Every section of `.github/pull_request_template.md`, filled in as its comments say. A `Coordinator
record` or a `Process update` needs only "Backlog item", "What changed" and "Owner review".

"Backlog item" names the one item the pull request does, or one of these for a pull request that is not
product work:

| It says | For |
|---|---|
| `Coordinator record` | the coordinator's own records: the owner's decisions, `docs/now.md`, the backlog |
| `Setup` | setting up a project, or adopting the process in one ([setup.md](setup.md)) |
| `Process update` | bringing a newer version of the process from the template ([updates.md](updates.md)) |
| `Process change` | a change to the process, in the template itself |

## The checks CI runs

The workflows `.github/workflows/process-*.yml` run these jobs; their names start with `process-` so they
never clash with the project's own.

| Job | Runs | Checks |
|---|---|---|
| `process-docs` | `tools/process/check.py --process-only` | the documents (links, the backlog, IDs and coverage, decision records), the template's files against the lock, the checks' own tests |
| `process-pr` | `tools/process/check_pr.py` | the sections of the description, the kind in the title and the review label; a draft is checked when it leaves draft |
| `process-lock` | `tools/process/check_lock.py` | a pull request that changes the template's files moves to a newer version ([updates.md](updates.md#the-lock)) |
| `process-commits` | `tools/process/check_commits.py` | the title against the commit rules ([config.md](config.md#commits)); a job of `process-pr.yml`, so it runs on the same events |
| `process-owner` | `tools/process/check_owner.py` | a pull request that needs the owner's OK has the owner's approval of its last commit, and one labelled `ok-without-reading` changes none of the files CI holds for the owner ([workflow.md](workflow.md#the-owners-ok-and-the-merge)); it runs again on every review |

A passing run of `process-pr` or `process-owner` runs again the failed jobs of the red runs earlier events
left on the same commit, which would block the merge. If one stays red, `gh run list --workflow
<process-pr.yml or process-owner.yml> --commit <the pull request's last commit>`, then `gh run rerun
<id>`.

### Pull requests from a GitHub App

Pull requests opened by a GitHub App (a release bot, a dependency bot) skip `process-pr`: they don't
follow the template. Their other checks run, `process-commits` among them.

- Automation whose pull requests don't follow the template (a release tool run in CI, say) opens them
  with a GitHub App's token, not with the agents' or the owner's.
- A process update follows the template, and the coordinator opens it under the agents' account.
- One that changes the template's files (a dependency bot bumping an action in `process-*.yml`) is
  closed: such changes come from the template.

### What the checks can't stop

These checks catch mistakes, not a determined agent: a pull request runs its own copy of the workflow
and the scripts, so one that also edits them could get round them. `process-owner` is the exception: it
runs the check from the base branch's copy as it is now, and with the agents' own account
`.github/CODEOWNERS` gives the owner its workflow, so GitHub asks for the owner's review of any pull
request that changes it ([setup.md](setup.md), step 8).
