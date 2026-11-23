#!/usr/bin/env python3
"""
check_prototype.py - the Week 06 checker. DO NOT EDIT: the grader runs its own copy over your files.

    python tests/check_prototype.py          # from inside week-06/
    python tests/check_prototype.py --json   # machine-readable, for the grading pipeline

What it checks (27 checks):

    P1-P3    your FINAL prototype in prototype/: exported, clean, and inside the scope
             (no backend, no network calls, no storage, no login, no analytics)
    O1-O2    the first version (v1) is kept in original/, and the final is not identical to it
    E1-E4    the screenshots in evidence/: v1, every issue, every final case, a narrow-width view
    T1-T9    lab-report.md section 4: the final result of each of the nine cases matches the
             expected result
    L1-L9    lab-report.md has its sections filled in

It never runs your prototype. It reads files. The screenshots and the results you report are
YOUR evidence; the grader opens them. A clean run is the floor, not the grade.

Verdicts:
    PASS   the check found what it was looking for
    FAIL   the content is there but wrong, or not enough of it
    ERROR  it could not check: a file, a folder or a section is missing

Exit codes: 0 = no FAIL and no ERROR - 1 = at least one FAIL or ERROR - 3 = wrong directory.
Standard library only.
"""

import argparse
import hashlib
import json
import os
import re
import struct
import sys

PROTOTYPE = "prototype"
ORIGINAL = "original"
EVIDENCE = "evidence"
REPORT = "lab-report.md"

MAX_EXPORT_MB = 5
MIN_IMAGE_BYTES = 3000
WORDS_MIN, WORDS_MAX = 120, 180
EXPLAIN_MIN = 60

SOURCE_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".html", ".css", ".json")
CODE_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".html")
IGNORED_FILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", ".gitkeep", ".DS_Store")
IGNORED_DIRS = (".git", ".bolt", ".vscode", ".idea", "__pycache__")

# The nine cases. Base for every case: now 09:00 (540), room not blocked, the room's only
# booking 10:00-11:00 (600-660). README section 6.
CASES = [
    ("T1", "Touching", "Available"),
    ("T2", "Overlap", "Unavailable"),
    ("T3", "Blocked", "Unavailable"),
    ("T4", "Exactly 2 hours", "Available"),
    ("T5", "Over 2 hours", "Unavailable"),
    ("T6", "Starts now", "Unavailable"),
    ("T7", "Reversed times", "Unavailable"),
    ("T8", "Same check twice", "Available"),
    ("T9", "Narrow screen", "Available"),
]
VERDICTS = {"available": "Available", "unavailable": "Unavailable",
            "not testable": "Not testable", "not-testable": "Not testable", "n/t": "Not testable"}

# Scope: the deck says one page, fictional data, no login, no backend, no database, no external
# API, no analytics, and the check must not save anything (AC5). Each pattern is evidence of one
# of those, found by reading the source - never a judgement of the code.
SCOPE = [
    ("network call", r"\bfetch\s*\(|\baxios\b|XMLHttpRequest|new\s+WebSocket|\bEventSource\b"),
    ("browser storage", r"\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b"),
    ("backend or database", r"supabase|firebase|@prisma|\bmongodb\b|\bmongoose\b|\bexpress\s*\("),
    ("login or account", r"\bsignIn\w*\s*\(|\bsign[ -]?in\b|\blog[ -]?in\b|\bpassword\b|\bauth0\b"),
    ("analytics", r"\bgtag\s*\(|google-analytics|\bmixpanel\b|\bposthog\b|\bsegment\.io\b"),
]

LAB_TITLES = {
    "L1": "report 1: tool, model and project link",
    "L2": "report 2: two predictions and the initial prompt as sent",
    "L3": "report 3: what v1 consists of and what works",
    "L4": "report 4: the v1 result of all nine cases",
    "L5": "report 5: issue log, two issues or more",
    "L6": "report 6: the cleanup prompts, each suggestion judged",
    "L7": "report 7: change log of 2-4 changes",
    "L8": "report 8: one component explained, in %d words or more" % EXPLAIN_MIN,
    "L9": "report 10: conclusion of %d-%d words" % (WORDS_MIN, WORDS_MAX),
}

# Fixed sentences from the three prompts on the practice deck (slides 15, 19, 20). Each must be
# present, unchanged, in the prompt you pasted - that is how the checker knows the prompt was used.
INITIAL_PROMPT = ("Build a small responsive Smart Campus Room Availability Checker.",
                  "Do not add authentication, backend services, analytics, or unrelated features.")
FIX_PROMPT = ("Make the smallest change that fixes this behavior.",
              "Preserve the other acceptance criteria.")
CLEANUP_PROMPT = ("Suggest one small cleanup.",
                  "Do not add features or redesign the whole application.")
BRACKETS = re.compile(r"\[(paste AC1[^\]]*|steps|observed result|expected result|component/area)\]|\bAC#", re.I)


# --------------------------------------------------------------------------- small helpers


class Results:
    def __init__(self):
        self.rows = []

    def add(self, cid, title, verdict, message):
        self.rows.append({"id": cid, "title": title, "verdict": verdict, "message": message})

    def counts(self):
        return {v: sum(1 for r in self.rows if r["verdict"] == v) for v in ("PASS", "FAIL", "ERROR")}


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def walk_files(root):
    for here, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and d != "node_modules")
        for name in sorted(files):
            if name in IGNORED_FILES:
                continue
            yield os.path.join(here, name)


def project_root(folder):
    """The exported project: folder itself, or the one sub-folder Bolt's zip unpacks into."""
    if not os.path.isdir(folder):
        return None
    candidates = [folder] + sorted(os.path.join(folder, d) for d in os.listdir(folder)
                                   if os.path.isdir(os.path.join(folder, d)) and d not in IGNORED_DIRS)
    for c in candidates:
        if os.path.isfile(os.path.join(c, "package.json")) or os.path.isfile(os.path.join(c, "index.html")):
            return c
    return None


def code_files(root):
    return [p for p in walk_files(root) if p.lower().endswith(CODE_EXT)]


def fingerprint(root):
    """Hash of every source file, by path relative to the project root."""
    out = {}
    for p in walk_files(root):
        if p.lower().endswith(SOURCE_EXT):
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            data = open(p, "rb").read().replace(b"\r\n", b"\n").strip()
            out[rel] = hashlib.sha1(data).hexdigest()
    return out


def scope_hits(root):
    hits = []
    for p in walk_files(root):
        low = p.lower()
        if not (low.endswith(CODE_EXT) or os.path.basename(low) == "package.json"):
            continue
        text = read(p) or ""
        for number, line in enumerate(text.splitlines(), 1):
            for label, pattern in SCOPE:
                if re.search(pattern, line, re.I):
                    hits.append({"what": label,
                                 "where": "%s:%d" % (os.path.relpath(p, ".").replace(os.sep, "/"), number)})
    return hits


def image_info(path):
    """(width, height) for a real PNG or JPEG, else None."""
    try:
        data = open(path, "rb").read()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) > 24:
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return (w, h)
            i += 2 + length
    return None


def find_image(stem):
    """evidence/<stem>.png|.jpg|.jpeg, any case."""
    if not os.path.isdir(EVIDENCE):
        return None
    for name in os.listdir(EVIDENCE):
        base, ext = os.path.splitext(name)
        if base.lower() == stem.lower() and ext.lower() in (".png", ".jpg", ".jpeg"):
            return os.path.join(EVIDENCE, name)
    return None


def image_problem(path):
    if path is None:
        return "missing"
    if os.path.getsize(path) < MIN_IMAGE_BYTES:
        return "%s is too small to be a screenshot" % path.replace(os.sep, "/")
    if image_info(path) is None:
        return "%s is not a real PNG or JPEG" % path.replace(os.sep, "/")
    return None


def file_hash(path):
    return hashlib.sha1(open(path, "rb").read()).hexdigest()


# --------------------------------------------------------------------------- lab-report.md parsing

PLACEHOLDER = re.compile(r"\(paste here\)|\(write here[^)]*\)|^<.*>$|yes / no|accept / reject|"
                         r"Available / Unavailable / Not testable|High / Medium / Low|Fix / Reject / Defer", re.I)


def sections(text):
    """{'1': body, '9.2': body, ...} - split on the numbered '## N.' and '### N.M' headings."""
    out, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^#{2,3}\s+(\d+(?:\.\d+)?)[.\s]", line)
        if m:
            current = m.group(1)
            out[current] = []
            top = current.split(".")[0]
            if top != current:
                out.setdefault(top, [])
        elif current is not None:
            out[current].append(line)
            top = current.split(".")[0]
            if top != current:
                out[top].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def table_rows(body):
    rows, lines = [], [l.strip() for l in body.splitlines()]
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c) and any(cells):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if nxt.startswith("|") and re.match(r"^\|[\s:|-]+\|?$", nxt):
            continue
        rows.append(cells)
    return rows


def useful(cell):
    cell = re.sub(r"<!--.*?-->", "", cell).strip()
    return bool(cell) and not PLACEHOLDER.search(cell)


def filled(cells, need):
    return sum(1 for c in cells[1:] if useful(c)) >= need


def blocks(body):
    return re.findall(r"```[^\n]*\n(.*?)```", body, re.S)


def real_blocks(body, min_lines=2):
    return [b for b in blocks(body)
            if len([l for l in b.splitlines() if l.strip()]) >= min_lines and not PLACEHOLDER.search(b)]


def strip_comments(body):
    return re.sub(r"<!--.*?-->", " ", body, flags=re.S)


def word_count(body):
    body = strip_comments(body)
    body = "\n".join(l for l in body.splitlines()
                     if not l.lstrip().startswith((">", "|", "#", "**File")))
    return len(re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", body))


def verdict_of(cell):
    cell = re.sub(r"<!--.*?-->", "", cell).strip().strip("*").strip()
    return VERDICTS.get(cell.lower())


def case_rows(sec4):
    """{'T1': {'expected': .., 'v1': .., 'final': ..}} from the section 4 table."""
    out = {}
    for cells in table_rows(sec4):
        if not cells:
            continue
        cid = cells[0].strip().upper()
        if not re.match(r"^T[1-9]$", cid) or cid in out or len(cells) < 7:
            continue
        out[cid] = {"expected": verdict_of(cells[3]), "v1": verdict_of(cells[5]),
                    "final": verdict_of(cells[6]), "raw_final": cells[6].strip()}
    return out


# --------------------------------------------------------------------------- P and O: the exports


def check_exports(res, measured):
    final = project_root(PROTOTYPE)
    v1 = project_root(ORIGINAL)
    measured["prototype_root"] = final.replace(os.sep, "/") if final else None
    measured["original_root"] = v1.replace(os.sep, "/") if v1 else None

    # P1
    files = code_files(final) if final else []
    if final and files:
        res.add("P1", "final prototype exported to prototype/", "PASS",
                "%s: %d source files" % (final.replace(os.sep, "/"), len(files)))
    else:
        res.add("P1", "final prototype exported to prototype/", "ERROR",
                "no package.json or index.html in prototype/ - download the final project from Bolt "
                "and unzip it there" if not final else "prototype/ has no source files")

    # P2
    problems = []
    for folder in (PROTOTYPE, ORIGINAL):
        if not os.path.isdir(folder):
            continue
        size = 0
        for here, dirs, names in os.walk(folder):
            if "node_modules" in dirs:
                problems.append("%s contains node_modules/ - delete it, it is not your work" % here.replace(os.sep, "/"))
                dirs.remove("node_modules")
            for n in names:
                if n == ".env" or n.startswith(".env."):
                    problems.append("%s/%s must not be committed" % (here.replace(os.sep, "/"), n))
                try:
                    size += os.path.getsize(os.path.join(here, n))
                except OSError:
                    pass
        if size > MAX_EXPORT_MB * 1024 * 1024:
            problems.append("%s/ is %.1f MB - an export is source files only" % (folder, size / 1048576.0))
    if not final:
        res.add("P2", "exports are clean: no node_modules, no .env, under %d MB" % MAX_EXPORT_MB, "ERROR",
                "nothing to check until prototype/ holds the export")
    else:
        res.add("P2", "exports are clean: no node_modules, no .env, under %d MB" % MAX_EXPORT_MB,
                "FAIL" if problems else "PASS", "; ".join(problems) if problems else "clean")

    # P3
    if not final:
        res.add("P3", "final stays in scope: no network, storage, backend, login", "ERROR", "no final prototype")
    else:
        hits = scope_hits(final)
        measured["scope_final"] = hits
        if hits:
            kinds = sorted(set(h["what"] for h in hits))
            res.add("P3", "final stays in scope: no network, storage, backend, login", "FAIL",
                    "%s - e.g. %s" % (", ".join(kinds), ", ".join(h["where"] for h in hits[:4])))
        else:
            res.add("P3", "final stays in scope: no network, storage, backend, login", "PASS",
                    "nothing out of scope found in the source")
    if v1:
        measured["scope_v1"] = scope_hits(v1)

    # O1
    if v1 and code_files(v1):
        res.add("O1", "v1 export kept in original/", "PASS", v1.replace(os.sep, "/"))
    else:
        res.add("O1", "v1 export kept in original/", "ERROR",
                "original/ holds no project - download v1 from Bolt BEFORE the first cleanup prompt")

    # O2
    if not (final and v1):
        res.add("O2", "final differs from v1", "ERROR", "needs both prototype/ and original/")
    else:
        a, b = fingerprint(v1), fingerprint(final)
        changed = sorted(p for p in set(a) | set(b) if a.get(p) != b.get(p))
        measured["changed_files"] = changed
        res.add("O2", "final differs from v1", "PASS" if changed else "FAIL",
                "%d file(s) changed, e.g. %s" % (len(changed), ", ".join(changed[:3])) if changed
                else "prototype/ is identical to original/ - the deck asks for at least one cleanup, "
                     "even when v1 passes everything")


# --------------------------------------------------------------------------- E: screenshots


def check_evidence(res, measured, report_sections):
    v1 = find_image("v1")
    why = image_problem(v1)
    res.add("E1", "v1 screenshot: evidence/v1.png", "FAIL" if why and v1 else ("ERROR" if why else "PASS"),
            why if why and v1 else ("evidence/v1.png (or .jpg) not found" if why else v1.replace(os.sep, "/")))

    issues = [r for r in table_rows(report_sections.get("5", "")) if filled(r, 3)]
    needed = max(2, len(issues))
    found, bad = [], []
    for n in range(1, needed + 1):
        p = find_image("issue-%d" % n)
        why = image_problem(p)
        if why is None:
            found.append("issue-%d" % n)
        else:
            bad.append("issue-%d" % n if why == "missing" else why)
    res.add("E2", "one screenshot per logged issue: evidence/issue-N.png",
            "PASS" if not bad else ("ERROR" if not found else "FAIL"),
            "%d issue screenshot(s)" % len(found) if not bad
            else "missing or unreadable: " + ", ".join(bad[:5]) + " (one per row in section 5, at least 2)")

    paths, missing, hashes = {}, [], {}
    for cid, _, _ in CASES:
        p = find_image("final-" + cid)
        why = image_problem(p)
        if why:
            missing.append("final-%s" % cid if why == "missing" else why)
        else:
            paths[cid] = p
            hashes.setdefault(file_hash(p), []).append(cid)
    if v1 and not image_problem(v1):
        hashes.setdefault(file_hash(v1), []).append("v1")
    dupes = [ids for ids in hashes.values() if len(ids) > 1]
    if missing:
        res.add("E3", "nine final screenshots, all different", "ERROR" if not paths else "FAIL",
                "missing or unreadable: " + ", ".join(missing[:5]))
    elif dupes:
        res.add("E3", "nine final screenshots, all different", "FAIL",
                "identical files: " + "; ".join(" = ".join(ids) for ids in dupes))
    else:
        res.add("E3", "nine final screenshots, all different", "PASS", "final-T1 ... final-T9")

    t9 = paths.get("T9")
    if not t9:
        res.add("E4", "T9 taken at narrow width (portrait)", "ERROR", "evidence/final-T9.png not found")
    else:
        w, h = image_info(t9)
        measured["t9_size"] = [w, h]
        res.add("E4", "T9 taken at narrow width (portrait)", "PASS" if h > w else "FAIL",
                "%dx%d" % (w, h) + ("" if h > w else " - not portrait; take it with the window or the "
                                                      "device toolbar at phone width (about 375 px)"))


# --------------------------------------------------------------------------- T: the nine cases


def check_cases(res, measured, sec):
    rows = case_rows(sec.get("4", ""))
    v1_matches = final_matches = 0
    for cid, name, expected in CASES:
        title = "%s %s: final result is %s" % (cid, name, expected)
        row = rows.get(cid)
        if row is None:
            res.add(cid, title, "ERROR", "no row %s in the section 4 table" % cid)
            continue
        if row["expected"] != expected:
            res.add(cid, title, "FAIL", "the Expected column says %s - it is %s, from the ACs, not from "
                                        "the page" % (row["expected"] or "nothing", expected))
            continue
        if row["v1"] == expected:
            v1_matches += 1
        if row["final"] is None:
            res.add(cid, title, "ERROR", "the final result is empty - write Available, Unavailable or Not testable")
        elif row["final"] == expected:
            final_matches += 1
            res.add(cid, title, "PASS", "final: %s" % row["final"])
        else:
            res.add(cid, title, "FAIL", "final: %s, expected %s" % (row["final"], expected))
    measured["v1_matches"] = v1_matches
    measured["final_matches"] = final_matches
    measured["cases_reported"] = sorted(rows)
    return rows


# --------------------------------------------------------------------------- L: lab-report.md


def check_report(res, measured):
    text = read(REPORT)
    if text is None:
        for cid, title in LAB_TITLES.items():
            res.add(cid, title, "ERROR", "lab-report.md not found")
        for cid, name, expected in CASES:
            res.add(cid, "%s %s: final result is %s" % (cid, name, expected), "ERROR", "lab-report.md not found")
        return {}
    sec = sections(text)

    def add(cid, ok, good, bad):
        res.add(cid, LAB_TITLES[cid], "PASS" if ok else "FAIL", good if ok else bad)

    # L1
    setup = {r[0].lower(): r[1] for r in table_rows(sec.get("1", "")) if len(r) > 1}
    missing = [k for k in ("tool", "model", "project")
               if not any(k in label and useful(value) for label, value in setup.items())]
    add("L1", not missing, "tool, model and project link recorded",
        "section 1 has no value for: " + ", ".join(missing))

    # L2
    s2 = sec.get("2", "")
    preds = [r for r in table_rows(s2) if filled(r, 2)]
    prompt_blocks = " ".join(blocks(s2))
    lost = [p for p in INITIAL_PROMPT if p not in prompt_blocks]
    probs = []
    if len(preds) < 2:
        probs.append("two predictions with the AC each one concerns (found %d)" % len(preds))
    if lost:
        probs.append("the initial prompt as sent, with its fixed sentences unchanged")
    elif BRACKETS.search(prompt_blocks) or "AC6" not in prompt_blocks:
        probs.append("the initial prompt with AC1-AC6 actually pasted in place of [paste AC1-AC6]")
    add("L2", not probs, "%d predictions; initial prompt pasted as sent" % len(preds),
        "section 2 needs " + "; ".join(probs))

    # L3
    s3 = sec.get("3", "")
    listing = real_blocks(s3)
    works = [l for l in strip_comments(s3).splitlines()
             if re.match(r"^\s*[-*]\s+\S", l) and len(l.strip()) > 12]
    add("L3", bool(listing) and bool(works), "v1 listing pasted; %d line(s) on what works" % len(works),
        "section 3 needs Bolt's list of files/components pasted and at least one line on what v1 does")

    # T1-T9 + L4
    rows = check_cases(res, measured, sec)
    no_v1 = [cid for cid, _, _ in CASES if not (rows.get(cid) or {}).get("v1")]
    add("L4", not no_v1, "v1 result recorded for all nine cases",
        "section 4: the v1 column is empty or not a verdict for " + (", ".join(no_v1) or "-"))

    # L5
    issues = [r for r in table_rows(sec.get("5", "")) if filled(r, 3)]
    measured["issues"] = len(issues)
    add("L5", len(issues) >= 2, "%d issue(s) logged" % len(issues),
        "section 5 needs at least 2 issues, each with evidence, a priority and a decision (found %d)" % len(issues))

    # L6
    s6 = sec.get("6", "")
    allblocks = " ".join(blocks(s6))
    probs = []
    if any(p not in allblocks for p in FIX_PROMPT):
        probs.append("the functional fix prompt, pasted as sent")
    if any(p not in allblocks for p in CLEANUP_PROMPT):
        probs.append("the cleanup prompt, pasted as sent")
    if BRACKETS.search(allblocks):
        probs.append("every [bracketed field] and AC# replaced")
    judged = [r for r in table_rows(s6)
              if filled(r, 2) and re.search(r"\b(accept|reject)(ed)?\b", " ".join(r), re.I)
              and re.search(r"\bAC\s?-?[1-6]\b|scope", " ".join(r), re.I)]
    measured["decisions"] = len(judged)
    if len(judged) < 2:
        probs.append("at least 2 suggestions marked accept or reject, each citing an AC or the scope (found %d)" % len(judged))
    add("L6", not probs, "both prompts pasted; %d decisions with a reason" % len(judged),
        "section 6 needs " + "; ".join(probs))

    # L7
    changes = [r for r in table_rows(sec.get("7", "")) if filled(r, 3)]
    measured["change_log_rows"] = len(changes)
    add("L7", 2 <= len(changes) <= 4, "%d change(s) logged" % len(changes),
        "section 7 needs 2-4 changes: issue, decision, change, result after retest (found %d)" % len(changes))

    # L8
    s8 = sec.get("8", "")
    marker = "Write your explanation below this line"
    words = word_count(s8.split(marker, 1)[1] if marker in s8 else s8)
    root = project_root(PROTOTYPE)
    named = re.findall(r"`([^`\s]+\.(?:jsx?|tsx?|vue|svelte|html))`", s8)
    exists = [n for n in named if root and os.path.isfile(os.path.join(root, n.lstrip("./")))]
    measured["explained_file"] = exists[0] if exists else None
    probs = []
    if not exists:
        probs.append("the path of a file that exists in your prototype, in backticks, e.g. `src/App.tsx`"
                     + (" (%s not found)" % named[0] if named else ""))
    if words < EXPLAIN_MIN:
        probs.append("at least %d words of explanation (found %d)" % (EXPLAIN_MIN, words))
    add("L8", not probs, "%s explained in %d words" % (exists[0] if exists else "-", words),
        "section 8 needs " + "; ".join(probs))

    # L9
    words = word_count(sec.get("10", ""))
    measured["conclusion_words"] = words
    add("L9", WORDS_MIN <= words <= WORDS_MAX, "%d words" % words,
        "section 10 has %d words, the task asks for %d-%d" % (words, WORDS_MIN, WORDS_MAX))
    return sec


# --------------------------------------------------------------------------- main

ORDER = ["P1", "P2", "P3", "O1", "O2", "E1", "E2", "E3", "E4"] + [c[0] for c in CASES] + list(LAB_TITLES)


def run():
    res, measured = Results(), {}
    check_exports(res, measured)
    sec = check_report(res, measured)
    check_evidence(res, measured, sec)
    res.rows.sort(key=lambda r: ORDER.index(r["id"]))
    return res, measured


def print_human(res, measured):
    counts = res.counts()
    print("Week 06 - prototype cleanup: the exports, the screenshots, the evidence\n")
    width = max(len(r["title"]) for r in res.rows)
    for r in res.rows:
        print(("%-6s %-4s %-*s  %s" % (r["verdict"], r["id"], width, r["title"], r["message"])).rstrip())
    print("-" * 78)
    if measured.get("scope_v1"):
        kinds = sorted(set(h["what"] for h in measured["scope_v1"]))
        print("v1 (original/) has out-of-scope code: %s - a candidate for your issue log (section 5)."
              % ", ".join(kinds))
    if "v1_matches" in measured:
        print("Cases matching the expected result: v1 %d of 9 - final %d of 9."
              % (measured["v1_matches"], measured["final_matches"]))
    print("SUMMARY pass=%d fail=%d error=%d   (%d checks)"
          % (counts["PASS"], counts["FAIL"], counts["ERROR"], len(res.rows)))
    if counts["FAIL"] or counts["ERROR"]:
        print("Every FAIL or ERROR you keep goes in lab-report.md section 9.1 and in submission.yml known_fails.")
        print("One you report and explain costs you nothing. One you hide costs the whole criterion.")
    else:
        print("Files and shape are clean. The grader still opens your screenshots - this says nothing "
              "about whether they show what you reported.")


def main():
    parser = argparse.ArgumentParser(description="Week 06 checker - run from inside week-06/")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if not os.path.isdir("tests") and not os.path.exists(REPORT) and not os.path.isdir(PROTOTYPE):
        message = "run this from inside your week-06/ folder:  cd week-06 && python tests/check_prototype.py"
        print(json.dumps({"ok": False, "error": message}) if args.json else "ERROR: " + message)
        return 3

    res, measured = run()
    counts = res.counts()
    ok = counts["FAIL"] == 0 and counts["ERROR"] == 0
    if args.json:
        print(json.dumps({"ok": ok, "counts": counts, "total": len(res.rows),
                          "rows": res.rows, "measured": measured}, ensure_ascii=False, indent=2))
    else:
        print_human(res, measured)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
