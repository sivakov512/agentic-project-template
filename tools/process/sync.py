#!/usr/bin/env python3
"""Brings the template's files from a checkout of the template into a project: copies them, removes the
ones the new version no longer has, and copies the lock. Prints the changelog entries newer than the
project's version. Standard library only.

The update workflow runs the new version's copy of this script (docs/process/updates.md):
    python3 <template>/tools/process/sync.py <template> <project>
"""

import shutil
import sys
from pathlib import Path

import owned


def changelog_since(template, version):
    """The changelog entries of the template newer than version, as Markdown."""
    text = (template / owned.CHANGELOG).read_text(encoding="utf-8")
    entries = []
    current = None
    for line in text.splitlines():
        match = owned.VERSION_HEADING.match(line)
        if match:
            current = [] if owned.version_tuple(match.group(1)) > owned.version_tuple(version) else None
            if current is not None:
                entries.append(current)
        if current is not None:
            current.append(line)
    return "\n".join("\n".join(entry).strip() for entry in entries)


def sync(template, project):
    """Returns (old version, new version)."""
    new_lock = owned.read_lock(template)
    if new_lock is None:
        raise ValueError(f"{template}: no {owned.LOCK}")
    old_lock = owned.read_lock(project) or {"version": "0.0.0"}
    for lock in (new_lock, old_lock):
        owned.version_tuple(str(lock.get("version", "")))  # ValueError unless X.Y.Z
    for name in owned.owned_files(project):
        if name not in new_lock["files"]:
            (project / name).unlink()
    for name in new_lock["files"]:
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template / name, target)
    shutil.copy2(template / owned.LOCK, project / owned.LOCK)
    return old_lock["version"], new_lock["version"]


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    template, project = Path(argv[1]).resolve(), Path(argv[2]).resolve()
    try:
        old, new = sync(template, project)
        changelog = changelog_since(template, old)
    except (OSError, ValueError) as error:
        print(f"sync.py: {error}")
        return 1
    print(f"Process {old} -> {new}")
    print(changelog)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
