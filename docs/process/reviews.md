# Reviews

For reviewers. Your brief names one of these reviews; the coordinator decides which a pull request gets
([workflow.md](workflow.md#how-a-piece-of-work-goes), step 5).

| Brief | Review | For |
|---|---|---|
| "Review pull request #N" | the review | every pull request but those step 5 names |
| "Review pull request #N for harm" | the review for harm | code `docs/plan.md` names as risky |
| "Review pull request #N for architecture" | the architecture review | a change to the architecture or to a contract between parts (an interface, an API, a data or file format) |
| "Review pull request #N for UI" | the UI review | a change to what a person sees and uses |
| "Review milestone <n> before its gate on pull request #N, reading whole <modules>" | the gate review | the end of each milestone |

## Every review

- Look for what is wrong or missing, not for reasons to approve. Don't fix things yourself.
- Check the pull request against its item's "Done when" and the documents it links. A pull request with
  no item has its bar elsewhere: for "Setup", the steps of [setup.md](setup.md) and the owner's answers
  in its comments; for "Process change", its description and
  [updates.md](updates.md#changing-the-process); for "Process update", the "Projects:" steps of the
  release's changelog entries; for a "Coordinator record", the owner's words it quotes and the documents
  above it.
- Check that the evidence is real: repeat it where you can.
- Post one comment on the pull request:
  1. A first line with the review's name and the head commit you reviewed.
  2. The sections your review asks for below, if any.
  3. The findings, each with the file and line, what is wrong and why it matters, and a mark with a
     one-line reason:
     - **fix:** wrong behaviour, a risk the project's rules name, a wrong or unsupported fact, a red or
       flaky check, behaviour added or changed without tests where the project can run them, a check
       loosened without the owner's OK, a wrong review label
       ([owner.md](owner.md#the-review-label)), documents that contradict each other, a gap the next
       item would trip on, or what your review below calls a "fix" finding;
     - **drop:** wording, taste, layout, or no effect on the result or the next steps.

     A problem the pull request didn't cause and its item doesn't cover is marked **fix** and "outside
     the item".
  4. A last line: "Ready to merge as is: yes" when no "fix" finding is left, otherwise "no".

  The marks **fix** and **drop**, "outside the item" and the last line stay in English, whatever the
  comment's language.
- **A second round** reviews only the change from the head you reviewed to the new head the fix comment
  names: `git diff <reviewed> <new>`, or, where a merge of `main` came in between,
  `git log -p --first-parent --remerge-diff <reviewed>..<new>`. Check whether each open finding is fixed
  and whether the fix broke anything nearby. A merge of `main` that resolves a conflict is reviewed the
  same way, for how it resolved it.

## The review

In a pull request that changes the work itself (code, a design, a document of the chain), the comment has
a section with a verdict on three points, each with what you judged it on; falling short on one is a
"fix" finding:

- **Understood by a person** who hasn't read the rest of the project (for code,
  [rules.md](rules.md#code)).
- **Fits the design:** each part sits where the design puts it, and the boundaries between parts hold.
- **Easy to change:** each piece has one job, nothing is copied where the copies will drift apart, and
  tests read as a description of the behaviour.

## The review for harm

Until your findings are posted, read the pull request's description, diff and commits, not its comments;
in the second round, only your own earlier comment and the fix reply besides.

Hunt for concrete ways the change does harm: a secret that leaks or reaches the wrong place, damage to
the owner's machine, infrastructure or data, a state nothing can recover from, a race or an interruption
that leads there. Each finding says how it would happen.

## The architecture review

- Judge whether each part sits where the design puts it and the boundaries hold.
- Then the contributor test: from the documentation alone, without reading the implementation, write a
  small implementation of the other side of the contract, outside the repository. Every place you had to
  guess is a "fix" finding.

## The UI review

A project with a user interface keeps a design-system document in its chain, which `docs/plan.md` names;
a UI pull request without one is a "fix" finding.

The pull request gives you:

- images of the interface as the product's own code draws it, on the fixture data below: screenshots of
  the real window, menu or page, or the product's own views rendered offscreen, never a mock-up or a
  picture drawn again by hand. A command the pull request names makes them, in CI, headless, or on the
  owner's machine with the owner's consent; at 2x, in the themes and screen sizes the design-system
  document names, before and after for a change;
- fixture data with the worst cases (empty, long text, extreme values, many items);
- when it adds a screen or changes what a screen is for, a table from each such screen to the
  requirement and scenario step it serves.

Check these; each one that fails is a "fix" finding:

1. Every scenario step has its control or label on a screen, and every state the requirements name is
   drawn, connection loss included.
2. Every label, colour, word and number means what the requirements say, and a number is a fact from the
   repository or marked as an example.
3. The design system wins over prototypes, and its tokens and components come before screens.
4. The strongest accent goes to what matters most for the user's decision; service elements stay quiet.
5. The layout holds under the worst content.
6. Accessibility is measured, not judged by eye: contrast, colours a colour-blind user tells apart,
   nothing said by colour alone, keyboard use.
7. The owner's remarks on looks are solved as design problems, with nothing nearby made worse.

A fix that changes a shared token or component renders every screen again for the second round.

## The gate review

The coordinator starts it before each gate, on the pull request of the next milestone's plan
([coordinator.md](coordinator.md#before-a-gate)). From the repository alone:

1. Say where the work stands and what comes next, and compare it with `docs/now.md`: a difference is a
   "fix" finding.
2. Check that each point of the exit list ticked in the pull request's description holds, by its
   evidence.
3. Judge the next milestone's plan as the review judges a pull request, and look for gaps in what it
   builds on.
4. Read the modules the brief names (those the milestone built or changed) from the top, as someone new
   to them would, and judge the review's three points on each: one name for one thing, one way for one
   decision, one style. In a large module, read whole the parts the milestone touched. A finding too
   large to fix before the gate becomes a backlog item.

Post one comment in the format of "Every review", naming `main`'s head and the pull request's. The
coordinator answers with one comment naming the new heads of `main` and the pull request; the second
round checks those fixes.
