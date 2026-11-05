<!-- template placeholder -->
# agentic-project-template

A GitHub repository template for building a product with AI agents, from the first idea to a working
result, while you stay in control. The agents research, write the spec, plan, build, review each
other's work and report to you. You decide what matters: the agents bring you what needs your decision
and merge the rest themselves after their own reviews and checks, listing it in their reports.

It is for a person who wants agents to carry a whole project, not just write code on request, and
needs the work to stay understandable and correctable months later.

## The problem it solves

Agents work in sessions that start with no memory. Left alone, they lose agreements made in an earlier
chat, drift from what was decided, widen their tasks, call unchecked work "done", and leave the owner to
dig through a pile of changes to find what needs a decision.

This template puts the whole process into the repository, as rules the agents read and checks CI runs:

- **The repository is the only source of truth.** Plans, specs, decisions, the backlog and where the
  work stands live in files. Any fresh session picks up the work from them alone; nothing depends on
  chat history.
- **Upstream first.** The work goes from what the product must do, through the design, to the backlog
  and the code. A change starts in the highest document it touches and is carried down, so the code
  never drifts from the spec.
- **One item, one pull request.** Every piece of work is a backlog item with a clear "Done when". A
  session does exactly that item, asks its questions first, and reports with evidence someone can
  repeat.
- **Review before you see it.** A second agent with a fresh context checks each pull request against
  its item and the spec before the owner is asked.
- **You decide, briefly.** Each report says what needs your review and lists what was merged without
  it. Settings come to you as clicks, questions in a batch with a recommendation.
- **Checked, not trusted.** CI checks links, the backlog, IDs and their coverage (every requirement has
  a source, every scenario has steps), pull request descriptions and titles.

## How work goes

```
idea ─► spec ─► backlog item ─► draft PR with questions ─► work ─► review by an agent ─► report ─► your OK, where needed ─► merge
```

Four roles do it:

| Role | Who | Does |
|---|---|---|
| Owner | you | Gives the goal and remarks, reviews and approves what matters. |
| Coordinator | an agent session | Runs the plan like a product manager: writes backlog items, starts work sessions and reviewers, checks results, reports to you, keeps your tracker in step. |
| Work session | an agent session | Does one backlog item in one pull request. |
| Reviewer | an agent with a fresh context | Looks for problems in a pull request; doesn't approve. |

The details are in [`docs/process/`](docs/process/README.md).

## Start a project

1. **Use this template** on GitHub to make a new repository.
2. **Choose whose account the agents work under:**
   - **an account of their own (recommended).** GitHub itself keeps what needs you from merging
     without your Approve. It needs a second GitHub account, invited to the repository with Write
     access (not Admin), with a token that may change workflow files; the repository under your
     personal account, not an organisation; and your own login kept off wherever the agents run.
   - **your account.** Simpler to set up, but the agents act with your full GitHub access, everything
     carries your name, and only their rules stop a merge without your OK, which you give in the chat
     or by merging yourself.
3. **Open an agent session** (Claude Code) in the repository, signed in to `git` and `gh` as that
   account, and say in a few lines what the project is.
4. **The agent sets the project up.** It asks you what it needs to know: the goal, your tracker, how
   the project ships. Then it brings one pull request with the plan, the milestones, the first backlog
   items, and a short list of repository settings for you to click.

From then on you talk to the coordinator: give it goals and remarks, answer its questions, approve
what needs you.

## What you will be asked

- At each gate: accept what the milestone delivered and agree the plan of the next one.
- The decisions that plan names as yours (an interface, a file format, the stack), each when it is
  ready.
- To use each milestone's result in your real work and say what came up: a milestone isn't finished
  without it.
- Questions in a batch, each with a recommendation; an Approve on GitHub for what needs you; now and
  then a setting to click, or something only you can do (an account, money, hardware).

## What is in it

- [`docs/process/`](docs/process/README.md): the process itself: rules for agents, roles, how a piece
  of work goes, pull requests, reports, decisions and traceability, setting up and updating.
- `tools/process/`: the checks CI runs; `doctor.py`, which tells the coordinator what the setup is
  missing; `update.py`, which brings a newer version of the process into a project.
- Placeholders for what is the project's own: `CLAUDE.md`, `docs/plan.md` (goal, milestones, releases),
  `docs/now.md` (where the work stands), `docs/backlog.md`, `docs/decisions/`, `docs/process.json`
  (settings the checks read).

## Updates

The process files belong to the template and are locked by hash in each project, so a project can't
drift from them by accident. When the template releases a new version, the project's coordinator brings
it in as a pull request and merges it once its checks pass; it comes to you only where it changes what
you keep. A change to the process is made here, never in a project
([`docs/process/updates.md`](docs/process/updates.md)); what changed is in
[`docs/process/CHANGELOG.md`](docs/process/CHANGELOG.md).

## Needs

- GitHub, with GitHub Actions.
- An agent that reads `CLAUDE.md`: the rules are written for Claude Code.
- Python 3.9 or newer for the checks; they use only its standard library.
- The repository is written in English; the agents talk to you in your language.

## License

[MIT](LICENSE). A project made from the template chooses its own license when it is set up; the process
files keep their notice.

This file is the project's: setting up a project replaces it with the project's own README.
