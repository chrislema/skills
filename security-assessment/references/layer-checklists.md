# Layer checklists — what each sweep sub-agent actually checks

Each Phase 2 sub-agent takes one layer, works its full list, and reports
BOTH hits and clean checks. "Checked, clean" lines make the final report
trustworthy; a report that only lists hits reads as a partial sweep.

For every hit: file:line, the evidence as quoted code, and the *intended*
behavior it violates. No speculative language — if you can't point at
code or config, it isn't a candidate finding, it's a question for the
user.

## 1. Transport & headers

- [ ] Any form that submits credentials reachable over plain HTTP; no
      server-side redirect to HTTPS; no HSTS in production config.
- [ ] Session cookies: `Secure`, `HttpOnly`, `SameSite` (Lax minimum on
      session cookies; None only with justification).
- [ ] Mixed content: HTTPS pages loading scripts/iframes over HTTP.
- [ ] CSP absent where the app renders user content (weight this with the
      XSS sweep — CSP is the seatbelt, not the fix).
- [ ] TLS config where visible (reverse-proxy/config files): ancient
      protocol versions explicitly enabled.

## 2. Authentication

- [ ] **Backdoors**: grep for auth short-circuits — `NODE_ENV`-gated
      bypasses that also run in prod, magic query params/headers
      (`?debug`, `X-Skip-Auth`), hardcoded user allowlists
      (`if (email === "dev@...")`), commented-out middleware, TODO/FIXME
      near auth code.
- [ ] **Credentials in code**: hardcoded passwords, API keys, default
      accounts seeded by migrations/fixtures that ship to prod.
- [ ] **Password storage**: plaintext, reversible encryption, unsalted or
      fast hashes (MD5/SHA-family). Acceptable: bcrypt/scrypt/argon2 with
      sane cost. Check the actual write path, not just the library import.
- [ ] **Password policy**: minimum length under 8, no check against
      common-password lists where the framework offers one, silent
      truncation.
- [ ] **Login hardening**: rate limiting/lockout on the login route,
      user-enumeration via distinct error messages or timing
      ("no such user" vs "wrong password").
- [ ] **Sessions**: ID rotated on login (fixation), invalidated
      server-side on logout, sane expiry, session data not in
      client-readable storage.
- [ ] **JWT (if used)**: algorithm pinned (reject `none`/`alg` from
      token), secret strength and storage, expiry present and enforced,
      signature actually verified on every protected route (not just
      decoded), revocation story for logout/password-change.
- [ ] **Reset flow**: token entropy (not sequential/guessable), expiry,
      single-use, no user enumeration, old sessions invalidated after
      reset.
- [ ] **OAuth (if used)**: `state` parameter used and verified, redirect
      URI validated against an allowlist, tokens not logged.

## 3. Authorization

- [ ] **IDOR**: every route taking an object ID from path/query/body —
      does the handler verify the object belongs to (or is visible to)
      the requesting user? Sample systematically: list all such routes
      from the Phase 0 attack-surface inventory and check each.
- [ ] **Vertical**: admin routes actually behind an admin check
      (middleware order matters — check the check runs *before* the
      handler); role checks compare against roles the auth layer really
      issues.
- [ ] **Client-trusted identity**: any handler reading `user_id`, `role`,
      `is_admin`, `price`, `quota` from the request body instead of the
      server-side session.
- [ ] **Mass assignment**: create/update handlers spreading the whole
      request body into the model (`Model.update(req.body)`) where the
      model has privileged columns.
- [ ] **UI-only enforcement**: buttons hidden for non-admins whose
      underlying API works fine for anyone (cross-check with the
      traceability route inventory if available).
- [ ] **Multi-tenancy (if applicable)**: tenant ID scoping on every
      query, not just top-level routes.

## 4. Input handling

- [ ] **SQL/NoSQL injection**: string-concatenated/template-literal
      queries with user input; ORM raw-query escape hatches; NoSQL
      operator injection (`{"$gt": ""}` reaching Mongo queries).
- [ ] **XSS**: unescaped template output (`|safe`, `{{{ }}}`,
      `dangerouslySetInnerHTML`, `v-html`, `innerHTML =`), user content
      in attributes/URLs (`javascript:`), stored content rendered
      elsewhere, JSON embedded in HTML without escaping.
- [ ] **CSRF**: state-changing routes (POST/PUT/DELETE) without CSRF
      token verification AND without SameSite protection; GET routes
      that mutate state (doubly bad).
- [ ] **SSRF**: server-side fetch of user-supplied URLs (webhooks, image
      proxies, importers) without scheme/host validation; access to
      cloud metadata endpoints.
- [ ] **Path traversal**: user input joined into filesystem paths
      (download endpoints, template selection) without normalization
      checks.
- [ ] **Uploads**: type validated server-side (content, not extension or
      client MIME), size limits, stored outside web root or with
      execution disabled, filenames sanitized (traversal via filename),
      SVG uploads treated as active content.
- [ ] **Command injection**: user input reaching `exec`/`spawn(shell)`/
      backticks/`os.system`.
- [ ] **Redirects**: open redirect via user-supplied `next`/`return_to`
      URLs.
- [ ] **Deserialization**: untrusted input into pickle/`unserialize`/
      YAML-unsafe loaders.

## 5. Data exposure

- [ ] **Secrets in repo**: grep working tree AND git history for keys,
      tokens, passwords, connection strings (`git log -p` sampling,
      obvious filenames: `.env` committed, `config.prod.*`). Anything in
      history that was ever real must be flagged for rotation, not just
      removal.
- [ ] **Secrets in client bundle**: server-only keys reachable in
      shipped JS; env vars with public prefixes (`NEXT_PUBLIC_`,
      `VITE_`) holding private values.
- [ ] **Over-fetching APIs**: serializers returning password hashes,
      tokens, internal flags, other users' fields; `SELECT *` piped to
      JSON.
- [ ] **Logs**: passwords, tokens, full request bodies of auth routes,
      PII logged at info level.
- [ ] **Errors**: stack traces / SQL errors / framework debug pages
      reaching clients in prod config.
- [ ] **Stray files**: `.git/` served, backup files (`*.bak`, `*.sql`),
      editor droppings in web root, source maps exposing server code.

## 6. Configuration

- [ ] **CORS**: `Access-Control-Allow-Origin: *` combined with
      credentials; origin reflection without validation.
- [ ] **Debug mode**: framework debug flags on in production config
      (`DEBUG=True`, `APP_DEBUG=true`, dev error handlers).
- [ ] **Exposed operational endpoints**: `/admin` without auth,
      `/metrics`, `/health` leaking internals, framework consoles,
      GraphQL introspection + playground in prod.
- [ ] **Dependencies**: run the ecosystem audit tool; report ONLY
      criticals/highs with known exploits relevant to how the dependency
      is used. A 400-line vulnerability dump is noise, not a finding.
- [ ] **Security headers**: `X-Content-Type-Options`, `X-Frame-Options`/
      `frame-ancestors`, `Referrer-Policy` — batch these as one hygiene
      finding, not six.
- [ ] **Default ports/creds on infra in repo**: docker-compose exposing
      DB ports publicly, default DB passwords in compose files that
      mirror prod.
