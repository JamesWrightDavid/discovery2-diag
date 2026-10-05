# server/

A self-hosted community contribution endpoint (stdlib + sqlite3). It is separate from
the diagnostic app.

**Interim location.** This is the seed of the private Ostler Cloud repo (ADR-0013): it
moves to `openostler/ostler-cloud` when that repo is created, and is not part of the
`d2diag` package.

## Files

- `README.md` — deploy and API.
- `endpoint.py` — receiver plus admin view.

## Editing rules

- Whitelist-based and PII-free by construction. Never add VIN, EKA or location fields.
- Tests live in `tests/test_endpoint.py`.
