# Pull requests

So the owner can see from the list what each pull request is and whether to read it.

## Kind and labels

- **Its kind is its purpose,** not every file it touches: changes that follow from the work (the backlog
  tick or the split of its own item, `docs/now.md`, links) don't count. A pull request with two purposes is two pull requests.

  | Kind | Title starts with | For |
  |---|---|---|
  | `plan` | `Plan:` | the plan, rules for agents, the process, the commands of the checks, and CI |
  | `spec` | `Spec:` | what the product must do and how it looks: the documents of the chain above the code |
  | `research` | `Research:` | studies, facts found by experiment |
  | `code` | `Code:` | the code of the tools (the code the checks run among it) and of the product |

  A coordinator record takes the kind of what it records: `plan` for `docs/now.md`, the backlog and the
  plan, `spec` for a document of the chain, and a decision record the kind of what it decides.
- **Two labels:** its kind, and `owner-review` or `ok-without-reading` ([reports.md](reports.md)). The
  review label follows the strictest part of the pull request.

## The description

Every section of `.github/pull_request_template.md`, filled in.

- **Backlog item** names the one item the pull request does, or one of these for a pull request that is
  not product work:

  | It says | For |
  |---|---|
  | `Coordinator record` | the coordinator's own records: the owner's decisions, `docs/now.md`, the backlog |
  | `Setup` | setting up a project, or adopting the process in one ([setup.md](setup.md)) |
  | `Process update` | bringing a newer version of the process from the template ([updates.md](updates.md)) |
  | `Process change` | a change to the process, in the template itself |

- **Behaviour change** says `None` and why nothing changes for whoever uses the result, or `Yes` and at
  least three steps the owner can follow to try the change by hand. It is how a refactor that changes
  behaviour gets caught.
- **Owner review** says what the owner should look at and how long it takes, or why no reading is
  needed.

## The checks CI runs

The workflows `.github/workflows/process-*.yml` run these jobs; their names start with `process-` so they never
clash with the project's own.

| Job | Runs | Checks |
|---|---|---|
| `process-docs` | `tools/process/check.py --process-only` | the documents (links, the backlog, IDs and coverage, decision records), the template's files against the lock, the checks' own tests |
| `process-pr` | `tools/process/check_pr.py` | the sections of the description, the title and the labels; a draft is checked when it leaves draft |
| `process-lock` | `tools/process/check_lock.py` | a pull request that changes the template's files moves to a newer version ([updates.md](updates.md#the-lock)) |
| `process-commits` | `tools/process/check_commits.py` | the commit messages ([config.md](config.md#commits)) |
| `process-owner` | `tools/process/check_owner.py` | a pull request that needs the owner's OK has the owner's approval of its last commit, and one labelled `ok-without-reading` changes nothing the owner keeps for themself, a process update that is exactly the template's release aside ([workflow.md](workflow.md#the-owners-ok-and-the-merge)); it runs again on every review and reads the labels and reviews as they are when it runs; a passing run runs again the red ones earlier events left on the same commit, which would block the merge; if one stays red, `gh run list --workflow process-owner.yml --commit <the pull request's last commit>`, then `gh run rerun <id>` |

Pull requests opened by a GitHub App (a release bot, a dependency bot) skip `process-pr`: they don't
follow the template. Their other checks run; with no review label they need the owner's OK, and the coordinator labels
them after its review ([reports.md](reports.md#when-the-owner-looks)). So automation whose pull requests don't follow the template (a release tool run in CI, say)
opens them with a GitHub App's token, not with the agents' or the owner's; a process update follows the
template, and the coordinator opens it under the agents' account. One that changes the template's files (a dependency bot
bumping an action in `process-*.yml`) is closed: such changes come from the template.

These checks catch mistakes, not a determined agent: a pull request runs its own copy of the workflow
and the scripts, so one that also edits them could get round them. `process-owner` is the exception:
it runs the check from the base branch's copy as it is now, and with the agents' own account `.github/CODEOWNERS` gives the
owner its workflow, so GitHub asks for the owner's review of any pull request that changes it
([setup.md](setup.md), step 8). That is why every change to the
process, the commands of the project's checks and CI needs the owner's OK ([reports.md](reports.md)).

The project's own CI (builds, product tests, its own rules for pull requests) is in
`.github/workflows/project-*.yml`, with job names of its own.
