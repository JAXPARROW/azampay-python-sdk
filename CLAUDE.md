# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install with dev dependencies
make install           # pip install -e ".[dev]"

# Run all tests
make test              # PYTHONPATH=src:. pytest -v

# Run a single test file
PYTHONPATH=src:. pytest tests/test_checkout.py -v

# Run a single test by name
PYTHONPATH=src:. pytest tests/test_client.py::test_token_cached_across_requests -v

# Lint and type-check
make lint              # ruff check src tests
make typecheck         # mypy src

# Live sandbox integration test (requires .env)
python sandbox_test.py

# Build distribution
make build
```

## Architecture

The SDK follows a **service-oriented client pattern** modelled after `clickpesa-python-sdk` (at `../clickpesa/clickpesa-python-sdk`). Every public feature has a mirrored sync/async pair.

### Entry points

`AzamPay` and `AsyncAzamPay` (in `src/azampay/__init__.py`) are thin subclasses of `AzamPayClient` / `AsyncAzamPayClient` that attach four service namespaces on `__init__`:

```
client.checkout      → CheckoutService
client.disbursement  → DisbursementService
client.lookup        → LookupService
client.links         → LinkService
```

Each service holds a `self._c` reference back to the client and delegates every HTTP call through `self._c.request(...)`.

### Request flow

`client.request(method, endpoint, json, params, base_url, skip_checksum)` in `client.py`:
1. Calls `_authenticate()` — fetches and caches the bearer token (23-hour TTL, thread-safe via `threading.Lock`; async uses `asyncio.Lock` created lazily).
2. Injects `X-API-Key` header when `x_api_key` is set.
3. Injects HMAC-SHA256 `checksum` into mutation payloads **unless** `skip_checksum=True`.
4. Retries on `{500,502,503,504}` and `TransportError` with exponential backoff (`2^(attempt-1)` seconds).
5. Maps HTTP status codes to typed exceptions via `_handle_response`.

### Base URLs (three separate hosts)

| Purpose | Sandbox | Production |
|---|---|---|
| Auth | `authenticator-sandbox.azampay.co.tz` | `authenticator.azampay.co.tz` |
| Checkout / Links | `sandbox.azampay.co.tz` | `checkout.azampay.co.tz` |
| Disbursement / Lookup | `api-disbursement-sandbox.azampay.co.tz` | `api-disbursement.azampay.co.tz` |

Services that use the disbursement host pass `base_url=self._c.disburse_url` and `skip_checksum=True` to `request()`. Disbursement requires an RSA+SHA512 checksum (`Base64(RSA(SHA512(payload)))`) — AzamPay must provide their public key; contact `support@azampay.com`.

### Checksum

`SecurityManager` in `security.py` handles HMAC-SHA256 for checkout/links. Keys are sorted recursively before serialisation to ensure a deterministic digest. `WebhookValidator` wraps the same logic for callback verification.

### Exceptions

All errors extend `AzamPayError(message, status_code, response)`. The hierarchy:
`AzamPayError` → `AuthenticationError` (401), `ForbiddenError` (403), `ValidationError` (400), `NotFoundError` (404), `RateLimitError` (429), `ServerError` (5xx).

### Testing

Tests use `respx` to mock HTTP at the transport layer. Each test file imports `SANDBOX_AUTH`, `SANDBOX_BASE`, `SANDBOX_DISBURSE` from `tests/conftest.py` to build mock URLs — update those constants there if base URLs change, not in individual test files.

### Sandbox credentials

Stored in `.env` (gitignored). Copy `.env.example` and fill in `APP_NAME`, `CLIENT_ID`, `CLIENT_SECRET`, `X_API_KEY`. Optionally set `BEARER_TOKEN` to skip the auth endpoint with a pre-issued portal token.
