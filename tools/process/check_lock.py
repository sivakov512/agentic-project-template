#!/usr/bin/env python3
"""Checks a pull request against main's lock (docs/process/updates.md, "The lock"): if it changes the
template's files, its lock must name a newer version than main's.
Standard library only.

    python3 tools/process/check_lock.py --base-lock <main's .process-lock.json> "$GITHUB_EVENT_PATH"
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import owned  # noqa: E402


def changed_files(root, base_lock):
    """The template's files that differ from base_lock: changed, added or removed."""
    base = base_lock.get("files", {})
    present = owned.owned_files(root)
    changed = [name for name in present if base.get(name) != owned.digest(root / name)]
    return sorted(set(changed + [name for name in base if name not in present]))


def check(root, base_lock):
    changed = changed_files(root, base_lock)
    if not changed:
        return []
    errors = []
    lock = owned.read_lock(root) or {}
    try:
        newer = owned.version_tuple(lock.get("version", "0")) > owned.version_tuple(base_lock.get("version", "0"))
    except ValueError:
        newer = False
    if not newer:
        errors.append(f"it changes the template's files but its lock doesn't move past version "
                      f"{base_lock.get('version')}: " + ", ".join(changed))
    return errors


def main(argv):
    parser = argparse.ArgumentParser(description="Check a pull request against main's lock.")
    parser.add_argument("event", help="the GitHub event file")
    parser.add_argument("--base-lock", required=True, help="main's .process-lock.json")
    args = parser.parse_args(argv[1:])
    root = Path(__file__).resolve().parents[2]
    base_path = Path(args.base_lock)
    try:
        base_lock = json.loads(base_path.read_text(encoding="utf-8")) if base_path.exists() else None
        errors = check(root, base_lock) if base_lock else []
    except (OSError, ValueError, KeyError) as error:
        errors = [f"can't read the lock: {error}"]
    if base_lock is None and not errors:
        print("main has no lock yet: nothing to compare with")
    for error in errors:
        print(f"Template files: {error}")
    if errors:
        return 1
    print("Template files check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
