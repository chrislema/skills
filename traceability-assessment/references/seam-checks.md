# Seam checks — extraction specs and the full mismatch checklist

This file backs Phases 2 and 3 of the traceability assessment. Phase 2
sub-agents use the extraction specs; Phase 3 uses the mismatch checklist.

## Extraction specs per tier

Record everything **as written in the code** — no normalization, no
correction, no "obviously they meant". The audit's value is in faithful
strings.

### UI templates / components
- Every `href` (internal only), form `action` + `method`, button/element
  with a click handler, and the handler function it invokes.
- For each form: field `name` attributes, in DOM order.
- Framework routing: `<Link to=...>`, `router.push(...)`, named-route
  helpers and the params they pass.

### Client-side JS
- Every `fetch`/`axios`/XHR call: URL (literal or template), HTTP method,
  body keys as written, query params, headers that matter (auth,
  content-type).
- What the caller does with the response: destructured keys, accessed
  fields, error handling branches.

### Route definitions
- Path pattern (with param names as declared: `/users/:userId`), HTTP
  method, middleware chain in order, handler reference.

### Auth / authz middleware
- What each middleware attaches to the request (e.g. `req.user`,
  `ctx.session.uid`) and the exact property names.
- Role/permission names as string literals, wherever they are checked.

### Handlers / controllers
- Parameters read from the request: path params, query params, body keys —
  exact names.
- Calls into services/business layer: function name, arguments in order.
- Response construction: status codes, exact keys of the response object,
  which service-result fields are included vs dropped.

### Services / business logic
- Public function signatures: name, parameters in order with names,
  return shape.
- Calls into models/data access: same detail.

### Models / data access
- Model/entity field names and their mapped column names (watch for
  explicit alias config — it reconciles apparent mismatches).
- Every query: raw SQL strings, ORM query-builder chains, the columns and
  placeholders they reference.

### Storage schema
- Source of truth order: migrations > schema files > live introspection
  (if the app runs, introspect and diff against migrations — schema drift
  between environments is itself a finding).
- Tables/collections, columns with types and nullability, constraints,
  indexes, foreign keys.

## The mismatch checklist (Phase 3)

Work every seam, both directions. For each item: what to look for, and the
classic way it produces a false positive (check before reporting).

1. **Identifier drift** — same concept, different name across a seam
   (`emp_ID` / `empID` / `employeeId`; `created_at` / `createdAt`).
   *False-positive check*: serializer or DTO layer that renames in transit;
   ORM naming-strategy config (snake_case ↔ camelCase auto-mapping).
2. **JSON key mismatch** — client sends `{ userId }`, server reads
   `req.body.user_id`. *FP check*: body-parsing middleware that
   case-normalizes (rare, but exists).
3. **Arity mismatch** — call passes N args, signature declares M. In JS
   this is silent. *FP check*: rest params, `arguments` usage, optional
   params genuinely intended to be omitted.
4. **Positional swap** — adjacent parameters of the same type passed in
   the wrong order (`transfer(toId, fromId)`). Detect by comparing caller
   variable names against callee parameter names. *FP check*: caller
   variable names may be legitimately different words for the same value.
5. **Type drift** — string route param compared with `===` against integer
   column value; date strings vs Date objects; `"true"` vs `true`.
   *FP check*: explicit casts/coercion near the seam; loose-equality use.
6. **Nullability assumption** — caller dereferences a field the schema
   allows to be NULL; optional chaining that silently swallows a missing
   required value.
7. **Query-to-schema** — column named in SQL/ORM doesn't exist; parameter
   placeholder count ≠ bound values; SELECTed columns vs fields read from
   the row. *FP check*: views, generated columns, migrations not yet in
   the schema file you read.
8. **Enum / literal drift** — status strings compared across tiers
   (`"active"` vs `"ACTIVE"`), role names in authz checks vs role names
   the auth layer actually issues.
9. **Route param drift** — route declares `:id`, handler reads
   `req.params.userId`.
10. **Method mismatch** — client POSTs, route is defined for PUT; form
    method vs route method.
11. **Orphaned endpoint** — route with no caller anywhere in the UI or
    client JS. *FP check*: external/API consumers, webhooks, cron/queue
    triggers, mobile clients — grep the docs and note the possibility
    before flagging as dead.
12. **Phantom call** — UI calls a URL no route serves. Guaranteed
    finding; confirm exact path matching including trailing slashes and
    base-path prefixes.
13. **Return-trip loss** — handler drops fields the client destructures;
    serializer excludes a field the UI binds; the UI renders
    `undefined` somewhere a value should be. Trace *up* as carefully as
    down.
14. **Auth continuity gap** — route in a protected group registered
    outside the middleware chain; handler that assumes `req.user` on a
    route where no middleware sets it.
15. **Error-path drift** — server error shape (`{ error: msg }` vs
    `{ message }` vs bare string) doesn't match what the client error
    handler reads, so failures are invisible to users.

## Trace matrix row format

| Trace ID | Entry point (file:line) | Interaction | Path (tier → tier …) | Verdict | Finding refs |
|---|---|---|---|---|---|
| T-014 | `views/staff.html:88` | "Save" button | UI → js/staff.js → POST /api/employees/:id → auth → employeeController.update → EmployeeService.save → Employee model → `employees` table → response → UI toast | DRIFT | F-07 |

Verdicts: CLEAN, DRIFT, BROKEN, UNTRACEABLE. Every entry point from the
Phase 0 inventory must appear exactly once.
