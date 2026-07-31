# Output formats — the report and the work orders

Two markdown files: `security-report.md` for humans, `work-orders.md` for
a Sonnet-class executing model. Both are required.

## Why work orders are written this way

The executor is competent but literal, and here it is editing the most
sensitive code in the application. Every order is **self-contained**,
**bounded** (explicit do-not-touch list), and **two-directionally
verifiable**: it must prove the hole is closed AND that legitimate users
still get through. A security fix that locks out real users is a
production incident wearing a virtue costume. If you cannot write both
verification directions, the finding stays in the report and does not
become a work order.

## `security-report.md` structure

1. **Summary** — counts by priority, the top 3 in one sentence each.
2. **Trust map** — the boundaries identified in Phase 0.
3. **Baseline harness** — what was built, exact commands, green list,
   and the `HOLE-OPEN-BASELINE` red list.
4. **Ranked findings** — strictly in severity order. Each: ID (S-nn),
   priority with L×I breakdown and one-sentence likelihood
   justification, evidence (file:line, quoted code), minimal
   reproduction (the single request that demonstrates it), and the fix
   direction in one sentence.
5. **Hardening notes** — privilege-capped and theoretical items,
   clearly separated. This is where "admin with root can delete
   everything" lives.
6. **Clean sweeps** — what was checked and found fine, by layer. This
   section is what makes the report trustworthy.
7. **STATIC-ONLY caveats** — checks that need a running app and didn't
   get one.
8. **Rotation list** — any secret ever committed to history, flagged
   for rotation regardless of whether it was removed. Removal from code
   does not un-leak a key.

## `work-orders.md` structure

Header block:

```markdown
# Work Orders — Security
Baseline command: <exact command>
Baseline state: <N green; HOLE-OPEN-BASELINE tests listed by name — these
are EXPECTED to fail before their order is executed and pass after>
Global rules for the executor:
- Execute in listed order. One order = one commit.
- Run the baseline after EVERY order. Required after each order: all
  legitimate-path tests green + this order's HOLE-OPEN test(s) flipped
  green + no other changes. Anything else: STOP and revert.
- Touch only the listed files. If the fix seems to need another file,
  STOP and report back.
- Never widen a fix ("while I'm here I'll also sanitize...") — adjacent
  issues have their own orders or belong in a report, not in this diff.
- Never commit secrets, even in tests. Test credentials come from env
  or fixtures marked fake.
```

Then each order:

```markdown
## WO-01 [P0] Remove debug auth bypass on /api/*
**Finding:** S-02 (CONFIRMED, L4×I3)
**Problem:** `middleware/auth.js:23-26` skips all verification when the
request carries `?auth=skip`. Reachable in production; grants any role.
**Change:** Delete lines 23–26 (`if (req.query.auth === 'skip') return
next();`). Nothing replaces them — the following verification logic is
the intended path.
**Do not touch:** the rest of `middleware/auth.js`, any route files, the
frontend dev-tools that used this bypass (`js/devlogin.js` — it will now
fail, which is correct; see report S-02 note to user).
**Verify (hole closed):** `npm test -- --grep "S-02"` — the
HOLE-OPEN-BASELINE test "GET /api/me?auth=skip without session returns
401" now passes.
**Verify (door still opens):** full baseline — every legitimate-path
test (login, authorized reads, admin actions) still green.
**Expected test changes:** exactly the S-02 test flipping red→green.
```

Field notes:

- **Order of orders**: strict severity order (P0 first), except where a
  later order depends on an earlier one — say so explicitly when it does.
- **Minimal fixes over rewrites.** The order specifies the smallest
  change that closes the hole using the framework's intended mechanism
  (parameterized query, the framework's CSRF middleware, the
  serializer's field allowlist). Executors must never hand-roll crypto,
  sanitizers, or session logic — if the right fix is "adopt the
  framework mechanism", the order names the exact mechanism and shows
  the target call shape.
- **Human-decision escalations**: some findings need the user, not the
  executor — rotating leaked keys, choosing a password-policy stance,
  removing a backdoor a team may knowingly rely on. Write these as
  orders addressed to the user, clearly marked `[HUMAN]`, with the
  decision framed and a recommendation. Never have the executor guess.
- **Grouped hygiene**: header-type fixes may batch into one order with
  every site enumerated. Never "and anywhere else".
- **Behavior-change warnings**: when a fix intentionally changes visible
  behavior (rate limiting kicks in, CORS narrows, an old bypass used by
  a dev tool dies), the order must name who/what will notice, so the
  user isn't surprised.
