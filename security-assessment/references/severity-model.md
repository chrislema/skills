# Severity model — likelihood × impact, likelihood dominates

The single most common failure of security reports is ranking by impact
alone. It produces reports where "attacker with root can do bad things"
sits above "anyone on the internet can log in as anyone", and readers
learn to ignore the whole document. This model exists to prevent that.

## Scoring

Score each CONFIRMED finding on both axes, then apply the caps.

### Likelihood (how plausible is the bad event, really)

Start from the strongest applicable row:

| L | Condition |
|---|---|
| L4 | Unauthenticated + network-reachable + well-known exploit pattern (SQLi on a public form, exposed admin panel, secret in a public repo, auth bypass via crafted request) |
| L3 | Requires only a normal user account, or modest effort/knowledge (IDOR behind login, CSRF on a state-changing route, XSS needing one victim click) |
| L2 | Requires unusual circumstances: a specific misconfiguration also being present, MITM position on the network, social engineering, or race timing |
| L1 | Requires an already-privileged actor (admin, root, DB access, deploy access) or physical access |

### Impact (what the event costs if it happens)

| I | Condition |
|---|---|
| I4 | Full account takeover at scale, all-user data breach, remote code execution, destruction of data without recovery |
| I3 | Single-account takeover, exposure of sensitive data for some users, privilege escalation to admin |
| I2 | Exposure of non-sensitive data, degraded integrity (spoofed content, unauthorized non-destructive writes), denial of service |
| I1 | Information leakage useful only for reconnaissance (versions, paths, stack traces), hygiene issues |

### Priority

| | I4 | I3 | I2 | I1 |
|---|---|---|---|---|
| **L4** | P0 | P0 | P1 | P2 |
| **L3** | P0 | P1 | P2 | P3 |
| **L2** | P1 | P2 | P3 | P4 |
| **L1** | P3 | P3 | P4 | P4 |

### The privilege cap (non-negotiable)

If exploiting the finding **requires** an actor who already holds the
privileges the exploit would grant or exceed, the finding caps at **P3**
regardless of impact. "An admin with root access could delete everything"
is L1 and capped: it is a blast-radius/least-privilege recommendation,
not an emergency. Put such items in the report's "hardening notes"
section, clearly separated from the ranked findings.

The cap does NOT apply when the privileged role is itself easily reached
(default admin password, admin signup open) — score the chain as one
finding at the likelihood of its weakest link.

## Chains

Attackers chain findings. Score chains explicitly when two LIKELY/
CONFIRMED findings compose into something worse (e.g. XSS [L3/I2] +
session cookie missing HttpOnly [hygiene] = session theft [L3/I3 → P1]).
Write the chain as its own finding referencing its components, and rank
the components at their standalone score.

## Calibration examples

| Finding | Score | Why |
|---|---|---|
| Login form posts over HTTP in production | L3×I3 = P1 | Needs network position OR any shared network; credential capture |
| Hardcoded `admin/admin123` accepted in prod code path | L4×I3 = P0 | Anyone who reads the bundle or guesses; full admin |
| Debug bypass `?auth=skip` left in a route | L4×I3 = P0 | Reachable, trivial, total |
| SQLi in an admin-only report page | L3×I4 = P0 | Only needs a normal admin login? If admin accounts are few and trusted, argue L2×I4 = P1 — write the argument down |
| `is_admin` accepted via mass assignment on profile update | L3×I3 = P1 | Any user, self-escalation |
| Stack traces shown to users | L4×I1 = P2 | Certain to occur, recon value only |
| Root DB user could DROP TABLE | L1, capped | Hardening note, not a ranked finding |
| JWT secret is `"secret"` | L4×I4 = P0 | Forgeable tokens for anyone |
| CORS `*` on a read-only public API | L2×I1 = P4 | Probably intended; confirm intent, note it |

## Report discipline

- Every ranked finding shows its L, I, and any cap applied, with one
  sentence justifying the L score. The L sentence is where honesty lives.
- If you argue a score up or down from the table, the argument appears in
  the finding. Silent adjustment is forbidden.
- The "hardening notes" section (capped and theoretical items) is welcome
  and useful — it just never mixes with the ranked list.
