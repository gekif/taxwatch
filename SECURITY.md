# Security notes

## Implemented
- Passwords hashed with PBKDF2-HMAC-SHA256 (200k iterations, per-user salt); constant-time comparison.
- JWT (HS256) with expiry; inactive users are rejected even with a valid token.
- Role-based authorization enforced server-side on every endpoint (never only in the UI).
- Input validation with Pydantic (formats, ranges, enums); SQL injection prevented by the ORM.
- Production refuses to start with a default or short `SECRET_KEY`.
- Login uses a dummy hash check for unknown users to reduce user-enumeration timing differences.
- Soft deletes and an audit trail preserve evidence.

## Known limitations (documented trade-offs)
- The frontend stores the token in `sessionStorage` for simplicity; production should use
  httpOnly, SameSite cookies with CSRF protection.
- No login rate limiting / lockout, refresh tokens, or MFA.
- No HTTPS termination in this repo: put it behind a TLS-terminating proxy.
- Demo seed credentials are public; never run `python -m app.seed` against production.

## Reporting
Open a private security advisory on the repository.
