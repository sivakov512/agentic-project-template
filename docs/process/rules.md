# Rules for agents

These rules come from the template and hold in every project made from it. The project's own rules are
in `CLAUDE.md` around the line that imports this file; they may add to these rules and make them
stricter, never looser. How the whole process works: [README.md](README.md).

## Which role you are

The first of these that fits is your role:

1. **Your first message is "Do B-###":** you are a work session. Follow "Your work" below.
2. **It is "Fix pull request #N":** you are a work session fixing review findings. Follow "If you fix a
   pull request".
3. **It is "Review pull request #N":** you are a reviewer. Follow "If you are the reviewer".
4. **This repository is the template** (the `owner/name` of its `origin` remote is the `template` in
   `.process-lock.json`): you are the template's coordinator. Changes to the process go as
   [updates.md](updates.md#changing-the-process) says; the rest of [coordinator.md](coordinator.md)
   holds where it applies.
5. **The project is not set up yet** (`docs/process.json` on `main` says `"set_up": false`): you are
   setting it up. Follow [setup.md](setup.md).
6. **Anything else, from the owner:** you are the coordinator. Follow [coordinator.md](coordinator.md),
   starting from `docs/now.md`.

Whatever your role: a question from the owner is a question. Answer it and propose; act only after a yes.

## Where you get information

- **Only from this repository.** Not from chat history, other folders on this machine, older copies of
  the project or other repositories. The exceptions, each only for what it names: a source outside the
  repository that your backlog item or the owner names (a path, a repository, a link); the template, for
  a process update, for adopting the process, or for a change proposed to it; the tracker, which only
  the coordinator reads and writes, to keep it in step, never to learn what to do.
- If something you need is not here, stop and say so in your report; don't fill the gap from memory or
  guesswork.
- The spec is the document chain in `docs/plan.md`, read from the top. A change starts in the highest
  document it touches ([changes.md](changes.md)).

## Your work

- You are given one backlog item from `docs/backlog.md` as "Do B-###". Read the item and every document
  it links before you start. If you continue an interrupted item, find its branch and open pull request
  and continue there.
- Work on your own branch, named `b-###-short-name`. Never commit to `main`.
- **Questions first.** Before any work, open a draft pull request with a short plan (what you will
  change and how you will check it) and your questions about the item, or "no questions". GitHub needs a
  commit to open one: start the branch with an empty commit (`git commit --allow-empty -m "Start
  B-###"`, or in the form the project's commit rules ask for). With questions, end your turn and say
  in your last message that you wait for answers in the pull request; the coordinator answers there and
  tells you to go on (a message to your session). With no questions, go on at once.
- **Do only that item, and no more than it needs.** Its "Done when" is the bar. Tools for our own use get
  no options, modes or cases nobody needs yet.
- If the item is unclear, wrong, or conflicts with a document above it, stop and report; don't widen or
  reinterpret it. If your work shows that a document above your item is wrong, report it rather than
  change it, unless your item says so. Facts you find by experiment are the exception: record them where
  `docs/plan.md` says facts go, with the date and how you found them, and report them too if they
  contradict your item.
- A bug or gap you find that your item doesn't cover is reported in your pull request's "Not done and
  open questions", not fixed in it: the coordinator makes it an item of its own.
- A pull request stays reviewable: about 800 changed lines at most, generated files, data and removed
  files aside. If the item needs more, stop and report; the coordinator splits it.
- **To stop and report:** push what you have, keep the pull request in draft (its checks may fail then),
  say what is left and why in its "Not done and open questions", and say the same in your last message.
  The coordinator decides whether the pull request goes on, split or not, or is closed.
- Before you push, run `python3 tools/process/check.py` (the process checks and the project's own) and
  `python3 tools/process/check_pr.py --body <description file> --title "<title>" --labels
  <kind>,<review label>`. Finish only with every check passing.
- Tick your item in the backlog (`- [x]`) in the same pull request. Don't edit `docs/now.md`: the
  coordinator does.
- Don't edit the template's files ([README.md](README.md#what-lives-where)). If the process is wrong,
  report it; the coordinator proposes a change to the template.

## Your pull request is your report

- Fill in every section of `.github/pull_request_template.md`, and name and label it as
  [pull-requests.md](pull-requests.md) says. CI rejects a pull request that doesn't.
- "How it was checked" gives commands, output or screenshots someone else can repeat. "It works" is not
  evidence.
- Your report is not proof: the coordinator checks the diff, the checks and the running result.

## If you fix a pull request

- Read the reviewer's comment on the pull request. Fix every finding marked **fix**, on the pull
  request's branch; leave the **drop** ones.
- Run the checks as in "Your work", push, and answer with one comment: for each "fix" finding, what you
  changed and where, or why you couldn't. The coordinator then runs the second round.

## If you are the reviewer

- Check the pull request against its item's "Done when" and the documents it links. Look for what is
  wrong or missing, not for reasons to approve.
- Check that the evidence in the pull request is real: repeat it where you can.
- Post your findings as one comment on the pull request: each with the file and line, what is wrong and
  why it matters, and marked **fix** (wrong behaviour, a risk the project's rules name, a wrong or
  unsupported fact, a red or flaky check, documents that contradict each other, or a gap the next item
  would trip on) or **drop** (wording, taste, layout, or no effect on the result or the next steps) with
  a one-line reason. Nothing is put off for later. Don't fix things yourself.
- A second round comes only if the first had "fix" findings: review only the fix, whether each is fixed
  and whether the fix broke anything nearby.

## Writing

- Write for the next reader, briefly: say each thing once, and link to the document that says it rather
  than restating it.
- Everything in the repository is in English: docs, code, comments, commits, pull request titles and
  descriptions, and what agents write to each other in pull requests. Docs in plain words.
- Talk with the owner is in the owner's language (`owner_language` in `docs/process.json`; before it is
  set, the language the owner writes in): the chat, questions to the owner, and comments on pull
  requests addressed to the owner. Text proposed for the repository is quoted in English.
- A commit subject is at most 72 characters; `docs/process.json` may ask for more
  ([config.md](config.md#commits)).

## Git and GitHub

- Commits, pushes and pull requests go out under the account the project chose for agents
  ([workflow.md](workflow.md#the-owners-ok-and-the-merge)). Call `git` and `gh` by name.
- Open pull requests through the REST API (`gh api repos/{owner}/{repo}/pulls`), so nothing adds text
  to the description you wrote.
- Nobody but the coordinator merges, and only after the owner's OK, by rebase; or the owner merges, as
  the project chose ([workflow.md](workflow.md#the-owners-ok-and-the-merge)).
