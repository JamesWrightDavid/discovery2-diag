# server/

A self-hosted community contribution endpoint (stdlib + sqlite3). It is separate from
the diagnostic app.

## Files

- `README.md` — deploy and API.
- `endpoint.py` — receiver plus admin view.

## Editing rules

- Whitelist-based and PII-free by construction. Never add VIN, EKA or location fields.
- Tests live in `tests/test_endpoint.py`.
