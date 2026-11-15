# Security

- Secrets are loaded from environment variables; `.env` is excluded from Git. Production startup rejects the development JWT key and requires at least 32 characters.
- Passwords are hashed with Argon2 through `pwdlib`; raw passwords are never stored. Bootstrap credentials are supplied interactively through an operator-controlled command, never committed.
- JWTs are signed with HS256, have a bounded expiration, and are validated on protected routes. The user must remain active, and role checks use the current database role.
- Customer and order inputs are constrained with Pydantic. SQLAlchemy uses parameterized statements. Inventory adjustments and order transitions are auditable.
- CORS allows only configured origins. The API emits generic server errors while logging structured diagnostics server-side.
- Payment records contain amounts and provider references only. The platform does not accept or persist card numbers, CVVs, or bank credentials.
- The Compose database password is a local-development default only. Production deployments must inject a managed secret and use TLS, private networking, backups, and least-privilege database accounts.

## Production hardening backlog

Use secure, HttpOnly, SameSite cookies (or a reviewed token flow), rate-limit authentication, add account lockout and password reset controls, rotate signing keys, enable database TLS, restrict CORS, add request IDs and log redaction, and integrate secrets management. Add provider-specific payment webhooks with signature verification before enabling actual payment processing.
