# Contributing

## Before opening a pull request

1. Keep changes scoped to a business capability or a narrowly defined technical improvement.
2. Add or update tests for behavior changes. Keep database and API vocabulary aligned.
3. Run backend tests, Ruff, frontend lint and production build as applicable.
4. Update API or operational documentation when contracts or workflows change.
5. Confirm no secrets, local databases, generated files, or dependency directories are included.

## Design conventions

- API payloads use validated Pydantic schemas; do not expose ORM entities directly.
- Put business invariants in services so HTTP routes remain small.
- Use explicit database transactions for multi-entity workflows.
- Record actor, resource and meaningful context for business mutations.
- Enforce authorization on the server; frontend role checks are presentation only.
- Preserve order-line product name, SKU and price snapshots.

## Pull requests

Describe the user/business impact, implementation, migration needs, and validation performed. Call out security, data-retention, backward-compatibility, and operational risks. CI must pass before merge to `main`.
