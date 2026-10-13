#!/usr/bin/env python3
"""Offline sanity checks for metadata/lms (penguinctl only validates server-side).

Checks: JSON parses; required fields; ids/slugs unique; ids tenant-prefixed; lesson ids start
with their parent module's id; modules hold >= 2 lessons; lesson `type`; auth/pro entitlements
not mixed; every markdown image link resolves. Exit status 1 on any error.
"""
import glob, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "metadata", "lms")
ROOT = os.path.normpath(ROOT)
TENANTS = ("spring-", "tanzu-", "kube-")
TYPES = {"article", "video", "lab"}
errors = []


def err(path, msg):
    errors.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        err(path, f"invalid JSON ({e})")
        return None


ids, slugs = {}, {}


def register(path, d):
    for key, seen in (("id", ids), ("slug", slugs)):
        if not d.get(key):
            err(path, f"missing '{key}'")
        elif d[key] in seen:
            err(path, f"duplicate {key} '{d[key]}' (also {os.path.relpath(seen[d[key]], ROOT)})")
        else:
            seen[d[key]] = path
    if not d.get("title"):
        err(path, "missing 'title'")
    if d.get("id") and not d["id"].startswith(TENANTS):
        err(path, f"id '{d['id']}' must start with one of {TENANTS}")
    ent = d.get("entitlements", [])
    if "auth" in ent and "pro" in ent:
        err(path, "entitlements 'auth' and 'pro' are mutually exclusive")


course_path = os.path.join(ROOT, "course.template.json")
course = load(course_path)
if course:
    register(course_path, course)


def walk(directory, parent_id):
    """Check each module/lesson dir under `directory`; returns the number of lessons found."""
    lessons = 0
    for name in sorted(os.listdir(directory)):
        sub = os.path.join(directory, name)
        if not os.path.isdir(sub):
            continue
        mod, les = os.path.join(sub, "module.json"), os.path.join(sub, "lesson.json")
        if os.path.exists(mod):
            d = load(mod)
            if not d:
                continue
            register(mod, d)
            if parent_id and d.get("id") and not d["id"].startswith(parent_id):
                err(mod, f"module id '{d['id']}' must start with '{parent_id}'")
            n = walk(sub, d.get("id"))
            if n < 2:
                err(mod, f"module holds {n} lesson(s); modules need at least two")
            lessons += n
        elif os.path.exists(les):
            d = load(les)
            if not d:
                continue
            register(les, d)
            if d.get("type") not in TYPES:
                err(les, f"type must be one of {sorted(TYPES)}")
            if parent_id and d.get("id") and not d["id"].startswith(parent_id):
                err(les, f"lesson id '{d['id']}' must start with its parent id '{parent_id}'")
            if d.get("type") == "lab" and not d.get("settings", {}).get("educates"):
                err(les, "lab lesson without settings.educates")
            lessons += 1
    return lessons


if course:
    total = walk(ROOT, course.get("id"))
else:
    total = 0

for md in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
    with open(md) as f:
        for link in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", f.read()):
            RAW = "https://raw.githubusercontent.com/mrporcles/course-test/main/"
            if link.startswith(RAW):
                local = os.path.join(ROOT, "..", "..", link[len(RAW):])
            elif link.startswith(("http://", "https://")):
                continue
            else:
                local = os.path.join(os.path.dirname(md), link)
            if not os.path.exists(local):
                err(md, f"broken image link '{link}'")

if errors:
    print("\n".join(errors))
    print(f"\n{len(errors)} problem(s) found")
    sys.exit(1)
print(f"metadata OK: {total} lessons, {len(ids)} ids, no problems")
