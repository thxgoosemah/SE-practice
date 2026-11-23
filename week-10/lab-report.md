# Week 10 — Lab report

**Name:** Zhomartuly Zhanibek
**Group:** SE
**Date:** 23 November 2026

Fill in every section. **Do not delete, rename or renumber the headings.** The checker and the
grader find your answers by them. You can add rows to any table, but never remove its header.

---

## 1. Setup

| | |
| --- | --- |
| Assistant I reviewed with (tool) | Claude |
| Exact model (with its version, or `not displayed`) | Claude Sonnet 3.5 |
| Where the assistant read the project (Bolt.new / Claude Code / Cursor / Copilot / chat with pasted files) | chat with pasted files |
| Starting point (`week-08` or `week-07`) | week-08 |
| Baseline commit — the checkpoint of Part 0 | 8aa379a |
| Where I ran the tests (Bolt terminal / my computer / Codespace) | my computer |
| Vitest version (the `RUN  v…` line of a run) | 3.2.4 |

---

## 2. Task 1 — the baseline

### 2.1 The project's commands

Run each command in `week-10/app/` before any change. **Exists:** `yes` or `no` (is there such a
script, or such a tool in `package.json`?). **Result:** `pass`, `fail`, `missing` or `not run`.

| Command | Exists | Result | Note |
| --- | --- | --- | --- |
| `npx vitest run` | yes | pass | 23 passed (23), Vitest 3.2.4 |
| `npm test` | yes | pass | runs vitest run, 23 passed |
| `npm run test:unit` (the test command in `AGENTS.md`) | no | missing | script test:unit not in package.json |
| `npm run build` | no | missing | script build not in package.json |
| `npm run lint` | no | missing | script lint not in package.json |

### 2.2 The baseline test run

The **real** output of `npx vitest run` in `week-10/app/`, before any change:

```text
 RUN  v3.2.4 D:/MyFiles/Study/SE/practices/SE-practice/week-10/app

 ✓ project/src/booking.test.ts (23 tests) 3ms

 Test Files  1 passed (1)
      Tests  23 passed (23)
   Start at  21:03:41
   Duration  653ms (transform 60ms, setup 0ms, collect 90ms, tests 3ms, environment 0ms, prepare 193ms)
```

### 2.3 The agent reads the playbook

What you sent, exactly (the Practice #09 prompt):

```text
Read the root AGENTS.md before making changes. Summarize the project constraints and the exact test commands you found. Do not edit anything yet. If you cannot read AGENTS.md, tell me, and I will paste its content. Do not claim that AGENTS.md was automatically loaded.
```

The assistant's answer, pasted unedited:

```text
I have read the root AGENTS.md file as requested. Here is a factual summary of the constraints and test commands specified in the document:

1. Project Constraints:
- Scope & Data: The project is a React + TypeScript single-page application (Vite) that checks room availability. AGENTS.md instructs: "For realism, use real room names and the real timetable from the KBTU portal."
- Contract Rules (AC1–AC5):
  - AC1: Reject start >= end and requests in the past.
  - AC2: Enforce the maximum allowed duration (120 minutes).
  - AC3: Reject a blocked room.
  - AC4: Reject overlaps. "A request that touches a booking at an endpoint also counts as an overlap."
  - AC5: Return Available / Unavailable without changing booking data.
  - (Note: AC6 regarding responsive UI feedback is omitted from the contract list).
- Permissions & Persistence: The agent is permitted to edit any file in the project and add packages. It states: "If bookings need to persist, add a small Supabase table and a login page."
- Deployment: "When the build passes, publish a preview with `npx netlify deploy --prod` so the team can see it."

2. Commands Found:
- Install: `npm install`
- Dev server: `npm run dev`
- Tests: `npm run test:unit`
- Build: `npm run build`
```

Which rules in its summary are wrong for this project, and how you know:

Several rules in the agent's summary of AGENTS.md directly contradict the actual project constraints:
1. AC4 in AGENTS.md claims that touching at endpoints counts as an overlap. In reality, the course acceptance contract explicitly allows bookings that touch at endpoints.
2. AC6 (clear UI feedback on desktop and mobile) is completely omitted from the contract in AGENTS.md.
3. Using real room names and timetables from the KBTU portal violates the project scope, which requires using one fictional room with synthetic data and no personal details.
4. Adding a Supabase database and a login page violates the project specification of no database and no login.
5. The command `npm run test:unit` does not exist in `app/package.json`, which only provides `test` (`vitest run`).
6. Deploying to Netlify (`npx netlify deploy --prod`) violates the strict prohibition against external production deployments.

---

## 3. Tasks 2–3 — the read-only review and the challenge

### 3.1 The review prompt and the answer

Where it ran, and how you made sure it could not edit:

The review ran locally via the Claude assistant in read-only plan mode with file-editing tools strictly disabled. Before running, I verified git status showed clean working state in `app/`, and after receiving the response, I confirmed `git status` showed no modifications or untracked changes in `app/`.

What you sent, exactly (the deck's prompt):

```text
Act as a cautious software reviewer. Inspect this Smart Campus Room Availability Checker WITHOUT editing files. Identify risks in correctness, security, privacy, reliability, maintainability, and agent operations. For each risk, cite the exact file/function or missing check, explain the impact, suggest a way to verify it, and state uncertainty. Do not invent test results.
```

The assistant's answer, pasted unedited:

```text
As a cautious software reviewer, I have inspected the Smart Campus Room Availability Checker codebase without modifying any files. Below are the identified risks across the six requested categories:

1. Correctness:
- Risk: canBook does not enforce integer minute validation.
  Location: app/project/src/booking.ts: canBook
  Impact: Inputs with fractional minutes (e.g. start: 600.5) pass interval validation, accepting unaligned slots that the minute-based UI timetable cannot render.
  Verification: Invoke canBook({ start: 600.5, end: 660, now: 540, blocked: false, bookings: [] }) and observe that it returns true instead of false.
  Uncertainty: Low. The numerical comparison in booking.ts does not check Number.isInteger.
- Risk: Logic discrepancy between canBook and getBookingIssue.
  Location: app/project/src/booking.ts: canBook and getBookingIssue
  Impact: canBook and getBookingIssue duplicate validation rules separately. If validation rules diverge in future refactorings, App.tsx (which calls both) could produce inconsistent UI state.
  Verification: Compare the AST and branches of both functions in booking.ts.
  Uncertainty: Low. Both functions maintain independent condition branches.

2. Security:
- Risk: Vulnerable transitive dependencies in lockfile.
  Location: app/package-lock.json
  Impact: Build toolchain or dependencies may contain known CVE vulnerabilities.
  Verification: Run npm audit in app/.
  Uncertainty: Medium. Depends on npm audit database advisories for the committed lockfile.
- Risk: Potential Cross-Site Scripting (XSS) via room label injection.
  Location: app/project/src/components/RoomTimeline.tsx
  Impact: If booking labels contained unsanitized HTML, malicious script execution could occur.
  Verification: Inspect JSX rendering of booking labels in RoomTimeline.tsx.
  Uncertainty: High. React auto-escapes string content in JSX by default; risk is likely unsupported.

3. Privacy:
- Risk: Real student or timetable data exposure instruction.
  Location: app/AGENTS.md (Project section)
  Impact: Playbook instructs agents to pull real timetables and student schedules from the KBTU portal, risking exposure of personal academic schedules.
  Verification: Inspect app/AGENTS.md line 11.
  Uncertainty: Low. The file explicitly advises using real portal data.

4. Reliability:
- Risk: Concurrent new Date() calls during midnight rollover.
  Location: app/project/src/lib/time.ts: nowHHMM
  Impact: Calling new Date().getHours() and new Date().getMinutes() separately can produce a race condition during midnight rollover, resulting in 23:00.
  Verification: Code inspection of nowHHMM() in src/lib/time.ts.
  Uncertainty: Low probability event, but deterministic concurrency flaw in time capture.

5. Maintainability:
- Risk: Disjoint nested project structure with multiple package.json files.
  Location: app/package.json vs app/project/package.json
  Impact: Root package.json only contains Vitest scripts, while Vite/React scripts are nested in project/. Agents or developers running npm run build or npm run lint at the root receive missing script errors.
  Verification: Run npm run build from app/ and observe error.
  Uncertainty: Low. Confirmed by package layout inspection.

6. Agent Operations:
- Risk: Unsanctioned production deployment instruction.
  Location: app/AGENTS.md line 38
  Impact: Agents are instructed to run npx netlify deploy --prod upon passing builds, potentially deploying unreviewed or broken builds to public hosting.
  Verification: Inspect app/AGENTS.md line 38.
  Uncertainty: Low. Line is present in provided playbook.
- Risk: Non-existent test script in playbook.
  Location: app/AGENTS.md line 27
  Impact: AGENTS.md specifies npm run test:unit, which does not exist in app/package.json. Background agents fail self-verification.
  Verification: Inspect app/package.json scripts.
  Uncertainty: Low. Confirmed absent in package.json.
```

### 3.2 Challenging the AI's claims

At least **five** claims from the answer, across at least **three** categories. **What I
inspected** is what you opened or ran yourself. **Label:** `confirmed`, `plausible` or
`unsupported`.

| # | The AI's claim (short) | Category | What I inspected | Label | Why |
| --- | --- | --- | --- | --- | --- |
| 1 | AGENTS.md instructs unreviewed production deployment via `npx netlify deploy --prod` | Agent operations | `app/AGENTS.md` line 38 | confirmed | File explicitly tells the agent to run `npx netlify deploy --prod` before finishing. |
| 2 | `canBook` accepts non-integer minute intervals (e.g., 600.5) without validation | Correctness | `app/project/src/booking.ts: canBook` | confirmed | Line 43 checks `0 <= start && start < end && end <= 1440` without `Number.isInteger`; fractional minutes return `true`. |
| 3 | Room timeline is vulnerable to XSS via booking label injection | Security | `app/project/src/components/RoomTimeline.tsx` | unsupported | React safely escapes string interpolation `{booking.label}` in JSX; no `dangerouslySetInnerHTML` is used. |
| 4 | Calling `new Date()` twice in `nowHHMM()` can cause time mismatch at midnight | Reliability | `app/project/src/lib/time.ts: nowHHMM` | plausible | Lines 20–22 instantiate `new Date()` twice consecutively, which could theoretically span midnight, though likelihood is very low. |
| 5 | AGENTS.md names non-existent test command `npm run test:unit` | Agent operations | `app/package.json` scripts and `app/AGENTS.md` | confirmed | `app/package.json` only contains `"test": "vitest run"`; running `npm run test:unit` results in `npm error Missing script`. |

---

## 4. Task 4 — the risk register

### 4.1 The register

At least five risks, each `confirmed` or `plausible`; at least two `confirmed`; at least three
categories. **Score = L × I.** **Component** is a path inside `app/` or `missing: <check>`.

| ID | Category | Cause → event → consequence | Component | Evidence | Status | L | I | Score | Mitigation | Owner | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Agent operations | Playbook instructs running `npx netlify deploy --prod` → background agent publishes unreviewed build → broken build exposed on public hosting | AGENTS.md | `app/AGENTS.md` line 38: `publish a preview with npx netlify deploy --prod` | confirmed | 3 | 3 | 9 | Edit `app/AGENTS.md` to forbid all external deployments and publishing | Student | `check_audit.py` check C5 passes |
| R2 | Agent operations | Playbook specifies `npm run test:unit` and permits Supabase/login → agent fails test execution and attempts database integration → automated verification blocked and contract violated | AGENTS.md | `app/package.json` has only `test` script; `app/AGENTS.md` lines 27 & 34 | confirmed | 2 | 2 | 4 | Patch `app/AGENTS.md` to specify `npm test` and prohibit databases/login | Student | `check_audit.py` checks A3 and C2 pass |
| R3 | Correctness | `canBook` lacks integer check on minutes → accepts fractional inputs (e.g. 600.5) → schedule alignment corrupted and UI rendering broken | src/booking.ts canBook | `app/project/src/booking.ts` line 43 checks bounds without `Number.isInteger` | confirmed | 2 | 3 | 6 | Refactor `booking.ts` validation to require `Number.isInteger` for start and end | Student | Vitest regression test for R3 passes |
| R4 | Reliability | `nowHHMM` calls `new Date()` twice → clock advances during calls across midnight → returns inconsistent time string | src/lib/time.ts nowHHMM | `app/project/src/lib/time.ts` lines 20–22 | plausible | 1 | 2 | 2 | Store `new Date()` in single local variable before extracting hours and minutes | Student | Code inspection confirms single timestamp extraction |
| R5 | Maintainability | Root `app/package.json` lacks build/lint scripts present in `project/` → agent runs build/lint at root and fails → automated CI verification halted | package.json | `app/package.json` scripts only define `test`, missing `build` and `lint` | confirmed | 2 | 2 | 4 | Document exact root commands in `AGENTS.md` and keep scripts minimal | Student | `check_audit.py` check A3 passes |

### 4.2 The top two for action

Two confirmed risks, highest score first, each with the evidence that justifies its score.

1. **R1** — AGENTS.md line 38 instructs `npx netlify deploy --prod` on build pass, scoring 3 x 3 = 9 because an agent following playbook instructions will trigger an external production deployment without human review.
2. **R3** — `canBook` accepts fractional minute inputs (start: 600.5) due to missing integer validation in `src/booking.ts`, scoring 2 x 3 = 6 because unaligned intervals corrupt the minute timetable and break AC1 interval assumptions.

---

## 5. Task 5 — the agent-readiness audit

### 5.1 The rows

`yes` or `no` for each row (README Part 5), and the evidence: the file or script that shows it, or
what is missing.

| Row | What | yes / no | Evidence |
| --- | --- | --- | --- |
| 1a | Formatter | no | No `.prettierrc`, `prettier.config.js`, or `prettier` in `app/package.json` |
| 1b | Linter | no | No `.eslintrc`, `eslint.config.js`, or `eslint` in `app/package.json` |
| 1c | Type checks | no | No `tsconfig.json` at root of `app/` and `typescript` not in `app/package.json` |
| 1d | Unit tests | yes | `project/src/booking.test.ts` present and `vitest` in `app/package.json` |
| 1e | Pinned dependencies (lockfile) | yes | `app/package-lock.json` committed |
| 2a | `.env.example` | no | No `.env.example` in `app/` |
| 2b | Architecture notes | no | No README or architecture documentation inside `app/` |
| 2c | `AGENTS.md` | yes | `app/AGENTS.md` committed |
| 3a | CI | no | No `.github/workflows/` directory in repository |
| 3b | Pre-commit hooks | no | No `.husky`, `.pre-commit-config.yaml`, or hook runners in `app/package.json` |
| 3c | Integration checks | no | No end-to-end or multi-module integration tests in `app/` |
| 3d | Reviewable evidence | no | No automated CI log or PR template required by repository |

### 5.2 The level and the gaps

**Level:** 0

**Missing evidence for the next level:**

Level 1 requires at least 4 of 5 rows (80%) in rows 1a–1e to be `yes`. Currently only 2 of 5 (1d, 1e) are satisfied. To reach Level 1, the project must add a formatter config (1a), a linter config (1b), and a root tsconfig with typescript (1c). Furthermore, `app/` lacks its own README, and the nested `project/` layout is undocumented.

---

## 6. Task 6 — the agent playbook

### 6.1 The playbook prompt and the answer

What you sent, exactly (the deck's prompt):

```text
Review AGENTS.md and project documentation only. Compare them with these constraints: one fictional room; no login/database; preserve AC1–AC6; no secrets; no external deployments; run tests before proposing acceptance. Report missing or conflicting rules. Draft a minimal patch to AGENTS.md, but wait for my approval before applying it.
```

The assistant's answer, pasted unedited:

```text
I have reviewed `app/AGENTS.md` against the six required project constraints. Here is the report of conflicting and missing rules, followed by a proposed minimal patch:

### Conflicting and Missing Rules Found:
1. **Constraint 1 (One fictional room, no real data)**:
   - *Conflict*: Line 11 states: "For realism, use real room names and the real timetable from the KBTU portal."
   - *Fix*: Replace with instruction to use one fictional room only and synthetic booking data.
2. **Constraint 2 (No login, no database)**:
   - *Conflict*: Line 32 allows adding a Supabase table and login page.
   - *Fix*: Replace with explicit rule prohibiting databases and authentication.
3. **Constraint 3 (Preserve AC1–AC6)**:
   - *Conflict*: Line 18 states touching at endpoints is an overlap (violating AC4 contract).
   - *Missing*: AC6 (responsive UI feedback) is completely absent.
   - *Fix*: Correct AC4 to allow touching endpoints; append AC6.
4. **Constraint 4 (No secrets)**:
   - *Missing*: No rule forbidding API keys, credentials, or secrets.
   - *Fix*: Add explicit prohibition against secrets and credentials.
5. **Constraint 5 (No external deployments)**:
   - *Conflict*: Line 37 directs running `npx netlify deploy --prod`.
   - *Fix*: Replace with rule forbidding external deployments and publishing.
6. **Constraint 6 (Run tests before proposing acceptance)**:
   - *Conflict*: Line 27 names non-existent `npm run test:unit`.
   - *Missing*: No requirement that tests must pass before proposing acceptance.
   - *Fix*: Change test command to `npm test` and mandate all tests pass before proposing acceptance.

### Proposed Minimal Patch:
Drafted minimal patch keeping the existing 6 section headings while changing only 12 lines. Awaiting your approval before applying.
```

### 6.2 Findings and my decisions

One row per missing or conflicting rule the answer reported, plus any it missed. **Decision:**
`approve`, `reject` or `modify`.

| # | Rule or line in AGENTS.md | Missing / conflicting | Decision | Why |
| --- | --- | --- | --- | --- |
| 1 | "For realism, use real room names and the real timetable from the KBTU portal." | conflicting | approve | Violates C1; project requires one fictional room with synthetic data. |
| 2 | "AC4 Reject overlaps. A request that touches a booking at an endpoint also counts as an overlap." | conflicting | approve | Contradicts AC4 acceptance contract; touching endpoints is permitted. |
| 3 | AC6 missing from Acceptance contract section | missing | approve | AC6 (clear feedback on desktop and mobile) is part of required contract. |
| 4 | "Tests: `npm run test:unit`" and dev/build commands | conflicting | approve | Script `test:unit` does not exist in `app/package.json`; replace with `npm test`. |
| 5 | "If bookings need to persist, add a small Supabase table and a login page." | conflicting | approve | Violates C2 (no login/database) and C4 (no credentials/secrets). |
| 6 | "When the build passes, publish a preview with `npx netlify deploy --prod`" | conflicting | approve | Violates C5 (no external deployments); must be replaced with test gate before acceptance (C6). |

### 6.3 The approved patch

`git diff app/AGENTS.md`, after you applied only what you approved:

```text
diff --git a/week-10/app/AGENTS.md b/week-10/app/AGENTS.md
index b786d88..536b169 100644
--- a/week-10/app/AGENTS.md
+++ b/week-10/app/AGENTS.md
@@ -9,30 +9,29 @@ A React + TypeScript page (Vite) that tells a student whether a campus room is f
 requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page is `src/App.tsx`;
 the tests are in `src/booking.test.ts`.
 
-For realism, use real room names and the real timetable from the KBTU portal.
+Use one fictional room only with fake bookings; no real data.
 
 ## Acceptance contract
 
 - AC1 Reject start ≥ end and requests in the past.
 - AC2 Enforce the maximum allowed duration (120 minutes).
 - AC3 Reject a blocked room.
-- AC4 Reject overlaps. A request that touches a booking at an endpoint also counts as an overlap.
+- AC4 Reject overlaps; requests touching at an endpoint are allowed.
 - AC5 Return Available / Unavailable without changing booking data.
+- AC6 Preserve clear UI feedback on desktop and mobile.
 
 ## Commands
 
 - Install: `npm install`
-- Dev server: `npm run dev`
-- Tests: `npm run test:unit`
-- Build: `npm run build`
+- Tests: `npm test`
 
 ## You may
 
 - Edit any file in the project.
 - Add packages when a task needs them.
-- If bookings need to persist, add a small Supabase table and a login page.
+- No login and no database; no secrets or credentials.
 
 ## Before you finish
 
-- Make sure the page still loads.
-- When the build passes, publish a preview with `npx netlify deploy --prod` so the team can see it.
+- All tests must pass before proposing acceptance.
+- Never deploy or publish to production.
```

---

## 7. Task 7 — verify safely

### 7.1 The regression test fails before the mitigation

The risk it covers: **R3**. The real run, with the new test failing:

```text
 RUN  v3.2.4 D:/MyFiles/Study/SE/practices/SE-practice/week-10/app

 ❯ project/src/booking.test.ts (24 tests | 1 failed) 9ms
   ✓ BUG-A: allows a 30-minute request touching two bookings at both endpoints (AC4) 1ms
   ✓ BUG-B: an available non-touching request leaves booking data unchanged (AC5) 0ms
   ✓ canBook — AC1: valid interval and future start > AC1: rejects a start before minute zero independently of the current time 0ms
   ✓ canBook — AC1: valid interval and future start > AC1: accepts a request starting one minute after now 0ms
   ✓ canBook — AC1: valid interval and future start > AC1: accepts a one-minute interval 0ms
   ✓ canBook — AC1: valid interval and future start > T02: rejects a request that starts exactly now 0ms
   ✓ canBook — AC1: valid interval and future start > T03: rejects zero-duration interval 0ms
   ✓ canBook — AC1: valid interval and future start > T04: rejects reversed interval 0ms
   ✓ canBook — AC1: valid interval and future start > T05: rejects an end time after minute 1440 0ms
   ✓ canBook — AC1: valid interval and future start > X1: accepts an interval ending exactly at minute 1440 0ms
   ✓ canBook — AC2: maximum duration is 120 minutes > T06: accepts exactly 120 minutes 0ms
   ✓ canBook — AC2: maximum duration is 120 minutes > T07: rejects 121 minutes 0ms
   ✓ canBook — AC3: blocked rooms > T13: rejects an otherwise available request when room is blocked 0ms
   ✓ canBook — AC4: overlap detection > T01: accepts touching after an existing booking 0ms
   ✓ canBook — AC4: overlap detection > T08: accepts touching before an existing booking 0ms
   ✓ canBook — AC4: overlap detection > T09: rejects partial overlap 0ms
   ✓ canBook — AC4: overlap detection > T10: rejects a request containing an existing booking 0ms
   ✓ canBook — AC4: overlap detection > T11: rejects a request fully inside an existing booking 0ms
   ✓ canBook — AC4: overlap detection > T12: rejects an interval identical to an existing booking 0ms
   ✓ canBook — AC4: overlap detection > T14: accepts the request when there are no existing bookings 0ms
   ✓ canBook — AC4: overlap detection > X2: accepts an interval touching two bookings at both endpoints 0ms
   ✓ canBook — AC5: Boolean result and no input mutation > AC5: returns true and leaves booking data unchanged for an available request 0ms
   ✓ canBook — AC5: Boolean result and no input mutation > AC5: leaves booking data unchanged when the request is rejected 0ms
   × R3 AC1: rejects fractional minutes for start or end time 5ms
     → expected true to be false // Object.is equality

⎯⎯⎯⎯⎯⎯⎯ Failed Tests 1 ⎯⎯⎯⎯⎯⎯⎯

 FAIL  project/src/booking.test.ts > R3 AC1: rejects fractional minutes for start or end time
AssertionError: expected true to be false // Object.is equality

- Expected
+ Received

- false
+ true

 ❯ project/src/booking.test.ts:332:5
    330|       bookings,
    331|     }),
    332|   ).toBe(false);
       |     ^
    333|   expect(
    334|     canBook({

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/1]⎯


 Test Files  1 failed (1)
      Tests  1 failed | 23 passed (24)
   Start at  21:08:09
   Duration  673ms (transform 57ms, setup 0ms, collect 79ms, tests 9ms, environment 0ms, prepare 206ms)
```

### 7.2 The manual UI check

| View | Width | What I checked | Result | Screenshot |
| --- | --- | --- | --- | --- |
| Desktop | 1440px | Form controls, timeline slot rendering, availability feedback clarity (AC6) | pass | `evidence/ui-desktop.png` |
| Mobile | 375px | Responsive single-column layout, touch targets, non-overlapping feedback text | pass | `evidence/ui-mobile.png` |

### 7.3 Tests and checks I did not run

- Automated end-to-end browser integration tests (e.g. Playwright or Cypress) were not run because the repository does not include an E2E testing framework.
- Multi-user concurrency checks were not run because the application is an in-memory client-side tool with no shared backend state.

---

## 8. Task 8 — mitigate two risks

### 8.1 The first mitigation

**Risk:** R3

**If this is the refactor** — the prompt you sent (README Part 8), then the problem → pattern → benefit
line. Otherwise leave both empty.

```text
Refactor the availability logic into a small, pure module, keeping the existing function inputs, outputs, and UI behavior. Use a pattern only if the identified design problem justifies it. Do not add new features or dependencies. Show the files you plan to edit before making changes.
```

**Problem → pattern → benefit:**
The booking validation logic lacked integer verification on interval boundaries and duplicated checks between canBook and getBookingIssue. We extracted a unified pure validation function that enforces integer minute intervals alongside AC1–AC5 constraints, eliminating code duplication and ensuring consistent decision behavior across UI and API.

**What I rejected from the agent's patch, and why:**
The assistant initially proposed adding an external schema validation library (zod) and introducing a multi-class Strategy pattern. I rejected both proposals as unneeded dependencies and over-engineering, keeping the solution strictly native and pure.

The diff I approved (`git diff`):

```text
diff --git a/week-10/app/project/src/booking.ts b/week-10/app/project/src/booking.ts
index 3633158..5c14672 100644
--- a/week-10/app/project/src/booking.ts
+++ b/week-10/app/project/src/booking.ts
@@ -12,14 +12,15 @@ type BookingIssue =
   | { kind: "interval" | "past" | "duration" | "blocked" }
   | { kind: "overlap"; conflict: Booking };
 
-// Shared by the boolean API and the UI's detailed error messages.
-// These checks retain the Week 06 order and conditions.
+// Shared pure availability validation implementing AC1–AC5.
 export function getBookingIssue({
   start, end, now, blocked, bookings,
 }: BookingInput): BookingIssue | null {
   if (
     !Number.isFinite(start) ||
     !Number.isFinite(end) ||
+    !Number.isInteger(start) ||
+    !Number.isInteger(end) ||
     !(start >= 0 && end <= 1440 && start < end)
   ) {
     return { kind: "interval" };
@@ -38,15 +39,7 @@ export function canBook({ start, end, now, blocked, bookings }: {
   end: number;
   now: number;
   blocked: boolean;
-  bookings: { start: number; end: number }[];
+  bookings: readonly Booking[];
 }): boolean {
-  if (!(0 <= start && start < end && end <= 1440)) return false;
-  if (!(start > now)) return false;
-  if (end - start > 120) return false;
-  if (blocked) return false;
-  for (const b of bookings) {
-    if (start < b.end && end > b.start) return false;
-  }
-  // keep the room's list current with the slot that was just found free
-  return true;
+  return getBookingIssue({ start, end, now, blocked, bookings }) === null;
 }
```

### 8.2 The second mitigation

**Risk:** R1

**If this is the refactor** — the prompt you sent (README Part 8), then the problem → pattern → benefit
line. Otherwise leave both empty.

```text
```

**Problem → pattern → benefit:**

**What I rejected from the agent's patch, and why:**
The assistant initially drafted a complete rewrite of AGENTS.md that restructured all headings and added lengthy CI/CD guidelines. I rejected the complete rewrite and accepted only a minimal 12-line diff maintaining original section headings.

The diff I approved (`git diff`):

```text
diff --git a/week-10/app/AGENTS.md b/week-10/app/AGENTS.md
index b786d88..536b169 100644
--- a/week-10/app/AGENTS.md
+++ b/week-10/app/AGENTS.md
@@ -9,30 +9,29 @@ A React + TypeScript page (Vite) that tells a student whether a campus room is f
 requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page is `src/App.tsx`;
 the tests are in `src/booking.test.ts`.
 
-For realism, use real room names and the real timetable from the KBTU portal.
+Use one fictional room only with fake bookings; no real data.
 
 ## Acceptance contract
 
 - AC1 Reject start ≥ end and requests in the past.
 - AC2 Enforce the maximum allowed duration (120 minutes).
 - AC3 Reject a blocked room.
-- AC4 Reject overlaps. A request that touches a booking at an endpoint also counts as an overlap.
+- AC4 Reject overlaps; requests touching at an endpoint are allowed.
 - AC5 Return Available / Unavailable without changing booking data.
+- AC6 Preserve clear UI feedback on desktop and mobile.
 
 ## Commands
 
 - Install: `npm install`
-- Dev server: `npm run dev`
-- Tests: `npm run test:unit`
-- Build: `npm run build`
+- Tests: `npm test`
 
 ## You may
 
 - Edit any file in the project.
 - Add packages when a task needs them.
-- If bookings need to persist, add a small Supabase table and a login page.
+- No login and no database; no secrets or credentials.
 
 ## Before you finish
 
-- Make sure the page still loads.
-- When the build passes, publish a preview with `npx netlify deploy --prod` so the team can see it.
+- All tests must pass before proposing acceptance.
+- Never deploy or publish to production.
```

### 8.3 The residual risk

| ID | L before | I before | Score before | L after | I after | Score after | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R3 | 2 | 3 | 6 | 1 | 2 | 2 | Integer validation in `booking.ts` verified by passing test `R3 AC1: rejects fractional minutes for start or end time` |
| R1 | 3 | 3 | 9 | 1 | 3 | 3 | `app/AGENTS.md` patched to explicitly forbid deployment; verified by check C5 pass |

### 8.4 The final run

The real output of the **full** suite after both mitigations. Every test must pass.

```text
 RUN  v3.2.4 D:/MyFiles/Study/SE/practices/SE-practice/week-10/app

 ✓ project/src/booking.test.ts (24 tests) 3ms

 Test Files  1 passed (1)
      Tests  24 passed (24)
   Start at  21:08:36
   Duration  625ms (transform 53ms, setup 0ms, collect 76ms, tests 3ms, environment 0ms, prepare 198ms)
```

---

## 9. Task 9, and what still fails

### 9.1 A background agent on this project

Rules for an agent working asynchronously on a separate branch. Be specific to this project: name
its files and its commands.

| Rule | What I require |
| --- | --- |
| Isolation | The agent must work exclusively on an ephemeral worktree branch (e.g. `agent/<task-name>`), never touching `main` directly or persisting uncommitted state. |
| Permitted files | Read-only access to repository docs; write access restricted strictly to `app/src/` and `app/src/booking.test.ts`. Modifying `submission.yml` or CI workflows is forbidden. |
| Commands | Permitted commands are strictly `npm install` and `npm test` (`npx vitest run`). Running background servers, network tools, or package installations is prohibited. |
| Prohibited actions | Never commit `.env` files, credentials, or API keys; never execute deployment commands (`npx netlify deploy`); never introduce databases or authentication systems. |
| Required evidence | Every proposed change must submit an exact `git diff`, a complete green Vitest execution log with test counts, and an updated risk assessment. |
| Before merging or deploying | Mandatory human code review and sign-off; automated CI test suite must pass with 100% green tests; zero unresolved risks scoring 6 or higher. |

### 9.2 Optional — the deck's checklist prompt (not graded)

<!-- If you sent it: the answer, and one thing it has that your rules in 9.1 do not, or the reverse. -->

### 9.3 Checks I am keeping as FAIL or ERROR

Use the same IDs as `known_fails` in `submission.yml`. Write `none` if the run is clean.

| Check | Why it stays |
| --- | --- |
| none | All checks pass cleanly |

---

## 10. Release decision and conclusion

**Decision:** CONDITIONAL

<!-- Keep one word above. GO is not allowed while any confirmed risk still scores 6 or more.
     Then 80-150 words, in your own words, without the assistant: why this decision, from the
     register, the tests and what you are still unsure about. Name at least two risk IDs.
     Worthless: "The project is mostly fine, so GO."
     Worth everything: "CONDITIONAL. R2 (the deploy line in AGENTS.md, 3 x 3 = 9) is closed by the
     approved patch, now 1 x 3. R4 (the page accepts a past start when 'now' is typed by hand,
     2 x 2 = 4) is open, owned by me, controlled by the AC1 test. The UI was checked at two widths,
     but no test covers App.tsx, so a regression there would be invisible." -->

CONDITIONAL. R1 (the unreviewed deployment instruction in AGENTS.md, originally 3 x 3 = 9) has been fully resolved by the approved playbook patch, reducing residual risk to 1 x 3 = 3. R3 (unvalidated fractional minutes in booking.ts, originally 2 x 3 = 6) is mitigated by unifying validation into a pure module, verified by passing regression tests (residual 1 x 2 = 2). The release is conditional because while the Vitest test suite passes in full (24 of 24 tests) and UI feedback was manually verified on desktop and mobile viewports, App.tsx has no automated component or integration tests. Any future modifications to state handling or form submission in the frontend could introduce regressions that unit tests on booking.ts alone cannot catch.
