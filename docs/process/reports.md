# Reports to the owner

Whenever there is something for the owner (one or more pull requests ready to merge, or a gate), the
coordinator reports, in this order:

1. **Where we are:** the stage and the next step.
2. **Summary:** two or three lines on what was done and why.
3. **How it was checked.**
4. **Decisions the coordinator made itself,** one line each, so the owner can reverse any of them.
5. **Deviations from the plan, and risks,** if any.
6. **What is needed from the owner,** for each pull request one of:
   - **Review:** what to look at, a link, how many minutes;
   - **OK without reading:** why no reading is needed.
7. **The tracker:** one line on what changed there, if the project has one.

Settings the owner must change are given as a path of clicks with links (Settings → Branches → `main`
→ …), not as commands to run.

## Review or OK without reading

Review is needed for: what the product must do and what is in and out of it, the design the owner will
use, stack and architecture, the interfaces between parts (in whatever form they are written), any
decision that is hard to reverse, changes to the plan, to `CLAUDE.md` and to the process, anything
risky the project's rules name, and accepting what a stage, or an iteration within it, delivered.
`docs/plan.md` may name more.

OK without reading is enough for: documents written for machines other than interfaces, studies that only collect material
(what they find reaches the owner through the documents built on them), tests, code inside an agreed
design, code of our own tools, the project's checks and CI (they are the coordinator's: the report says
in one line what each change does, and what it loosens or tightens; when a change matters to the owner,
the coordinator asks for a review anyway and explains it in plain words), records of facts found by
experiment, `docs/now.md`, and the coordinator's records of the owner's own decisions, wherever they
land, the plan included: the owner said them. Anything the coordinator adds of its own in such a record
makes it a Review.

When in doubt, it is Review. The coordinator never moves a kind of work from Review to OK without
reading on its own; only the owner can, by a change to the plan.

## Batching

Pull requests that are OK without reading come to the owner in a batch when several are near, not one
at a time, unless one holds up the next piece of work. Questions to the owner come in a batch, each with
the coordinator's recommendation.
