# docs/process.json

The settings the process reads from a project. The project owns this file; `docs/plan.md` says in
words what the IDs mean, this file says it for the checks. JSON so the checks need nothing beyond
Python's standard library.

```json
{
  "project": {
    "set_up": true,
    "owner_language": "English",
    "tracker": "Linear, project EXA",
    "releases": "release-please, versions vX.Y.Z, built and published on release",
    "agents_account": "own",
    "merged_by": "coordinator"
  },
  "commits": {"one_line": true, "no_co_authors": false, "conventional": true},
  "checks": ["npm test", "npm run lint"],
  "ids_ignore": ["docs/audit/*.md"],
  "ids": [
    {"kind": "scenario", "prefix": "S", "file": "docs/scenarios.md", "defined_by": "heading"},
    {"kind": "step", "prefix": "S", "parts": 2, "file": "docs/walkthroughs.md", "defined_by": "heading"},
    {"kind": "feature", "prefix": "F", "dash": true, "digits": 3, "file": "docs/features.md", "defined_by": "table"},
    {"kind": "fr", "prefix": "FR", "dash": true, "digits": 3, "file": "docs/requirements.md", "defined_by": "heading"}
  ],
  "coverage": [
    {"kind": "scenario", "children": "step"},
    {"kind": "step", "field": "Requirements", "refs": ["fr"]},
    {"kind": "fr", "field": "Source", "refs": ["step", "feature"], "or_match": "requirements\\.md#general-needs"},
    {"kind": "feature", "field": "Requirements", "refs": ["fr"], "or_starts": "out of scope"}
  ]
}
```

## project

- `set_up`: `false` in the template; setting up sets it to `true` ([setup.md](setup.md)). Agents read it
  on `main` to know their role.
- `owner_language`: the language of talk with the owner.
- `tracker`: the tracker that mirrors the project for the owner, and the project in it, in a few words;
  or `none`. `doctor.py` shows it at the start of every coordinator session
  ([coordinator.md](coordinator.md#the-tracker)).
- `releases`: how the project ships, in a few words; `not yet: <where it is decided>` for a project
  that will ship but hasn't chosen how; or `none`. The full description is in the Releases section of
  `docs/plan.md` ([releases](#releases)).
- `agents_account`: `own` (the agents have a GitHub account of their own) or `owner` (they work under
  the owner's); `merged_by`: `coordinator` or `owner`. What each means:
  [workflow.md](workflow.md#the-owners-ok-and-the-merge).

`owner_language`, `tracker`, `releases`, `agents_account` and `merged_by` must be set once `set_up` is
`true`, so these choices are always made and written down.

## commits

Every commit subject is at most 72 characters. Stricter rules the project may ask for:

- `one_line`: a commit message is its subject line only, with no body;
- `no_co_authors`: no `Co-authored-by` lines;
- `conventional`: every subject follows Conventional Commits, as release tools that read the history
  need: one of the types `feat`, `fix`, `perf`, `revert`, `refactor`, `chore`, `docs`, `style`, `test`,
  `build`, `ci`, in lower case, an optional lower-case scope, an optional `!` (`fix(parser): …`,
  `docs!: …`). A revert is written `revert: …`, not git's default `Revert "…"`.

All default to `false`. Rules beyond these go in the project's own check.

## releases

The process doesn't choose a release tool; it makes the project choose one and write it down. For a
project that ships, a good default is release-please: it opens release pull requests from the
Conventional Commits history (set `commits.conventional`), keeps the changelog and tags versions,
and the project's own workflows build and publish on the release. Run it with a GitHub App's token,
not the agents' or the owner's: its pull requests are then recognised as a bot's
([pull-requests.md](pull-requests.md#the-checks-ci-runs)), and the release it creates starts the
publishing workflows. Its configuration is the project's: it differs with what the project ships.

## checks

Commands `tools/process/check.py` runs after the process checks, from the repository root: the
project's own tests and linters, so an agent runs one command before pushing. CI runs them in the
project's own workflows (`.github/workflows/project-*.yml`), not in the process workflow, because they
need the project's toolchain.

## ids_ignore

File patterns (`fnmatch`, from the repository root) the ID check leaves alone: frozen documents where
text that looks like an ID means something else and must not be edited. Anywhere else, such text is
written as code (`` `S3` ``), which the check skips.

## ids

The project's kinds of ID. Backlog items (`B-###`) and decision records are built in.

| Key | Means | Default |
|---|---|---|
| `kind` | the name rules refer to, unique | required |
| `prefix` | capital letters before the number | required |
| `dash` | a dash between prefix and number (`FR-001`, not `C1`) | `false` |
| `parts` | how many dot-separated numbers (`S1` is 1, `S1.2` is 2) | `1` |
| `digits` | exact digits in each number; `0` for any | `0` |
| `file` | where the kind is defined | required |
| `defined_by` | `heading`: a heading that starts with the ID; `table`: the first cell of a table row | required |

Any text like an ID (capital letters, an optional dash, numbers with dots) whose prefix belongs to a
kind must fit one of the kinds with that prefix and be defined once; text with other prefixes is left
alone. A kind whose file doesn't exist yet (a document of a later stage) defines nothing, so references
to it fail and its coverage rules have nothing to check.

## coverage

Rules that every ID of a kind is covered. Each rule has `kind` and one of:

- `children`: another kind; every ID needs at least one child, an ID of that kind that starts with it
  and a dot (`S1` needs some `S1.n`).
- `field`: a label; the text after `Label:` in the ID's section (from its heading to the next heading),
  or the cell under that column for kinds defined by table, must name an ID of a kind in `refs`. Also
  accepted, if given: text matching the regular expression `or_match`, or text starting with
  `or_starts`. In a table whose first column is `ID`, a row without an ID is reported too.
