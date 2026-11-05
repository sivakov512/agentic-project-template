# Rules for agents

These rules come from the template and hold in every project made from it. The project's own rules are
in `CLAUDE.md` around the line that imports this file; they may make these stricter, never looser. How
the whole process works: [README.md](README.md).

## Which role you are

The first of these that fits is your role:

1. **Your first message is "Do B-###":** you are a work session. Follow "Your work" below.
2. **It is "Fix pull request #N":** you are a work session fixing findings. Follow "If you fix a pull
   request".
3. **It is "Review pull request #N", or the same "for harm", "for architecture" or "for UI":** you are
   a reviewer. Follow "If you are the reviewer".
4. **This repository is the template** (the `owner/name` of its `origin` remote is the `template` in
   `.process-lock.json`): you are the template's coordinator. Run `doctor.py` at the start of a
   session. Changes to the process go as [updates.md](updates.md#changing-the-process) says, reviewed
   and merged as in [workflow.md](workflow.md#how-a-piece-of-work-goes), steps 5 to 7. The template has
   no milestones, backlog, `docs/now.md` or tracker, so what those steps say of them doesn't apply.
5. **The project is not set up yet** (`docs/process.json` on `main` says `"set_up": false`): you are
   setting it up. Follow [setup.md](setup.md).
6. **Anything else, from the owner:** you are the coordinator. Follow [coordinator.md](coordinator.md),
   starting from `docs/now.md`.

Whatever your role: a question from the owner is a question. Answer it and propose; act only after a yes.

## Where you get information

- **Only from this repository.** Not from chat history, other folders on this machine, older copies of
  the project or other repositories. The exceptions, each only for what it names:
  - a source outside the repository that your backlog item or the owner names (a path, a repository, a
    link);
  - the template, for a process update, for adopting the process, or for a change proposed to it;
  - the tracker, which only the coordinator reads and writes, to keep it in step, never to learn what
    to do.
- If something you need is not here, stop and say so in your report; don't fill the gap from memory or
  guesswork.
- The spec is the document chain in `docs/plan.md`. Where your item and its documents leave a question,
  look it up from the top of the chain down. A change starts in the highest document it touches
  ([changes.md](changes.md)).

## Your work

- You are given one backlog item from `docs/backlog.md` as "Do B-###". Read the item and every document
  it links before you start. If you continue an interrupted item, continue on its branch and open pull
  request.
- Work on your own branch, named `b-###-short-name`. Never commit to `main`.
- **Questions first.** Before any work, open a draft pull request with a short plan (what you will
  change and how you will check it) and your questions about the item, or "no questions". Start the
  branch with `git commit --allow-empty -m "chore: start B-###"`, since GitHub needs a commit to open
  one. With questions, end your turn and say in your last message that you wait for answers in the pull
  request; the coordinator answers there and tells you to go on. With no questions, go on at once.
- **Do only that item, and no more than it needs.** Its "Done when" is the bar. Tools for our own use get
  no options, modes or cases nobody needs yet.
- If the item is unclear, wrong, or conflicts with a document above it, stop and report; don't widen or
  reinterpret it.
- If your work shows that a document above your item is wrong, report it rather than change it, unless
  your item says so. Facts you find by experiment are the exception: record them where `docs/plan.md`
  says facts go, with the date and how you found them, and report them too if they contradict your item.
- A bug or gap your item doesn't cover goes in your pull request's "Not done and open questions", not
  into the fix: the coordinator makes it an item of its own.
- A pull request stays reviewable: about 800 changed lines at most, generated files, data and removed
  files aside. If the item needs more, stop and report; the coordinator splits it.
- **To stop and report:** push what you have, keep the pull request in draft (its checks may fail then),
  and say what is left and why in its "Not done and open questions" and in your last message. The
  coordinator decides what happens to the pull request.
- Once the pull request is open (the empty start commit is pushed to open it), run these before every
  push, and finish only with every one passing:
  - `python3 tools/process/check.py` (the process checks and the project's own);
  - `python3 tools/process/check_pr.py --body <description file> --title "<title>" --labels <review
    label>`;
  - `python3 tools/process/check_commits.py --title "<title>" --number <its number>`.
- Tick your item in the backlog (`- [x]`) in the same pull request. Don't edit `docs/now.md`: the
  coordinator does.
- Don't edit the template's files ([README.md](README.md#what-lives-where)). If the process is wrong,
  report it.

## Your pull request is your report

- Fill in every section of `.github/pull_request_template.md`, and name and label it as
  [pull-requests.md](pull-requests.md) says.
- A pull request that changes what a person sees gives in "How it was checked" what the UI review needs
  ("The UI review" below).

## If you fix a pull request

- Read the findings on the pull request: the comment of every review it had, and those the coordinator
  posts (the owner's remarks, a conflict with `main`).
- Fix every finding marked **fix**, on the pull request's branch, except:
  - those marked "outside the item", which you list under "Not done and open questions" instead;
  - those the coordinator closed in a comment.

  Leave the **drop** ones.
- Commit the fixes on top of the branch ("Git and GitHub" below), run the checks as in "Your work", and
  push.
- Answer with one comment: the new head commit, and for each "fix" finding what you changed and where,
  or why you couldn't.

## If you are the reviewer

Your brief names one of four reviews. The coordinator gives each pull request the ones it is for
([workflow.md](workflow.md#how-a-piece-of-work-goes), step 5):

| Brief | Review | For |
|---|---|---|
| "Review pull request #N" | the review | every pull request, but two that step 5 names |
| "Review pull request #N for harm" | the review for harm | code `docs/plan.md` names as risky |
| "Review pull request #N for architecture" | the architecture review | a change to the architecture or to a contract between parts (the design document, an interface, an API, a data or file format) |
| "Review pull request #N for UI" | the UI review | a change to what a person sees and uses (a GUI, web pages and the like) |

### Every review

- Look for what is wrong or missing, not for reasons to approve. Don't fix things yourself.
- Check the pull request against its item's "Done when" and the documents it links. A pull request with
  no item has its bar elsewhere: for "Setup", the steps of [setup.md](setup.md) and the owner's answers
  in its comments; for "Process change", what its description says it changes and
  [updates.md](updates.md#changing-the-process); for "Process update", the "Projects:" steps of the
  release's changelog entries; for a "Coordinator record", the owner's words it quotes and the documents
  above the ones it changes.
- Check that the evidence in the pull request is real: repeat it where you can.
- Post one comment on the pull request:
  1. A first line with the review's name and the head commit you reviewed.
  2. The sections your review asks for below, if any.
  3. The findings, each with the file and line, what is wrong and why it matters, and a mark with a
     one-line reason:
     - **fix:** wrong behaviour, a risk the project's rules name, a wrong or unsupported fact, a red or
       flaky check, a check loosened without the owner's OK (a test removed or skipped, a threshold
       eased), a review label
       weaker than [reports.md](reports.md#when-the-owner-looks) asks, documents that contradict each
       other, a gap the next item would trip on, or what your review below calls a "fix" finding;
     - **drop:** wording, taste, layout, or no effect on the result or the next steps.

     Nothing is put off for later. A problem the pull request didn't cause and its item doesn't cover is
     marked **fix** and "outside the item"; the fixing session lists it under "Not done and open
     questions", which settles it here.
  4. A last line: "Ready to merge as is: yes" when no "fix" finding is left, otherwise "no".
- A second round comes only if the first had "fix" findings, or, for a review for harm, if a fix changed
  the code `docs/plan.md` names as risky. Review only the change from the head you reviewed to the new
  head the fix comment names: `git diff <reviewed> <new>`, or, where a merge of `main` came in between,
  `git log -p --first-parent --remerge-diff <reviewed>..<new>`. Check whether each finding the
  coordinator didn't close is fixed, and whether the fix broke anything nearby.

### The review

In a pull request that changes the work itself (code, a design, a document of the chain), the comment has
a section with a verdict on three points, each with what you judged it on; falling short on one is a
"fix" finding:

- **Understood by a person** who hasn't read the rest of the project: the work explains itself (for
  code, "Code" below).
- **Fits the design:** each part sits where the design puts it (for code, in a folder the design names),
  and the boundaries between parts hold.
- **Easy to change:** each piece has one job, nothing is copied where the copies will drift apart, and
  tests, where there are any, read as a description of the behaviour.

### The review for harm

Until your findings are posted, read the pull request's description, diff and commits, not its
comments; in the second round, only your own earlier comment and the fix reply besides.

Hunt for concrete ways the change does harm: a secret that leaks or reaches the wrong place, damage to
the owner's machine, to infrastructure or to data, a state nothing can recover from, a race or an
interruption that leads there. Each finding says how it would happen. The three points are the review's,
not yours.

### The architecture review

- Judge whether each part sits where the design puts it and the boundaries hold.
- Then the contributor test: from the documentation alone, without reading the implementation, write a
  small implementation of the other side of the contract, outside the repository. Every place you had to
  guess is a "fix" finding.

### The UI review

A project with a user interface keeps a design-system document in its chain, which `docs/plan.md`
names, written before the first UI work; a UI pull request without one is a "fix" finding.

The pull request gives you:

- images rendered by a command it names (in CI or headless, never by starting an app on the owner's
  machine without the owner's consent), at 2x, in every theme the project uses, desktop and phone where
  both apply, before and after for a change;
- fixture data with the worst cases (empty, long text, extreme values, late, paused, a heavy day with
  many items);
- a table from each screen to the requirement and scenario step it serves.

Check these; each one that fails is a "fix" finding that names it:

1. Every scenario step has its control or label on a screen, and every state the requirements or the
   information design name is drawn, volume and connection loss included.
2. Every label, colour, word and number means what the requirements say on the fixture data, and a
   number is a fact from the repository or marked as an example.
3. The design system, point by point: its rules win over prototypes unless the plan says otherwise, and
   its tokens and components come before screens.
4. The strongest accent goes to what matters most for the user's decision; service elements stay quiet.
5. The layout holds under the worst content.
6. Accessibility is measured, not judged by eye: contrast, colours a colour-blind user tells apart,
   nothing said by colour alone, keyboard use.
7. The owner's remarks on looks are solved as design problems, not literally, with nothing nearby worse.

A fix that changes a shared token or component renders every screen again for the second round. The
owner is shown 6 to 10 chosen images.

## Writing

- Write for the next reader, briefly: say each thing once, and link to the document that says it rather
  than restating it.
- Everything in the repository is in English: docs, code, comments, commits, pull request titles and
  descriptions. Docs in plain words.
- Talk is in the owner's language (`owner_language` in `docs/process.json`; before it is set, the
  language the owner writes in): the chat, and every comment and review on pull requests, agents' to
  each other included. Text proposed for the repository is quoted in English.
- To the owner, anything named by an ID (a backlog item, a requirement, a test, a milestone) is said in
  plain words first, the ID after it in brackets: "the test of the cable length with you, about 20
  minutes (T-013)", not "the T-013 test".

## Code

Where the project has code. A reader must be able to tell what a piece of code is for and how to use
it without working through the rest.

- Every module opens with a comment in plain sentences: what it is for, which part of the design it
  is, what it holds and who uses it. A link to a document, here or in any comment, adds to this, never
  replaces it.
- Everything a module offers to others has a comment: what it does or stands for, and why; its inputs,
  where their names and types don't say it all; what it returns, empty results and failures included;
  the errors it raises. Something internal gets one when its purpose isn't plain from its name.
- A comment says what and why, not how the next line works, and changes with the code it describes.
- Behaviour the code adds or changes is covered by automated tests where the project has a way to run
  them; a change without them is a "fix" finding.
- Where the language has a linter for such comments, the project's checks run it
  ([config.md](config.md#checks)).
- The document the document chain names for the code's design lists its folders: those at the top of
  the repository and those of each part of the code, as deep as the design describes the parts. One
  line each: what it holds and, for a name that isn't plain, where the name comes from.
- A new folder goes into the list in the same pull request as the work that makes it, or an earlier one.
  The project's checks include one that fails on a folder missing from the list; the item that adds the
  first code adds it.

## Git and GitHub

- Commits, pushes and pull requests go out under the account the project chose for agents
  ([workflow.md](workflow.md#the-owners-ok-and-the-merge)). Call `git` and `gh` by name. Agents never
  approve a pull request: an approval is the owner's OK.
- **A pull request lands on `main` as one squash commit,** its subject the pull request's title, which
  follows the commit rules ([config.md](config.md#commits)). So the title says what the change is, and
  the commits on the branch are only its working history.
- A fix from a review or a check is a new commit on top. Take in what others pushed to the branch first
  (`git pull --no-rebase origin <branch>`). Never rewrite what is pushed (no rebase, no force push), so
  the head a reviewer reviewed stays readable. A conflict with `main` is resolved by merging
  `origin/main` into the branch.
- Open pull requests through the REST API (`gh api repos/{owner}/{repo}/pulls`), so nothing adds text
  to the description you wrote.
- Only the coordinator or the owner merges, as [workflow.md](workflow.md#the-owners-ok-and-the-merge)
  says.
