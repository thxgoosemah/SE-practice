# Week 06 — Vibe Coding and Prototype Cleanup

**Course:** AI-Driven Software Engineering (Fall 2026, KBTU SITE)
**Practice work #06** · 1 point · AI-use level: **D (AI-integrated, disclosure required)**

> **This week the tool is fixed: Bolt.new**, the AI app builder the practice deck names. The
> prototype is whatever Bolt generates — usually React with TypeScript — and you do not need to
> know React to do this lab: you test the page in the browser and read the code Bolt wrote.
> Your choice is in the decisions: which issues to fix, which suggestions to reject, and why.
>
> **What stays identical for everyone:** the scenario and AC1–AC6 in §3, the three prompts in §5
> (sent unchanged except for the bracketed fields), the nine cases in §6, and the file layout in §2.
>
> **If Bolt.new is not available to you** (sign-up blocked, daily limit reached before you
> finished), finish with another browser app builder — Lovable, v0, Google AI Studio's Build mode —
> and say so in `submission.yml` (`assistant.fallback_reason`) and in `AI_USAGE.md`. Same prompts,
> same cases. It costs you nothing.

---

## 1. The idea of this lab

Last week you wrote one function, `can_book`, and proved it with tests. This week you skip the
function and ask an AI app builder for the whole page — in one prompt, in about a minute. It will
look finished. The lab is about the difference between **looking finished** and **meeting AC1–AC6**.

You keep the first generated version (v1) exactly as it came. You test it against nine fixed cases
in the page itself. You log what is wrong, fix it **one issue per prompt**, reject anything that
widens the scope, retest after every change, and prove the final version with screenshots.

You already know what correct looks like: AC1–AC5 are last week's acceptance criteria, and five of
the nine cases are last week's table. AC6 is new — the page must work on a phone-width screen and
explain its answers.

**Main message (the deck's own rule):** "AI changed it" is not evidence that the change is correct.

**Time budget:** ~50 min in class + ~60 min at home.

---

## 2. Deliverables

By the deadline, your branch `week-06` must contain:

```
week-06/
├── README.md                  # this file (read-only)
├── lab-report.md              # THE worksheet — fill in all 10 sections
├── AI_USAGE.md                # AI disclosure (every week)
├── submission.yml             # machine-readable declaration — facts only
├── original/                  # v1: Bolt's FIRST version, downloaded before any cleanup prompt
│   ├── package.json  (or index.html)
│   └── src/ …
├── prototype/                 # your FINAL version, downloaded after the last accepted change
│   ├── package.json  (or index.html)
│   └── src/ …
├── evidence/                  # screenshots, PNG or JPG
│   ├── v1.png
│   ├── issue-1.png, issue-2.png, …      one per row of your issue log
│   └── final-T1.png … final-T9.png      one per case, run on the final version
└── tests/
    ├── check_prototype.py     # provided checker — do not edit
    └── validate_submission.py # provided validator for submission.yml — do not edit
```

**Never commit `node_modules/` or a `.env` file.** A Bolt download contains source files only; keep
it that way.

---

## 3. The task

Everything in this block comes from the Lesson 06 practice deck, unchanged.

```text
User story: As a student, I want to check a room's availability so that I can choose a valid booking time.

Prototype scope: one responsive page for checking one selected room; no login, backend, database, or external API.
Use fictional room and booking data only. The prototype checks availability; it does not save or confirm a booking.

Acceptance criteria
AC1: Accept a candidate interval only when 0 ≤ start < end ≤ 1440 and start is after the supplied current time.
AC2: Reject a booking longer than 120 minutes.
AC3: Reject the request when the selected room is blocked.
AC4: Reject any interval that overlaps an existing booking; touching endpoints are allowed.
AC5: Show a clear Available / Unavailable decision without changing the existing booking data.
AC6: The page remains usable at desktop and narrow/mobile width and gives understandable validation feedback.

Intervals include the start and exclude the end. Other rules still apply.
```

Times in the criteria are **minutes after midnight**: 600 means 10:00, 1440 means 24:00. Your page
will almost certainly use `HH:MM` time inputs; somewhere in Bolt's code there is a conversion
between the two, and that is where the end of the day lives (§9.2 of the worksheet).

**What counts as cleanup** (deck, slide 10) — always: identify a concrete problem, make a focused
change, retest.

| Area | Look for | Possible cleanup |
| --- | --- | --- |
| Correctness | Broken or inconsistent behaviour | Fix logic; add a regression test |
| Usability | Unclear labels or feedback | Improve labels, states and messages |
| Code | Duplication or oversized components | Small refactor without changing behaviour |
| Scope | Unrequested features | Remove or reject scope creep |

**One question is deliberately open.** AC1 allows a booking to end at 24:00, but an `HH:MM` time
input stops at 23:59. What your final page does about it is your decision — declare it
(`assumptions.end_of_day`) and defend it in §9.2. Any answer is acceptable; not deciding is not.

---

## 4. Before class

- A Bolt.new account you have **signed in to**, in a current Chrome, Edge or Firefox.
- Bolt's free plan has a daily limit. This lab needs one generation and three or four short
  prompts — well within it — **if** you do not spend it on "make it better" prompts.
- Python 3.8+ to run the checker. No Python? On GitHub, open your repository → **Code → Codespaces → Create
  codespace on week-06** and run it in the terminal there, or fill `submission.yml` by hand and say
  so in §9.1.

---

## 5. The lab

### Part 0 — Setup (~3 min, in class)

1. `git checkout main && git pull && git checkout -b week-06` (full steps in `SETUP.md`).
2. Unzip `Week_06.zip` into the root of your repository so that `week-06/` sits next to `week-05/`.
3. Fill in `lab-report.md` §1. Commit: `week-06: setup`.

### Part 1 — Task 1: define before generating (~6 min, in class)

1. Read the block in §3 once more. **Before you open Bolt**, write two predictions in the §2
   table: where do you expect v1 to go wrong, and which AC is that? (Last week's defects are a good
   place to start.)
2. Build your initial prompt: the deck's prompt below, with AC1–AC6 from §3 pasted in place of
   `[paste AC1–AC6]`. **Nothing else changes.**

```text
Build a small responsive Smart Campus Room Availability Checker. Requirements: [paste AC1–AC6]. Use fictional sample data only. Keep the implementation simple and within one-page scope. Do not add authentication, backend services, analytics, or unrelated features. After building, briefly list the main files/components you created.
```

3. Paste the finished prompt into §2. Commit: `week-06: predictions and initial prompt`.

### Part 2 — Task 2: generate prototype v1 (~8 min, in class)

1. In Bolt.new, **create one new project** and send the prompt. Wait for a usable preview.
2. **Do not** ask Bolt to "improve everything". v1 is a baseline for comparison, not a product.
3. If the build does not run at all, you may send **one** focused repair prompt; whatever runs
   after it is v1. Paste that prompt in §3.
4. Save the evidence of v1 **before you send any other prompt**:
   - a screenshot of the preview → `evidence/v1.png`;
   - Bolt's download of the project (its export / download option gives a `.zip` of the source) →
     unzip into `original/`, so that `original/package.json` (or `original/index.html`) exists.
     If the zip unpacks into one folder, that is fine — the checker looks one level down.
5. Paste Bolt's list of files/components into §3 and write what v1 does.
6. Commit: `week-06: v1 as generated by Bolt`.

### Part 3 — Task 3: test v1 (~15 min in class, finish at home)

Run the nine cases in §6 **in the page itself**. For each, write the v1 result in the §4 table:
**Available**, **Unavailable**, or **Not testable** — when the page gives you no way to set the case
up (no current-time input, no way to block a room, no room with a 10:00–11:00 booking). "Not
testable" is a real finding, not a failure on your part: AC1 says *supplied* current time, AC3
needs a blocked room, and the page has to let you supply them.

Then choose your cleanup targets and log them in §5:

- at least **two** issues — one functional and one usability or code-quality issue when you have
  them. If v1 passes every case, log a justified cleanup that preserves behaviour;
- each with its evidence: the steps, what the AC expects, what the page did;
- a screenshot of each → `evidence/issue-1.png`, `evidence/issue-2.png`, …;
- a priority and a decision (Fix / Reject / Defer).

Also look at Bolt's code for scope creep: a "Book" button, a login screen, storage, calls to an API.
The checker prints anything it finds in `original/` under its table as a hint.

Commit: `week-06: v1 tested, issues logged`.

### Part 4 — Task 4: clean up with focused prompts (~20 min, at home)

**One issue per prompt.** For a functional issue, send the deck's fix prompt, with the brackets
filled in from your issue log:

```text
In the current prototype, [steps] produces [observed result], but AC# requires [expected result]. Make the smallest change that fixes this behavior. Preserve the other acceptance criteria. Explain which file/component you changed and why.
```

For a usability or code-quality issue, send the deck's cleanup prompt:

```text
Review only [component/area] for unnecessary duplication, confusing naming, or UI feedback problems. Suggest one small cleanup. Do not add features or redesign the whole application. Implement it only if it preserves AC1–AC6.
```

After **every** prompt:

1. Paste the prompt as sent and Bolt's answer into §6.
2. **Judge every change or suggestion** in the §6 table: accept or reject, with the AC or the scope
   rule that justifies it. Bolt will offer extras ("I also added a Book button", "saved your
   bookings so they persist"). Read AC5 and the scope before you keep any of them.
3. **Retest.** Repeat the case that exposed the issue first, then run all nine again to catch
   regressions. Write what you ran in the last column.
4. Log the change in §7. Two to four changes in total.

Rule from the deck: reject a suggestion if it broadens scope, breaks working behaviour, or cannot
be justified. A useful result can include rejecting an AI suggestion.

### Part 5 — Final evidence (~15 min, at home)

1. Download the final project from Bolt. **Empty `prototype/`** (keep `.gitkeep` if you like) and
   unzip the final version there.
2. Run the nine cases on the final version and fill the "Result on final" column.
3. Take one screenshot per case, showing the inputs and the decision →
   `evidence/final-T1.png` … `final-T9.png`. **T9 is taken at phone width**: open the preview in
   its own tab, press F12, switch on the device toolbar, pick a phone (about 375 px wide) and use
   the toolbar's "capture screenshot" — the result is portrait, which is what E4 checks.
4. Fill §8: one component Bolt generated, the one that decides availability if you can find it,
   explained **in your own words** — what it does and how it decides. Name its path in backticks.
5. Commit: `week-06: final prototype and evidence`.

### Part 6 — Report, declaration, submit (~10 min, at home)

1. Answer §9.2 and §9.3 and write the conclusion, §10 (120–180 words).
2. From inside `week-06/`, run the checker: `python tests/check_prototype.py`. Every FAIL or ERROR
   you keep goes in §9.1 with the reason.
3. Fill in `AI_USAGE.md`.
4. Commit everything, then note the hash: `git rev-parse --short HEAD`.
5. Fill in `submission.yml` (§8 below), run the validator, commit, push, open the PR (§9).

---

## 6. The nine cases

**Base for every case:** current time **09:00**; the selected room is **not blocked**; the room's
**only booking that day is 10:00–11:00**. If v1's sample data has no such room, or no way to set
the current time or to block a room, the case is **Not testable** on v1 — and that is your first
issue.

| # | Case | Set up and request | Expected | AC | Minutes |
| --- | --- | --- | --- | --- | --- |
| T1 | Touching | 11:00–12:00 | Available | AC4 | 660–720 |
| T2 | Overlap | 10:30–11:30 | Unavailable | AC4 | 630–690 |
| T3 | Blocked | 11:00–12:00, room blocked | Unavailable | AC3 | 660–720 |
| T4 | Exactly 2 hours | 12:00–14:00 | Available | AC2 | 720–840 |
| T5 | Over 2 hours | 12:00–14:01 | Unavailable | AC2 | 720–841 |
| T6 | Starts now | 09:00–09:30, current time 09:00 | Unavailable | AC1 | 540–570, now 540 |
| T7 | Reversed times | 12:00–11:00 — and the page says why | Unavailable | AC1, AC6 | 720–660 |
| T8 | Same check twice | T1, then T1 again without reloading | Available | AC5 | 660–720 twice |
| T9 | Narrow screen | T1, at about 375 px wide | Available | AC6 | 660–720 |

T1–T6 are the deck's six cases. **T7–T9 are ours**, one for each part of the deck's criteria the
six do not reach: T7 is "understandable validation feedback" (AC6) — the decision alone is not
enough, the page has to say what is wrong; T8 is "without changing the existing booking data"
(AC5) — a page that saves what it checks says Unavailable the second time; T9 is "usable at
narrow/mobile width" (AC6).

**The Expected column comes from AC1–AC6, never from the page.** The checker compares your
Expected column with this table; a row you "corrected" to match the page is a FAIL.

---

## 7. Checking your work

### Verdicts

```
PASS   the check found what it was looking for
FAIL   the content is there but wrong, or not enough of it
ERROR  it could not check: a file, a folder or a section is missing
```

From inside `week-06/`:

```text
python tests/check_prototype.py
```

It runs 27 checks:

| Checks | What they look at |
| --- | --- |
| **P1–P3** | The final export in `prototype/`: present (P1), clean — no `node_modules/`, no `.env`, under 5 MB (P2), and in scope (P3): no network calls, browser storage, backend or database, login, or analytics anywhere in the source. |
| **O1–O2** | v1 is kept in `original/` (O1), and the final is not identical to it (O2) — the deck asks for at least one cleanup even when v1 passes everything. |
| **E1–E4** | `evidence/`: `v1.png` (E1); one `issue-N.png` per row of your issue log, at least two (E2); `final-T1` … `final-T9`, all different files (E3); `final-T9` in portrait (E4). PNG or JPG. |
| **T1–T9** | §4 of the worksheet: the Expected column is the one in §6, and your final result matches it. |
| **L1–L9** | `lab-report.md` has its sections filled in: both prompts pasted as sent (their fixed sentences are checked, and no `[bracketed field]` may be left), at least two decisions citing an AC, a real file named in §8. |

**The checker never runs your prototype and never looks inside your screenshots.** It checks that
the evidence exists and that your report is consistent with it. The grader opens the screenshots:
a final-T8 screenshot that shows "Unavailable" next to a table that says "Available" costs the whole
*Evidence and honesty* criterion.

The first run on the untouched folder gives `0 PASS · 9 FAIL · 18 ERROR`. That is the intended
start.

---

## 8. The declaration — `submission.yml`

Facts only. From inside `week-06/`:

```text
python tests/validate_submission.py
```

Three things decide marks:

- **`checker.commit` is the commit you ran the checker at** — normally the one just before the
  commit that adds the declaration. It must be a commit on your `week-06` branch.
- **Your numbers are re-run at the last commit of your pull request.** We run `check_prototype.py`
  there ourselves. Numbers that match are settled automatically. Numbers that do not match cost the
  whole *evidence and honesty* criterion — so if you change anything after your last checker run,
  run it again and update `submission.yml`.
- **A FAIL you report costs you nothing extra.** If your final page still cannot express T6 and you
  ran out of prompts, write `Not testable`, list `T6` in `known_fails` and say in §9.1 what you
  tried. Hiding it is what costs.

---

## 9. Submit

1. Push the branch: `git push -u origin week-06`.
2. Pull Request `week-06 → main` in your own repository. Title: `Week 06 — Vibe Coding and
   Prototype Cleanup`. Description in the fixed shape from `SETUP.md` §4.
3. **Leave the PR open — do not merge it.**
4. In the Teams assignment: **+ Add work → Link → paste the pull request URL.**

The practice deck asks you to email screenshots to the main lecturer at the end of class. **That
does not apply to our groups** — the PR link in Teams is the only submission, and it contains
everything the email would have: your name, the tool, the project link, v1 and its screenshot, the
final version and its test evidence, the prompts and the AI's answers, and the change log.

**Deadline:** before the start of the next practice session. Late submissions per the course
policy; the Teams assignment closes at the end of the following week.

---

## 10. Grading — 1 point, 4 × 0.25

| Criterion | 0.25 when … |
| --- | --- |
| **Prototype** | The final page gives the expected result in all nine cases (T1–T9) and the screenshots show it; it stays in scope (P3); v1 is kept unedited in `original/`; the final differs from v1; the exports are clean. |
| **Testing** | §2 predictions written before generating; §4 v1 and final results from real runs, the Expected column untouched; a v1 screenshot, one per issue, nine different final screenshots, T9 at phone width. |
| **Cleanup decisions** | §5 has two or more issues with steps, expected and observed; §6 one issue per prompt, the deck's prompts as sent, every change or suggestion accepted or rejected with an AC or scope reason; §7 two to four changes, each retested. |
| **Evidence and honesty** | §8 explains a real file in your own words; §9 and §10 are your own; `AI_USAGE.md` complete; `submission.yml` passes the validator and its numbers match the re-run; PR open with 3 or more meaningful commits. |

**A FAIL you report and explain costs you nothing. One you hide costs the whole criterion.**

**Not accepted:** `original/` written after the cleanup, or identical to a later version ·
screenshots that are edited, composited, or do not show what the table says · an Expected column
changed to match the page · prompts paraphrased instead of pasted as sent · "make it better"
prompts in place of one issue per prompt · `node_modules/` or a `.env` committed · findings that
name no case, no AC and no file ("Bolt made mistakes and I fixed them") · a merged PR, a repo link,
or an emailed submission.

---

## 11. FAQ

**I don't know React. Can I still do this?** Yes. You test in the browser, and for §8 you need to
read one file and explain it — Bolt's own explanation of the file is a fine starting point, as
long as the words in §8 are yours and you can say them aloud in class.

**v1 passed all nine cases.** Then record that honestly, log a justified cleanup that preserves
behaviour (a clearer message, a component split, a removed extra feature), and retest. O2 still
needs the final to differ from v1 — the deck asks for at least one cleanup.

**Bolt hit its daily limit in the middle of Part 4.** Finish the prompts the next day, or move to
another app builder from your final Bolt download (the fallback note at the top of this file). Write what happened in §9.1 and
`AI_USAGE.md`. A case you could not fix goes in `known_fails`.

**Can I edit the code by hand instead of prompting?** A small hand edit is allowed — log it in §7
with "hand edit" in the Change column and retest. But the lab is about directing an AI with
evidence; a final built mostly by hand misses the point of the *Cleanup decisions* criterion.

**The page uses `HH:MM` and the cases are in minutes.** Use the "Set up and request" column of §6;
the minutes are there so you can check Bolt's conversion.

**The checker found `localStorage` in my final version.** Then the page stores something, and AC5
and the scope say it must not. Remove it with a fix prompt, or — if you are certain it stores
nothing about bookings (a theme setting, say) — keep it, list `P3` in `known_fails` and justify it
in §9.1.

**Where does the grader run my files?** Nowhere — nothing in `week-06/` is executed. The checker
reads files; the grader opens your screenshots and, where it helps, your Bolt project link.
