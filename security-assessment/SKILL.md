---
name: security-assessment
description: "Defensive security audit of a web application, layer by layer: transport (login over non-HTTPS, cookie flags), authentication (backdoors and debug bypasses left open, hardcoded or default credentials, weak password policy, session/JWT handling), authorization (IDOR, missing ownership checks, privilege escalation), input handling (SQL injection, XSS, CSRF, SSRF, path traversal, uploads), data exposure (secrets in the repo, PII in logs, over-fetching APIs, verbose errors), and configuration (open CORS, debug mode on, exposed admin routes). Ranks findings by likelihood × impact so a wide-open unauthenticated hole outranks a theoretical root-only attack — 'an admin with root access could delete everything' is not a five-alarm fire. Use for a security review, security audit, pre-launch hardening pass, 'is this app safe', or after AI agents have built features fast and nobody has checked the doors. Builds a test baseline first, then outputs prioritized, Sonnet-executable work orders where every fix carries proof the hole is closed AND the legitimate path still works."
---

# Security Assessment — check every door, rank by real risk

Codebases built fast — especially by multiple AI agents — accumulate open
doors: a debug login left in, an endpoint that trusts the client's user ID, a
secret committed "temporarily", CORS opened wide to make an error go away.
None of these announce themselves. This skill walks every layer of a web
application looking for the common, high-frequency classes of security
failure, and ranks what it finds by **how likely the bad event actually is**,
not just how bad it sounds.

**Prime directive: severity = likelihood × impact, and likelihood dominates
the ordering.** An unauthenticated, network-reachable hole with a public
exploit pattern is a P0 even if the data behind it is modest. A devastating
action that requires an already-root attacker is a P3 — an admin with root
being able to delete everything is not a five-alarm fire; it is a note about
blast-radius reduction. The full scoring rubric is in
`references/severity-model.md`. Apply it to every finding; never rank on
impact alone, and never pad the report with theoretical findings dressed as
urgent ones. A security report that cries wolf gets ignored, and then the
real P0 ships.

**Second directive: this is a defensive audit of an application the user
owns or is authorized to assess.** Findings include enough evidence to
confirm and fix the hole — not weaponized exploit tooling. Reproductions
stay minimal and local (a curl that shows the missing check, not a script
that dumps the table).

The output is not just findings — it is (1) a baseline test harness, (2) a
severity-ranked report, and (3) work orders precise enough for a
Sonnet-class model to fix each hole and **prove both directions**: the
attack path is closed and the legitimate path still works. Read
`references/work-orders.md` before writing output.

## Phase 0 — Recon

- **Stack and trust map**: frameworks, auth mechanism (sessions? JWT? which
  library?), storage engines, how secrets are supposed to be managed, what
  runs where (server, edge, client), and every trust boundary — each place
  data crosses from less-trusted to more-trusted (browser→server,
  server→DB, third-party webhooks→server, env→code).
- **Attack-surface inventory**: every route with its auth requirement as
  *intended* (from middleware/docs) — this becomes the checklist for
  authorization testing. Every form and file-upload. Every place user input
  reaches a query, a shell, a file path, a template, or an outbound request.
- **Run state**: can the app run locally? Several checks (session behavior,
  header inspection, actual TLS/redirect config) need a running app; where
  it can't run, mark those checks STATIC-ONLY in the report.

## Phase 1 — Baseline harness

Security fixes are behavior changes near the most sensitive code in the app.
The executor must not be able to break login while fixing login.

1. Inventory and run existing tests; record exact pass/fail as the baseline.
2. Build characterization tests for every **legitimate path through
   sensitive code**: successful login, successful logout, an authorized
   user reading their own data, an admin doing an admin thing, a valid
   upload. These are the tests that prove fixes didn't lock the front door.
3. For each finding that survives verification (Phase 3), add a **negative
   test**: a test that currently FAILS because the hole is open (e.g.
   "request with no session gets 401" — currently it gets 200). Tag these
   `HOLE-OPEN-BASELINE`. The matching work order flips them green.
4. Record the green list, the red `HOLE-OPEN-BASELINE` list, and exact
   commands.

## Phase 2 — Layer sweeps (fan out)

Spawn one sub-agent per layer below. Each works from the full checklist in
`references/layer-checklists.md` and reports candidate findings with
file:line evidence. Layers, in the order an attacker meets them:

1. **Transport & headers** — login/credential forms reachable over HTTP,
   missing HTTPS redirect/HSTS, cookies without `Secure`/`HttpOnly`/
   `SameSite`, missing CSP where XSS risk exists, mixed content.
2. **Authentication** — backdoors and debug bypasses (`if user == "test"`,
   magic query params, commented-out auth), hardcoded/default credentials,
   password policy and storage (plaintext? unsalted MD5/SHA1? bcrypt with
   sane cost?), rate limiting on login, session fixation/rotation, JWT
   pitfalls (`alg:none`, weak/hardcoded secret, no expiry, unverified
   claims), password reset flow (token entropy, expiry, single-use).
3. **Authorization** — IDOR (object IDs from the client used without
   ownership checks), missing role checks on admin routes, trusting
   client-supplied role/user_id fields, mass assignment reaching
   privileged columns (`is_admin`), authz checked in UI but not API.
4. **Input handling** — SQL/NoSQL injection (string-built queries), XSS
   (unescaped output, `dangerouslySetInnerHTML`, `v-html`), CSRF (state-
   changing routes without token/SameSite defense), SSRF (user URLs
   fetched server-side), path traversal, upload validation (type, size,
   storage location, execution risk), command injection.
5. **Data exposure** — secrets/keys committed in the repo or client bundle
   (grep history too, not just HEAD), PII/credentials in logs, API
   responses over-fetching (password hashes or internal fields serialized
   out), verbose stack traces to clients, backup/config files reachable.
6. **Configuration** — `CORS: *` with credentials, debug mode in prod
   config, exposed admin/metrics/console endpoints, directory listing,
   dependency audit (`npm audit` or equivalent — report criticals with
   known exploits, don't dump the whole list), missing security headers.

Each sub-agent must report **what it checked and found clean**, not only
hits — the report's value includes the clean sweep.

## Phase 3 — Adversarial verification

False positives in a security report destroy its credibility, and false
fixes break production auth. For each candidate finding, a verifier must:

1. Re-read the cited code in full context — is there a mitigating layer the
   sweep missed (framework auto-escaping, ORM parameterization, a
   middleware applied globally rather than per-route)?
2. Confirm reachability: is the vulnerable code actually wired to a route
   an attacker can reach? Dead vulnerable code is a P4 cleanup note, not a
   finding.
3. Where the app runs, reproduce minimally (one request demonstrating the
   missing check). Record the request and response in the finding.
4. Score it against `references/severity-model.md` — likelihood factors ×
   impact factors, with the privilege-required cap applied.
5. Mark CONFIRMED or LIKELY. Only CONFIRMED findings become work orders.

## Phase 4 — Output

Per formats in `references/work-orders.md`:

1. **`security-report.md`** — the trust map, what was swept and found
   clean, findings ranked strictly by the severity model (each with score
   breakdown, evidence, minimal reproduction), STATIC-ONLY caveats, and a
   short "not findings" section for the theoretical/root-required items so
   they're recorded without inflating the ranking.
2. **`work-orders.md`** — Sonnet-executable orders in severity order. Every
   order carries two-directional verification: the `HOLE-OPEN-BASELINE`
   test flips green (hole closed) AND the legitimate-path tests stay green
   (door still opens for the right people). A security fix that isn't
   provable both ways is not done.
