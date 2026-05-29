# AzamPay Python SDK

Production-grade Python SDK for the [AzamPay](https://developers.azampay.co.tz) API — sync & async, mobile checkout, bank checkout, disbursements, payment links, and webhook verification.

## Features

- **Sync & Async** — `AzamPay` for Django/Flask, `AsyncAzamPay` for FastAPI/asyncio
- **Auto auth** — token fetched on first call, cached for 23 hours, thread/async-safe refresh
- **Checksum injection** — HMAC-SHA256 automatically added to mutation requests when `x_api_key` is set
- **Retry logic** — exponential backoff on transient 5xx errors and network failures
- **Typed exceptions** — every API error maps to a specific exception class
- **Context manager** — `with`/`async with` for clean connection lifecycle
- **PEP 561** — ships `py.typed` for full mypy support

## Installation

```bash
pip install azampay-python-sdk
```

Requires Python 3.10+.

## Quick Start

### Synchronous

```python
from azampay import AzamPay, AzamPayError

with AzamPay(
    app_name="MyApp",
    client_id="your_client_id",
    client_secret="your_client_secret",
    x_api_key="your_x_api_key",
    sandbox=True,
) as client:
    # Mobile checkout (USSD push)
    result = client.checkout.mobile_checkout(
        amount="5000",
        account_number="0741234567",
        external_id="order-001",
        provider="Airtel",
    )
    print(result["transactionId"])
```

### Asynchronous

```python
import asyncio
from azampay import AsyncAzamPay

async def main() -> None:
    async with AsyncAzamPay(
        app_name="MyApp",
        client_id="your_client_id",
        client_secret="your_client_secret",
        x_api_key="your_x_api_key",
        sandbox=True,
    ) as client:
        result = await client.checkout.mobile_checkout(
            amount="5000",
            account_number="0741234567",
            external_id="order-001",
            provider="Airtel",
        )

asyncio.run(main())
```

## Services

### `client.checkout`

```python
# Mobile money (USSD push) — Airtel, Tigo, MPESA, HALOPESA, AZAMPESA, TTCL
client.checkout.mobile_checkout(amount, account_number, external_id, provider, currency="TZS")

# Internet banking
client.checkout.bank_checkout(amount, merchant_account_number, merchant_mobile_number, reference_id, bank_name)
```

### `client.disbursement`

```python
# Mobile wallet payout
client.disbursement.disburse_mobile(full_name, mobile_number, provider, amount)

# Bank account payout
client.disbursement.disburse_bank(full_name, account_number, bank_name, amount)

# Raw payout with full control
client.disbursement.disburse(source, destination, amount)
```

### `client.lookup`

```python
# Check transaction status
client.lookup.transaction_status(pg_reference_id="pg-123")
client.lookup.transaction_status(external_id="order-001")

# Resolve bank account holder name
client.lookup.name_lookup(bank_name="CRDB", account_number="1234567890")
```

### `client.links`

```python
# List all payment links
client.links.list_links()

# Create a reusable payment link
client.links.create_link(amount="10000", link_name="School Fees")

# Get payments for a link
client.links.get_link_payments(link_code="LC1")
```

## Webhook Verification

```python
from azampay import WebhookValidator

# In your Flask/FastAPI/Django view:
is_valid = WebhookValidator.verify(
    payload=request.json,
    signature=request.headers["X-Checksum"],
    checksum_key="your_x_api_key",
)
```

## Error Handling

```python
from azampay import (
    AzamPayError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

try:
    result = client.checkout.mobile_checkout(...)
except AuthenticationError:
    # Invalid credentials
except ValidationError as e:
    print(e.response)   # Full API response dict
except RateLimitError:
    # Back off and retry
except AzamPayError as e:
    print(e.status_code, e.response)
```

## Configuration

| Parameter       | Type            | Default | Description                          |
|-----------------|-----------------|---------|--------------------------------------|
| `app_name`      | `str`           | —       | App name from AzamPay portal         |
| `client_id`     | `str`           | —       | OAuth client ID                      |
| `client_secret` | `str`           | —       | OAuth client secret                  |
| `x_api_key`     | `str \| None`   | `None`  | X-API-Key for requests and checksums |
| `sandbox`       | `bool`          | `False` | Use sandbox environment              |
| `timeout`       | `float`         | `30.0`  | HTTP timeout in seconds              |
| `max_retries`   | `int`           | `3`     | Max retries on transient failures    |

## Development

```bash
make install   # Install with dev dependencies
make test      # Run tests
make lint      # Ruff lint
make typecheck # mypy strict
make build     # Build wheel + sdist
```

## License

MIT
