"""The template's files and their lock. Standard library only.

The lock, .process-lock.json, holds the template's name, the process version and a hash of every file
that belongs to the template (docs/process/updates.md, "The lock").
"""

import fnmatch
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = ".process-lock.json"
CHANGELOG = "docs/process/CHANGELOG.md"

# What belongs to the template: whole folders, and single files or file name patterns.
OWNED_DIRS = ["docs/process", "tools/process"]
OWNED_FILES = [".github/pull_request_template.md"]
OWNED_PATTERNS = [(".github/workflows", "process-*.yml")]
# Never the template's files; outside a git repository (the checks' own tests) these are also what is
# left out instead of what git ignores.
SKIP = {".git", "__pycache__", ".DS_Store", "node_modules", ".venv"}

VERSION_HEADING = re.compile(r"^## (\d+\.\d+\.\d+)\b", re.MULTILINE)


def repo_files(root):
    """The repository's files, tracked or not but not ignored by git, as POSIX paths relative to root."""
    done = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=root,
                          capture_output=True, text=True)
    if done.returncode == 0 and (root / ".git").exists():
        return sorted(name for name in done.stdout.split("\0") if name and (root / name).is_file())
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*")
                  if path.is_file() and not SKIP.intersection(path.relative_to(root).parts))


def is_owned(name):
    folder, _, base = name.rpartition("/")
    return (any(name.startswith(prefix + "/") for prefix in OWNED_DIRS) or name in OWNED_FILES
            or any(folder == where and fnmatch.fnmatch(base, pattern) for where, pattern in OWNED_PATTERNS))


def owned_files(root):
    """The template's files present under root, as sorted POSIX paths relative to it."""
    return [name for name in repo_files(root) if is_owned(name) and not SKIP.intersection(name.split("/"))]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changelog_version(root):
    """The newest version in the changelog: the version of the process in this tree."""
    match = VERSION_HEADING.search((root / CHANGELOG).read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{CHANGELOG} has no \"## X.Y.Z\" heading")
    return match.group(1)


def version_tuple(version):
    """(X, Y, Z) of "X.Y.Z" or "vX.Y.Z"; ValueError otherwise."""
    if not re.fullmatch(r"v?\d+\.\d+\.\d+", version):
        raise ValueError(f"not a version X.Y.Z: {version!r}")
    return tuple(int(part) for part in version.lstrip("v").split("."))


def read_lock(root):
    """The lock under root, or None if there is none; ValueError if it is not a valid lock."""
    path = root / LOCK
    if not path.exists():
        return None
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise ValueError(f"{LOCK}: not valid JSON: {error}")
    if not isinstance(lock, dict) or not isinstance(lock.get("files"), dict):
        raise ValueError(f"{LOCK}: not a lock (an object with template, version and files)")
    return lock


def make_lock(root, template):
    return {
        "template": template,
        "version": changelog_version(root),
        "files": {name: digest(root / name) for name in owned_files(root)},
    }


def write_lock(root, template):
    lock = make_lock(root, template)
    (root / LOCK).write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    return lock


def check(root):
    """Problems with the template's files against the lock."""
    try:
        lock = read_lock(root)
    except ValueError as error:
        return [str(error)]
    if lock is None:
        return [f"{LOCK}: missing"]
    errors = []
    locked = lock.get("files", {})
    present = owned_files(root)
    for name in present:
        if name not in locked:
            errors.append(f"{name}: belongs to the template but is not in {LOCK}")
        elif digest(root / name) != locked[name]:
            errors.append(f"{name}: differs from the template's version {lock.get('version')}")
    for name in sorted(set(locked) - set(present)):
        errors.append(f"{name}: in {LOCK} but missing")
    try:
        version = changelog_version(root)
    except (OSError, ValueError) as error:
        errors.append(str(error))
    else:
        if version != lock.get("version"):
            errors.append(f"{LOCK}: says version {lock.get('version')}, {CHANGELOG} says {version}")
    if errors:
        errors.append("The template's files can't be edited in a project: changes go to the template "
                      "(docs/process/updates.md). In the template, run python3 tools/process/lock.py")
    return errors
