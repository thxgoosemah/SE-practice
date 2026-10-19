#!/usr/bin/env python3
"""Helper (NOT part of the submission, do not commit it).

  python finish.py fill "Full Name" "Group" 24B031016 github-login
  python finish.py final        # after you committed everything else; run from the folder above week-04/
"""
import json, re, subprocess, sys, os

W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "week-04")
def rd(p): return open(os.path.join(W, p), encoding="utf-8").read()
def wr(p, t): open(os.path.join(W, p), "w", encoding="utf-8", newline="\n").write(t)
def sub(p, pairs):
    t = rd(p)
    for k, v in pairs.items(): t = t.replace(k, v)
    wr(p, t)

if len(sys.argv) >= 6 and sys.argv[1] == "fill":
    _, _, name, group, sid, gh = sys.argv[:6]
    pairs = {"@@NAME@@": name, "@@GROUP@@": group, "@@STUDENT_ID@@": sid, "@@GITHUB@@": gh}
    for f in ("lab-report.md", "AI_USAGE.md", "submission.yml"): sub(f, pairs)
    print("filled")
elif len(sys.argv) == 2 and sys.argv[1] == "final":
    run = lambda *a: subprocess.run(a, cwd=W, capture_output=True, text=True)
    py = sys.executable
    out = run(py, "tests/check_models.py").stdout.rstrip("\n")
    m = re.search(r"SUMMARY pass=(\d+) fail=(\d+) error=(\d+)", out)
    fails = re.findall(r"^([A-Z]{2}\d)\s+(?:FAIL|ERROR)\s", out, re.M)
    commit = run("git", "rev-parse", "--short", "HEAD").stdout.strip()
    kept = "none (no FAIL)" if not fails else ", ".join(fails) + "  <-- EXPLAIN EACH ONE HERE before committing"
    sub("lab-report.md", {"@@CHECKER_OUTPUT@@": out, "@@KEPT_FAILS@@": kept})
    sub("submission.yml", {"@@PASS@@": m.group(1), "@@FAIL@@": m.group(2), "@@ERROR@@": m.group(3),
                           "@@COMMIT@@": commit, "@@KEPT_LIST@@": "[" + ", ".join(fails) + "]"})
    print(out); print("commit:", commit)
    print(run(py, "tests/validate_submission.py").stdout)
else:
    print(__doc__)
