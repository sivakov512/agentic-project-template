# Pull requests

## Kind, title and label

- **Its kind is its purpose,** not every file it touches: what follows from the work (the backlog tick,
  `docs/now.md`, links) doesn't count. A pull request with two purposes is two pull requests.
- **The title** follows the commit rules ([config.md](config.md#commits)) and shows the kind: it starts
  with the kind's prefix, or, with Conventional Commits, with a type and scope that show it:

  | Kind | Title starts with | With Conventional Commits | For |
  |---|---|---|---|
  | `plan` | `Plan:` | `docs(plan):`, or `ci:` and `build:` for CI and the checks | the plan, rules for agents, the process, the checks and CI |
  | `spec` | `Spec:` | `docs(spec):` | the documents of the chain above the code: what the product must do and how it looks |
  | `research` | `Research:` | `docs(research):` | studies, facts found by experiment |
  | `code` | `Code:` | `feat:`, `fix:`, `refactor:` and the like | the code of the product and of its tools |

  A coordinator record takes the kind of what it records: `plan` for `docs/now.md`, the backlog and the
  plan, `spec` for a document of the chain. `update.py` titles a process update `Plan: ...`, or
  `chore: ...` with Conventional Commits.
- **One label:** `owner-review` or `ok-without-reading` ([owner.md](owner.md#the-review-label)). Other
  labels are not read.

## The description

Every section of `.github/pull_request_template.md`, filled in as its comments say. A coordinator record
or a process update needs only "Backlog item", "What changed" and "Owner review".

"Backlog item" names the one item the pull request does, or, for a pull request that is not product
work, one of these:

| It says | For |
|---|---|
| `Coordinator record` | the coordinator's own records: the owner's decisions, `docs/now.md`, the backlog |
| `Setup` | setting up a project, or adopting the process in one ([setup.md](setup.md)) |
| `Process update` | bringing a newer version of the process from the template ([updates.md](updates.md)) |
| `Process change` | a change to the process, in the template itself |

## The checks CI runs

The workflows `.github/workflows/process-*.yml` run these jobs, all required for `main`:

| Job | Runs | Checks |
|---|---|---|
| `process-docs` | `tools/process/check.py --process-only` | the documents (links, the backlog, IDs and coverage, decision records), the template's files against the lock, the workflows, the checks' own tests |
| `process-pr` | `tools/process/check_pr.py` | the description's sections, the kind in the title and the label; a draft only once it leaves draft |
| `process-commits` | `tools/process/check_commits.py` | the title against the commit rules ([config.md](config.md#commits)) |
| `process-lock` | `tools/process/check_lock.py` | a pull request that changes the template's files moves to a newer version ([updates.md](updates.md#the-lock)) |
| `process-owner` | `tools/process/check_owner.py` | a pull request that needs the owner's OK has the owner's Approve of its last commit, and one labelled `ok-without-reading` changes nothing the owner keeps ([owner.md](owner.md#the-owners-ok)); it runs again on every review |

Every workflow on pull requests, the project's own included, runs on `reopened`, since `merge.py` runs
the checks again by reopening the pull request ([workflow.md](workflow.md#the-merge)). One whose jobs
run only on another event (a label, say) then leaves a skipped run, whose age `merge.py` doesn't
count; it never hides an earlier red run.

A passing run of `process-pr` or `process-owner` runs again the failed jobs earlier events left red on
the same commit. If one stays red: `gh run list --workflow <file> --commit <last commit>`, then
`gh run rerun <id>`.

### Pull requests from a GitHub App

Pull requests opened by a GitHub App (a release bot, a dependency bot) skip `process-pr`, since they
don't follow the template; their other checks run.

- Automation whose pull requests don't follow the template opens them with a GitHub App's token, not the
  agents' or the owner's.
- One that changes the template's files (a bot bumping an action in `process-*.yml`) is closed: such
  changes come from the template.
