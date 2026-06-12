from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..security import SecurityManager


# ------------------------------------------------------------------
# Checkout
# ------------------------------------------------------------------

def mobile_checkout_payload(
    amount: str,
    account_number: str,
    external_id: str,
    provider: str,
    currency: str,
    additional_properties: dict[str, Any] | None,
    callback_url: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "accountNumber": account_number,
        "amount": amount,
        "currency": currency,
        "externalId": external_id,
        "provider": provider,
    }
    if additional_properties:
        payload["additionalProperties"] = additional_properties
    if callback_url:
        payload["callbackUrl"] = callback_url
    return payload


def bank_checkout_payload(
    amount: str,
    merchant_account_number: str,
    merchant_mobile_number: str,
    reference_id: str,
    bank_name: str,
    merchant_name: str | None,
    otp: str | None,
    currency: str,
    additional_properties: dict[str, Any] | None,
    callback_url: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "merchantAccountNumber": merchant_account_number,
        "merchantMobileNumber": merchant_mobile_number,
        "referenceId": reference_id,
        "amount": amount,
        "currencyCode": currency,
        "provider": bank_name,
    }
    if merchant_name:
        payload["merchantName"] = merchant_name
    if otp:
        payload["otp"] = otp
    if additional_properties:
        payload["additionalProperties"] = additional_properties
    if callback_url:
        payload["callbackUrl"] = callback_url
    return payload


# ------------------------------------------------------------------
# Disbursement
# ------------------------------------------------------------------

def mobile_destination(
    full_name: str,
    mobile_number: str,
    provider: str,
    currency: str,
) -> dict[str, str]:
    return {
        "countryCode": "TZ",
        "fullName": full_name,
        "bankName": provider,
        "accountNumber": mobile_number,
        "currency": currency,
    }


def bank_destination(
    full_name: str,
    account_number: str,
    bank_name: str,
    currency: str,
) -> dict[str, str]:
    return {
        "countryCode": "TZ",
        "fullName": full_name,
        "bankName": bank_name,
        "accountNumber": account_number,
        "currency": currency,
    }


def disburse_payload(
    source: dict[str, Any],
    destination: dict[str, Any],
    amount: str,
    reference_id: str,
    currency: str,
    remarks: str | None,
    transfer_type: str,
    rsa_public_key: str | None,
) -> dict[str, Any]:
    epoch_date = int(datetime.now(timezone.utc).timestamp())
    payload: dict[str, Any] = {
        "source": source,
        "destination": destination,
        "transferDetails": {
            "type": transfer_type,
            "amount": float(amount),
            "dateInEpoch": epoch_date,
        },
        "externalReferenceId": reference_id,
    }
    if remarks:
        payload["remarks"] = remarks
    if rsa_public_key:
        src_acc = source.get("accountNumber", "")
        dst_acc = destination.get("accountNumber", "")
        currency_val = source.get("currency", currency)
        input_string = f"{src_acc}{dst_acc}{currency_val}{amount}{epoch_date}{reference_id}"
        payload["checksum"] = SecurityManager.create_rsa_checksum(rsa_public_key, input_string)
    return payload


# ------------------------------------------------------------------
# Links
# ------------------------------------------------------------------

def link_payload(
    amount: str,
    currency: str,
    link_name: str | None,
    description: str | None,
    expiry_date: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"amount": amount, "currency": currency}
    if link_name:
        payload["linkName"] = link_name
    if description:
        payload["description"] = description
    if expiry_date:
        payload["expiryDate"] = expiry_date
    return payload


def post_checkout_payload(
    amount: str,
    external_id: str,
    currency: str,
    language: str,
    app_name: str | None,
    cart: dict[str, Any] | None,
    client_id: str | None,
    redirect_fail_url: str | None,
    redirect_success_url: str | None,
    request_origin: str | None,
    vendor_id: str | None,
    vendor_name: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "amount": amount,
        "currency": currency,
        "externalId": external_id,
        "language": language,
    }
    if app_name:
        payload["appName"] = app_name
    if cart:
        payload["cart"] = cart
    if client_id:
        payload["clientId"] = client_id
    if redirect_fail_url:
        payload["redirectFailURL"] = redirect_fail_url
    if redirect_success_url:
        payload["redirectSuccessURL"] = redirect_success_url
    if request_origin:
        payload["requestOrigin"] = request_origin
    if vendor_id:
        payload["vendorId"] = vendor_id
    if vendor_name:
        payload["vendorName"] = vendor_name
    return payload


def unwrap_list(result: Any) -> list[dict[str, Any]]:
    if isinstance(result, dict):
        return result.get("data", result)  # type: ignore[no-any-return]
    return result  # type: ignore[no-any-return]


# ------------------------------------------------------------------
# Lookup
# ------------------------------------------------------------------

def transaction_status_params(
    pg_reference_id: str | None,
    external_id: str | None,
    bank_name: str | None,
) -> dict[str, str]:
    if not pg_reference_id and not external_id:
        raise ValueError("Provide at least one of pg_reference_id or external_id.")
    params: dict[str, str] = {}
    if pg_reference_id:
        params["pgReferenceId"] = pg_reference_id
    if external_id:
        params["externalId"] = external_id
    if bank_name:
        params["bankName"] = bank_name
    return params
