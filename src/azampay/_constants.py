from __future__ import annotations

_SANDBOX_AUTH = "https://authenticator-sandbox.azampay.co.tz"
_SANDBOX_BASE = "https://sandbox.azampay.co.tz"
_SANDBOX_DISBURSE = "https://api-disbursement-sandbox.azampay.co.tz"
_TEST_AUTH = "https://authenticator-test.azampay.co.tz"
_TEST_DISBURSE = "https://api-disbursement-test.azampay.co.tz"
_PRODUCTION_AUTH = "https://authenticator.azampay.co.tz"
_PRODUCTION_API = "https://checkout.azampay.co.tz"
_PRODUCTION_DISBURSE = "https://api-disbursement.azampay.co.tz"

_AUTH_PATH = "/AppRegistration/GenerateToken"
_TOKEN_TTL = 82800  # 23 hours (API issues 24-hour tokens; -1 h safety margin)
_RETRY_STATUSES: frozenset[int] = frozenset({500, 502, 503, 504})
