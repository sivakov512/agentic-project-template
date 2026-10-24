#!/usr/bin/env python3
"""Checks the documents in this repository. Standard library only.

Fails on:
- a relative link in a *.md file that points to a missing file, or to a heading that isn't there;
- a backlog item that is not in the agreed form, or lacks "Depends on" or a filled-in "Done when";
- an ID (B-### or a kind from docs/process.json) in the wrong form, defined twice, or referred to but
  defined nowhere;
- a decision record whose number is taken twice, or that docs/decisions/README.md doesn't list;
- a gap in coverage, by the rules in docs/process.json (docs/process/config.md).

Run from anywhere: python3 tools/process/check_docs.py
"""

import fnmatch
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

import owned  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONFIG = "docs/process.json"
# The template's own text can't know a project's kinds of ID, so IDs in it are not checked.
NO_ID_CHECK = ("docs/process/",)
NOT_AN_ID = " (if it is not an ID, write it as code: `like this`)"

# [text](target) and [text](target "title"); images too.
LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
ANY_HEADING = re.compile(r"^#{1,6}\s")
HEADING_START = re.compile(r"^#{1,6}\s+")
TABLE_ROW = re.compile(r"^\s*\|")
TABLE_RULE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")

BACKLOG_ITEM = re.compile(r"^- \[( |x)\] \*\*(B-\d{3})\*\* \S")
# Anything that looks like an ID: capital letters, an optional dash, numbers with dots.
TOKEN = re.compile(r"(?<!\w)([A-Z]+)(-?)(\d+(?:\.\d+)*)(?!\w)")
BACKLOG_KIND = {"kind": "backlog", "prefix": "B", "dash": True, "parts": 1, "digits": 3,
                "file": "docs/backlog.md", "defined_by": "backlog"}



def load_config(root):
    path = root / CONFIG
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def kinds(config):
    """Every kind of ID: the built-in backlog items and the project's own, with defaults filled in."""
    found = [BACKLOG_KIND]
    for kind in config.get("ids", []):
        found.append({"dash": False, "parts": 1, "digits": 0, **kind})
    return found


def markdown_files(root):
    for name in owned.repo_files(root):
        if name.endswith(".md"):
            yield root / name


def prose_lines(path, keep_code=False):
    """Yields (line number, text) outside code blocks; inline code is removed unless keep_code."""
    in_fence = False
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"{path}: not UTF-8 text")
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, line if keep_code else INLINE_CODE.sub("", line)


def slug(heading):
    """The anchor GitHub gives a heading."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # links keep their text
    text = re.sub(r"[`*~]", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path):
    found = set()
    for _, line in prose_lines(path, keep_code=True):  # GitHub keeps inline code in anchors
        match = HEADING.match(line)
        if match:
            base = slug(match.group(1))
            name, n = base, 0
            while name in found:
                n += 1
                name = f"{base}-{n}"
            found.add(name)
    return found


def check_links(root):
    errors = []
    for path in markdown_files(root):
        for number, line in prose_lines(path):
            for match in LINK.finditer(line):
                target = match.group(1)
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                    continue  # external link or mailto:
                file_part, _, anchor = target.partition("#")
                file_part = unquote(file_part.split("?", 1)[0])
                if not file_part:
                    resolved = path
                elif file_part.startswith("/"):
                    resolved = root / file_part.lstrip("/")
                else:
                    resolved = path.parent / file_part
                where = f"{path.relative_to(root)}:{number}"
                if not resolved.exists():
                    errors.append(f"{where}: link to a missing file: {target}")
                elif anchor and resolved.suffix == ".md" and unquote(anchor) not in anchors(resolved):
                    errors.append(f"{where}: link to a missing heading: {target}")
    return errors


def backlog_items(root):
    """Yields (line number, ID, title line, the item's further lines) for each backlog item."""
    lines = (root / "docs" / "backlog.md").read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        match = BACKLOG_ITEM.match(line)
        if not match:
            continue
        body = []
        for following in lines[index + 1:]:
            if following.strip() and not following.startswith((" ", "\t")):
                break
            body.append(following)
        yield index + 1, match.group(2), line, "\n".join(body)


def check_backlog(root):
    path = root / "docs" / "backlog.md"
    if not path.exists():
        return ["docs/backlog.md: missing"]
    errors = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if re.match(r"^\s*[-*] \[.\]", line) and not BACKLOG_ITEM.match(line):
            errors.append(f"docs/backlog.md:{number}: an item must be a top-level \"- [ ] **B-###** Title\"")
    for number, item_id, _, body in backlog_items(root):
        if "depends on" not in body.lower():
            errors.append(f"docs/backlog.md:{number}: {item_id} has no \"Depends on\"")
        done_when = re.search(r"done when:?(.*)", body, re.IGNORECASE | re.DOTALL)
        if not done_when:
            errors.append(f"docs/backlog.md:{number}: {item_id} has no \"Done when\"")
        elif len(re.sub(r"[\s\-*:;.]", "", done_when.group(1))) < 10:
            errors.append(f"docs/backlog.md:{number}: {item_id} has an empty \"Done when\"")
    return errors


def fits(kind, match):
    """Whether a TOKEN match has the shape of the kind."""
    prefix, dash, number = match.group(1), match.group(2), match.group(3)
    parts = number.split(".")
    return (prefix == kind["prefix"] and bool(dash) == kind["dash"] and len(parts) == kind["parts"]
            and (not kind["digits"] or all(len(part) == kind["digits"] for part in parts)))


def kind_of(all_kinds, match):
    """The kind a TOKEN match is, None if it fits none, or False if its prefix is no kind's at all."""
    with_prefix = [kind for kind in all_kinds if kind["prefix"] == match.group(1)]
    if not with_prefix:
        return False
    return next((kind for kind in with_prefix if fits(kind, match)), None)


def defining_token(kind, line):
    """The ID a line defines for the kind, or None."""
    if kind["defined_by"] == "backlog":
        match = BACKLOG_ITEM.match(line)
        return match.group(2) if match else None
    if kind["defined_by"] == "heading":
        start = HEADING_START.match(line)
        if not start:
            return None
        match = TOKEN.match(line, start.end())
    elif kind["defined_by"] == "table":
        match = re.match(r"^\|\s*", line)
        match = TOKEN.match(line, match.end()) if match else None
        if match and not re.match(r"\s*\|", line[match.end():]):
            return None
    else:
        return None
    return match.group(0) if match and fits(kind, match) else None


def definitions(root, all_kinds):
    """Maps each defined ID to (kind name, where), and lists IDs defined twice as errors."""
    defined, errors = {}, []
    for kind in all_kinds:
        path = root / kind["file"]
        if not path.exists():
            continue
        for number, line in prose_lines(path):
            item_id = defining_token(kind, line)
            if not item_id:
                continue
            where = f"{kind['file']}:{number}"
            if item_id in defined:
                errors.append(f"{where}: {item_id} is already defined at {defined[item_id][1]}")
            else:
                defined[item_id] = (kind["kind"], where)
    return defined, errors


def check_ids(root, config):
    all_kinds = kinds(config)
    defined, errors = definitions(root, all_kinds)
    ignored = config.get("ids_ignore", [])
    for path in markdown_files(root):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(NO_ID_CHECK) or any(fnmatch.fnmatch(relative, pattern) for pattern in ignored):
            continue
        for number, line in prose_lines(path):
            for match in TOKEN.finditer(line):
                kind = kind_of(all_kinds, match)
                if kind is False:
                    continue
                where = f"{relative}:{number}"
                if kind is None:
                    errors.append(f"{where}: {match.group(0)} is not a valid ID{NOT_AN_ID}")
                elif match.group(0) not in defined:
                    errors.append(f"{where}: {match.group(0)} is defined nowhere{NOT_AN_ID}")
    return errors


def check_decisions(root):
    folder = root / "docs" / "decisions"
    if not folder.exists():
        return []
    errors = []
    index = (folder / "README.md").read_text(encoding="utf-8") if (folder / "README.md").exists() else ""
    numbers = {}
    for path in sorted(folder.glob("*.md")):
        if path.name == "README.md":
            continue
        match = re.match(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$", path.name)
        if not match:
            errors.append(f"docs/decisions/{path.name}: name must be NNNN-kebab-case.md")
            continue
        if match.group(1) in numbers:
            errors.append(f"docs/decisions/{path.name}: number {match.group(1)} is taken by {numbers[match.group(1)]}")
        numbers[match.group(1)] = path.name
        if f"({path.name})" not in index:
            errors.append(f"docs/decisions/{path.name}: not listed in docs/decisions/README.md")
    return errors


def heading_sections(path, kind):
    """Yields (line number, ID, lines up to the next heading) for each heading that defines the kind."""
    current = None
    for number, line in prose_lines(path):
        if ANY_HEADING.match(line):
            if current:
                yield current
            item_id = defining_token(kind, line)
            current = (number, item_id, []) if item_id else None
        elif current:
            current[2].append(line)
    if current:
        yield current


def table_rows(path, kind):
    """Yields (line number, ID, {column: cell}) for each table row that defines the kind, and with ID None
    for each row of a table whose first column is "ID" that defines nothing."""
    header = None
    for number, line in prose_lines(path):
        if not TABLE_ROW.match(line):
            header = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
        elif not TABLE_RULE.match(line):
            item_id = defining_token(kind, line.strip())
            if item_id or header[0] == "ID":
                yield number, item_id, dict(zip(header, cells))


def field(lines, label):
    """The text after "label:" (bold or not, a list item or not) with its continuation lines."""
    text = None
    for line in lines:
        if text is None:
            match = re.match(rf"^\s*(?:- )?(?:\*\*)?{re.escape(label)}:(?:\*\*)?(.*)", line)
            if match:
                text = match.group(1)
        elif line.strip() and not line.lstrip().startswith("- "):
            text += " " + line
        else:
            break
    return text or ""


def covered_items(root, kind):
    """Yields (line number, ID, a function giving a field's text) for every ID of the kind."""
    path = root / kind["file"]
    if not path.exists():
        return
    if kind["defined_by"] == "table":
        for number, item_id, row in table_rows(path, kind):
            yield number, item_id, lambda label, row=row: row.get(label, "")
    else:
        for number, item_id, lines in heading_sections(path, kind):
            yield number, item_id, lambda label, lines=lines: field(lines, label)


def check_coverage(root, config):
    all_kinds = kinds(config)
    by_name = {kind["kind"]: kind for kind in all_kinds}
    defined, _ = definitions(root, all_kinds)
    errors = []
    for rule in config.get("coverage", []):
        kind = by_name[rule["kind"]]
        if "children" in rule:
            children = [item_id for item_id, (name, _) in defined.items() if name == rule["children"]]
            for number, item_id, _ in covered_items(root, kind):
                if item_id is None:
                    errors.append(f"{kind['file']}:{number}: a row has no ID")
                elif not any(child.startswith(item_id + ".") for child in children):
                    errors.append(f"{kind['file']}:{number}: {item_id} has no {rule['children']}")
            continue
        refs = [by_name[name] for name in rule.get("refs", []) if name in by_name]
        for number, item_id, get in covered_items(root, kind):
            if item_id is None:
                errors.append(f"{kind['file']}:{number}: a row has no ID")
                continue
            text = get(rule["field"])
            if any(kind_of(refs, match) for match in TOKEN.finditer(text)):
                continue
            if rule.get("or_match") and re.search(rule["or_match"], text):
                continue
            if rule.get("or_starts") and text.strip().lower().startswith(rule["or_starts"].lower()):
                continue
            errors.append(f"{kind['file']}:{number}: {item_id} names no {' or '.join(rule.get('refs', []))}"
                          f" under \"{rule['field']}\"")
    return errors


def is_int(value, least):
    return isinstance(value, int) and not isinstance(value, bool) and value >= least


def project_errors(config):
    project = config.get("project", {})
    if not isinstance(project, dict):
        return [f"{CONFIG}: project must be an object"]
    errors = []
    for key, kind in (("set_up", bool), ("owner_language", str), ("tracker", str), ("agents_account", str),
                      ("merged_by", str)):
        if key in project and not isinstance(project[key], kind):
            errors.append(f"{CONFIG}: project.{key} must be a {kind.__name__}")
    for key, allowed in (("agents_account", ("own", "owner")), ("merged_by", ("coordinator", "owner"))):
        if project.get(key) and project[key] not in allowed:
            errors.append(f"{CONFIG}: project.{key} must be " + " or ".join(allowed))
    if project.get("set_up") is True:
        for key, what in (("owner_language", "the owner's language"),
                          ("tracker", "the tracker and the project in it, or \"none\""),
                          ("agents_account", "own or owner"), ("merged_by", "coordinator or owner")):
            if not str(project.get(key, "")).strip():
                errors.append(f"{CONFIG}: project.{key} must be set once the project is set up: {what}")
    for key in ("checks", "ids_ignore"):
        value = config.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(f"{CONFIG}: {key} must be a list of strings")
    commits = config.get("commits", {})
    if not isinstance(commits, dict) or not all(isinstance(value, bool) for value in commits.values()):
        errors.append(f"{CONFIG}: commits must be an object of true or false settings")
    elif set(commits) - {"one_line", "no_co_authors"}:
        errors.append(f"{CONFIG}: commits knows only one_line and no_co_authors")
    return errors


def kind_errors(index, kind):
    where = f"{CONFIG}: ids[{index}]"
    if not isinstance(kind, dict):
        return [f"{where} must be an object"]
    missing = [key for key in ("kind", "prefix", "file", "defined_by") if key not in kind]
    if missing:
        return [f"{where} lacks " + ", ".join(missing)]
    errors = []
    if not all(isinstance(kind[key], str) for key in ("kind", "file")):
        errors.append(f"{where}: kind and file must be strings")
    if kind["defined_by"] not in ("heading", "table"):
        errors.append(f"{where}: defined_by must be heading or table")
    if not isinstance(kind["prefix"], str) or not re.fullmatch(r"[A-Z]+", kind["prefix"]):
        errors.append(f"{where}: prefix must be capital letters")
    if not isinstance(kind.get("dash", False), bool):
        errors.append(f"{where}: dash must be true or false")
    if not is_int(kind.get("parts", 1), 1):
        errors.append(f"{where}: parts must be a whole number from 1")
    if not is_int(kind.get("digits", 0), 0):
        errors.append(f"{where}: digits must be a whole number from 0")
    return errors


def rule_errors(index, rule, names):
    where = f"{CONFIG}: coverage[{index}]"
    if not isinstance(rule, dict):
        return [f"{where} must be an object"]
    errors = []
    if "kind" not in rule:
        errors.append(f"{where} lacks kind")
    if ("children" in rule) == ("field" in rule):
        errors.append(f"{where} needs either children or field")
    refs = rule.get("refs", [])
    if not isinstance(refs, list):
        errors.append(f"{where}: refs must be a list of kinds")
        refs = []
    if "field" in rule and not refs:
        errors.append(f"{where}: a field rule needs refs")
    for name in [rule.get("kind"), rule.get("children")] + refs:
        if name is not None and (not isinstance(name, str) or name not in names):
            errors.append(f"{where} names an unknown kind \"{name}\"")
    for key in ("field", "or_match", "or_starts"):
        if key in rule and not isinstance(rule[key], str):
            errors.append(f"{where}: {key} must be a string")
    if isinstance(rule.get("or_match"), str):
        try:
            re.compile(rule["or_match"])
        except re.error as error:
            errors.append(f"{where}: or_match is not a valid regular expression: {error}")
    return errors


def config_errors(config):
    """Problems with docs/process.json itself (docs/process/config.md)."""
    if not isinstance(config, dict):
        return [f"{CONFIG}: must be an object"]
    ids, coverage = config.get("ids", []), config.get("coverage", [])
    if not isinstance(ids, list) or not isinstance(coverage, list):
        return [f"{CONFIG}: ids and coverage must be lists"]
    errors = project_errors(config)
    names = {"backlog"}
    for index, kind in enumerate(ids):
        found = kind_errors(index, kind)
        if not found and kind["kind"] in names:
            found = [f"{CONFIG}: ids[{index}]: the kind \"{kind['kind']}\" is named twice"]
        errors += found
        if not found:
            names.add(kind["kind"])
    for index, rule in enumerate(coverage):
        errors += rule_errors(index, rule, names)
    return errors


def check(root):
    try:
        config = load_config(root)
    except ValueError as error:
        return [f"{CONFIG}: not valid JSON: {error}"]
    errors = config_errors(config)
    if errors:
        return errors
    try:
        return (check_links(root) + check_backlog(root) + check_ids(root, config) + check_decisions(root)
                + check_coverage(root, config))
    except (ValueError, OSError) as error:
        return [f"can't read the documents: {error}"]


def main():
    errors = check(ROOT)
    for error in errors:
        print(error)
    if errors:
        print(f"{len(errors)} problem(s) found")
        return 1
    print("Docs check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
