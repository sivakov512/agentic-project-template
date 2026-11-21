# Rules for agents

These rules come from the template and hold in every project made from it. The project's own rules are
in `CLAUDE.md` around the line that imports this file; they may make these stricter, never looser, apart
from the choices these rules leave to the project. How the whole process works:
[README.md](README.md).

## Which role you are

The first of these that fits is your role:

1. **Your first message is "Do B-###":** you are a work session. Follow "Your work" below.
2. **It is "Fix pull request #N":** you are a work session fixing findings. Follow "If you fix a pull
   request".
3. **It starts with "Review":** you are a reviewer. Follow [reviews.md](reviews.md).
4. **This repository is the template** (the `owner/name` of its `origin` remote is the `template` in
   `.process-lock.json`): you are the template's coordinator. Run `doctor.py` at the start of a
   session. Changes to the process go as [updates.md](updates.md#changing-the-process) says.
5. **The project is not set up yet** (`docs/process.json` on `main` says `"set_up": false`): you are
   setting it up. Follow [setup.md](setup.md).
6. **Anything else, from the owner:** you are the coordinator. Follow [coordinator.md](coordinator.md).

Whatever your role: a question from the owner is a question. Answer it and propose; act only after a yes.

## Where you get information

- **Only from this repository:** not from chat history, other folders on this machine, older copies of
  the project or other repositories. The exceptions, each only for what it names:
  - a source outside the repository that your backlog item or the owner names;
  - the template, for a process update, for adopting the process, or for a change proposed to it;
  - the tracker, which only the coordinator reads and writes, to keep it in step, never to learn what
    to do.
- If something you need is not here, stop and say so in your report; don't fill the gap from memory or
  guesswork.
- The spec is the document chain in `docs/plan.md`. Where your item leaves a question, look it up from
  the top of the chain down.

## Your work

- Read your item in `docs/backlog.md` and every document it links before you start. If the item was
  started before you, continue on its branch and pull request.
- Work on your own branch, `b-###-short-name`. Never commit to `main`.
- **Questions first.** Before any work, open a draft pull request with a short plan (what you will change
  and how you will check it) and your questions, or "no questions". Start the branch with
  `git commit --allow-empty -m "chore: start B-###"`, since GitHub needs a commit to open one. With
  questions, end your turn and say that you wait for answers in the pull request. With none, go on.
- **Do only your item, and no more than it needs.** Its "Done when" is the bar. Tools for our own use get
  no options, modes or cases nobody needs yet.
- If the item is unclear, wrong, or conflicts with a document above it, stop and report; don't widen or
  reinterpret it. If a document above it is wrong, report that too rather than change it.
- Facts you find by experiment you record where `docs/plan.md` says facts go, with the date and how you
  found them.
- A bug or gap your item doesn't cover goes under "Not done and open questions", not into the fix.
- A pull request stays reviewable: about 800 changed lines at most, generated files, data and removed
  files aside. If the item needs more, stop and report.
- **To stop and report:** push what you have, keep the pull request in draft, and say what is left and
  why under "Not done and open questions" and in your last message.
- Before every push, run these, and finish only with all passing (`check_pr.py` from when the pull
  request leaves draft):
  - `python3 tools/process/check.py`;
  - `python3 tools/process/check_pr.py --body <description file> --title "<title>" --labels <label>`;
  - `python3 tools/process/check_commits.py --title "<title>" --number <its number>`.
- Tick your item in the backlog (`- [x]`) in the same pull request. Don't edit `docs/now.md`.
- When every point of "Done when" is met and the checks pass, fill in the description
  ([pull-requests.md](pull-requests.md)) and mark the pull request ready (`gh pr ready`). Where the
  project's `CLAUDE.md` asks for the reviews in draft, leave it in draft and say in a comment on it, and
  in your last message, that the work is done at its last commit
  ([workflow.md](workflow.md#reviews-in-draft)).
- A pull request that changes what a person sees gives in "How it was checked" what the UI review needs
  ([reviews.md](reviews.md#the-ui-review)).
- Don't edit the template's files ([README.md](README.md#what-lives-where)). If the process is wrong,
  report it.

## If you fix a pull request

- Read every review comment on the pull request and those the coordinator posted.
- Fix every finding marked **fix**, except those marked "outside the item", which you list under "Not
  done and open questions", and those the coordinator closed. Leave the **drop** ones.
- Commit the fixes on top of the branch, run the checks as in "Your work", and push.
- Answer with one comment: the new head commit, and for each "fix" finding what you changed and where,
  or why you couldn't.

## Writing

- Write for the next reader, briefly: say each thing once, and link to the document that says it rather
  than restating it.
- Everything in the repository is in English: docs, code, comments, commits, pull requests. Docs in plain
  words.
- Talk is in the owner's language (`owner_language` in `docs/process.json`; before it is set, the
  language the owner writes in): the chat and every comment and review on pull requests. Text proposed
  for the repository is quoted in English.
- To the owner, anything with an ID is said in plain words first, the ID after it in brackets: "the
  test of the cable length, about 20 minutes (T-013)".

## Code

A reader must be able to tell what a piece of code is for and how to use it without working through the
rest.

- Every module opens with a comment in plain sentences: what it is for, which part of the design it is,
  what it holds and who uses it.
- Everything a module offers to others has a comment: what it does and why; its inputs, where their names
  and types don't say it all; what it returns, empty results and failures included; the errors it raises.
- A comment says what and why, not how the next line works, and changes with the code it describes.
- Behaviour the code adds or changes is covered by automated tests where the project has a way to run
  them.
- Where the language has a linter for such comments, the project's checks run it.
- The design document of the code lists its folders, one line each: what it holds and, for a name that
  isn't plain, where the name comes from. A new folder goes into the list in the pull request that makes
  it. The project's checks include one that fails on a folder missing from the list.

## Git and GitHub

- Commits, pushes and pull requests go out under the agents' own account
  ([owner.md](owner.md#the-owners-ok)). Call `git` and `gh` by name. Agents never approve a pull
  request: an approval is the owner's OK.
- A pull request lands on `main` as one squash commit, its subject the pull request's title. The commits
  on the branch are only its working history.
- A fix is a new commit on top. Take in what others pushed first (`git pull --no-rebase origin
  <branch>`). Never rewrite what is pushed (no rebase, no force push), so the head a reviewer reviewed
  stays readable. A conflict with `main` is resolved by merging `origin/main` into the branch.
- Open pull requests through the REST API (`gh api repos/{owner}/{repo}/pulls`), so nothing adds text to
  the description you wrote.
- Only the coordinator or the owner merges.
