# Changelog

## [1.0.0] - 2026-05-29

### Added
- `AzamPay` and `AsyncAzamPay` top-level clients with service namespaces
- `CheckoutService` / `AsyncCheckoutService` — mobile checkout (USSD push) and bank checkout
- `DisbursementService` / `AsyncDisbursementService` — raw disburse, `disburse_mobile`, `disburse_bank` convenience methods
- `LookupService` / `AsyncLookupService` — transaction status and bank name inquiry
- `LinkService` / `AsyncLinkService` — list, create, and query payment links
- Automatic token caching with 23-hour TTL and thread/async-safe refresh
- HMAC-SHA256 checksum injection on `POST`/`PUT`/`PATCH` requests when `x_api_key` is set
- `WebhookValidator` for verifying AzamPay callback signatures
- `SecurityManager` for creating and verifying checksums
- Typed exception hierarchy: `AzamPayError`, `AuthenticationError`, `ForbiddenError`, `ValidationError`, `NotFoundError`, `RateLimitError`, `ServerError`
- Exponential backoff retry logic on transient 5xx errors and network failures
- Context manager support for both sync and async clients
- PEP 561 compliance (`py.typed` marker)
- Full type hints with `mypy --strict` compatibility
