"""
AzamPay Sandbox Integration Test
Run: PYTHONPATH=src python sandbox_test.py
"""

import os
import sys
import uuid

from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.environ["APP_NAME"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
X_API_KEY = os.environ["X_API_KEY"]
BEARER_TOKEN = os.environ.get("BEARER_TOKEN") or None  # optional pre-issued token

sys.path.insert(0, "src")

from azampay import AzamPay, AzamPayError  # noqa: E402

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
INFO = "\033[94m→\033[0m"
WARN = "\033[93m!\033[0m"


def section(title: str) -> None:
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print("─" * 55)


def run() -> None:
    client = AzamPay(
        app_name=APP_NAME,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        x_api_key=X_API_KEY,
        sandbox=True,
        token=BEARER_TOKEN,  # used directly if provided, skips auth call
    )

    # ── 1. Authentication ─────────────────────────────────────
    section("1. Authentication")
    if BEARER_TOKEN:
        print(f"{WARN} Using pre-issued BEARER_TOKEN from .env (skipping auth endpoint)")
        token_str = f"Bearer {BEARER_TOKEN}"
        print(f"{PASS} Token: {token_str[:50]}...")
    else:
        try:
            token_str = client._authenticate()
            print(f"{PASS} Token acquired: {token_str[:50]}...")
        except AzamPayError as e:
            print(f"{FAIL} Auth failed — status={e.status_code} | {e.response}")
            print(f"\n{WARN}  Tip: copy the bearer token from your AzamPay portal dashboard")
            print(f"     and set BEARER_TOKEN=<token> in your .env file, then rerun.\n")
            return
        except Exception as e:
            print(f"{FAIL} Auth error: {e}")
            return

    # ── 2. Mobile Checkout — Airtel ───────────────────────────
    section("2. Mobile Checkout — Airtel")
    ext_id_airtel = f"test-{uuid.uuid4().hex[:8]}"
    airtel_tx_id = None
    try:
        result = client.checkout.mobile_checkout(
            amount="1000",
            account_number="0655000000",
            external_id=ext_id_airtel,
            provider="Airtel",
        )
        print(f"{PASS} Response: {result}")
        airtel_tx_id = result.get("transactionId") or (result.get("data") or {}).get("transactionId")
    except AzamPayError as e:
        print(f"{FAIL} status={e.status_code} | {e.response}")

    # ── 3. Mobile Checkout — Tigo ─────────────────────────────
    section("3. Mobile Checkout — Tigo")
    ext_id_tigo = f"test-{uuid.uuid4().hex[:8]}"
    try:
        result = client.checkout.mobile_checkout(
            amount="2000",
            account_number="0713000000",
            external_id=ext_id_tigo,
            provider="Tigo",
        )
        print(f"{PASS} Response: {result}")
    except AzamPayError as e:
        print(f"{FAIL} status={e.status_code} | {e.response}")

    # ── 4. Mobile Checkout — MPESA ────────────────────────────
    section("4. Mobile Checkout — MPESA")
    ext_id_mpesa = f"test-{uuid.uuid4().hex[:8]}"
    try:
        result = client.checkout.mobile_checkout(
            amount="1500",
            account_number="0765000000",
            external_id=ext_id_mpesa,
            provider="MPESA",
        )
        print(f"{PASS} Response: {result}")
    except AzamPayError as e:
        print(f"{FAIL} status={e.status_code} | {e.response}")

    # ── 5. Transaction Status Lookup ──────────────────────────
    section("5. Transaction Status Lookup")
    lookup_id = airtel_tx_id or ext_id_airtel
    lookup_key = "pgReferenceId" if airtel_tx_id else "externalId"
    try:
        kwargs = {"pg_reference_id": lookup_id} if airtel_tx_id else {"external_id": lookup_id}
        status_result = client.lookup.transaction_status(**kwargs)
        print(f"{PASS} {lookup_key}={lookup_id!r} → {status_result}")
    except AzamPayError as e:
        print(f"{FAIL} status={e.status_code} | {e.response}")

    # ── 6. Payment Links — List ───────────────────────────────
    section("6. Payment Links — List")
    created_code = None
    try:
        links = client.links.list_links()
        print(f"{PASS} {len(links)} link(s) found: {links}")
    except AzamPayError as e:
        print(f"{FAIL} status={e.status_code} | {e.response}")

    # ── 7. Payment Links — Create ─────────────────────────────
    section("7. Payment Links — Create")
    try:
        link = client.links.create_link(
            amount="5000",
            link_name="SDK Test Link",
            description="Created by sandbox_test.py",
        )
        print(f"{PASS} Created: {link}")
        created_code = link.get("linkCode") or (link.get("data") or {}).get("linkCode")
    except AzamPayError as e:
        print(f"{FAIL} status={e.status_code} | {e.response}")

    # ── 8. Payment Links — Get Payments ───────────────────────
    if created_code:
        section(f"8. Payment Links — Payments for {created_code!r}")
        try:
            payments = client.links.get_link_payments(created_code)
            print(f"{PASS} {len(payments)} payment(s): {payments}")
        except AzamPayError as e:
            print(f"{FAIL} status={e.status_code} | {e.response}")

    # ── 9. Disbursement — Mobile ──────────────────────────────
    section("9. Disbursement — Mobile Money (Airtel)")
    try:
        disburse_result = client.disbursement.disburse_mobile(
            full_name="Test Recipient",
            mobile_number="0655000000",
            provider="Airtel",
            amount="500",
            reference_id=f"dis-{uuid.uuid4().hex[:8]}",
            remarks="SDK sandbox test",
        )
        print(f"{PASS} Response: {disburse_result}")
    except AzamPayError as e:
        print(f"{FAIL} status={e.status_code} | {e.response}")

    # ── 10. Name Lookup ───────────────────────────────────────
    section("10. Bank Name Lookup — CRDB")
    try:
        name_result = client.lookup.name_lookup("CRDB", "0000000001")
        print(f"{PASS} Response: {name_result}")
    except AzamPayError as e:
        print(f"{FAIL} status={e.status_code} | {e.response}")

    print(f"\n{'─' * 55}")
    print("  All tests complete.")
    print("─" * 55)
    client.close()


if __name__ == "__main__":
    run()
