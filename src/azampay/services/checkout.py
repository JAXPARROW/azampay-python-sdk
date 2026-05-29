from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from ..async_client import AsyncAzamPayClient
    from ..client import AzamPayClient

MobileProvider = Literal["Airtel", "Tigo", "MPESA", "HALOPESA", "AZAMPESA", "TTCL"]

_MNO_PATH = "/azampay/mno/checkout"
_BANK_PATH = "/azampay/bank/checkout"


class CheckoutService:
    """Synchronous collection (checkout) operations."""

    def __init__(self, client: "AzamPayClient") -> None:
        self._c = client

    def mobile_checkout(
        self,
        amount: str,
        account_number: str,
        external_id: str,
        provider: MobileProvider,
        currency: str = "TZS",
        additional_properties: dict[str, Any] | None = None,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        """Initiate a mobile-money (USSD push) payment.

        Args:
            amount:                Amount to collect as a string (e.g. "10000").
            account_number:        Customer mobile number (e.g. "0741234567").
            external_id:           Your unique order/reference ID.
            provider:              Mobile provider name.
            currency:              ISO 4217 currency code (default "TZS").
            additional_properties: Optional extra key/value pairs forwarded to AzamPay.
            callback_url:          URL to receive the payment status callback.
        """
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
        return self._c.request("POST", _MNO_PATH, json=payload)  # type: ignore[return-value]

    def bank_checkout(
        self,
        amount: str,
        merchant_account_number: str,
        merchant_mobile_number: str,
        reference_id: str,
        bank_name: str,
        merchant_name: str | None = None,
        otp: str | None = None,
        currency: str = "TZS",
        additional_properties: dict[str, Any] | None = None,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        """Initiate a bank-to-merchant payment (internet banking).

        Args:
            amount:                  Amount to collect as a string.
            merchant_account_number: Merchant bank account number.
            merchant_mobile_number:  Merchant mobile number.
            reference_id:            Your unique order/reference ID.
            bank_name:               Bank identifier (e.g. "CRDB", "NMB").
            merchant_name:           Display name for the merchant (optional).
            otp:                     One-time password if required by the bank (optional).
            currency:                ISO 4217 currency code (default "TZS").
            additional_properties:   Optional extra key/value pairs.
            callback_url:            URL to receive the payment status callback.
        """
        payload: dict[str, Any] = {
            "merchantAccountNumber": merchant_account_number,
            "merchantMobileNumber": merchant_mobile_number,
            "referenceId": reference_id,
            "amount": amount,
            "currency": currency,
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
        return self._c.request("POST", _BANK_PATH, json=payload)  # type: ignore[return-value]


class AsyncCheckoutService:
    """Asynchronous collection (checkout) operations."""

    def __init__(self, client: "AsyncAzamPayClient") -> None:
        self._c = client

    async def mobile_checkout(
        self,
        amount: str,
        account_number: str,
        external_id: str,
        provider: MobileProvider,
        currency: str = "TZS",
        additional_properties: dict[str, Any] | None = None,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        """Initiate a mobile-money (USSD push) payment."""
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
        return await self._c.request("POST", _MNO_PATH, json=payload)  # type: ignore[return-value]

    async def bank_checkout(
        self,
        amount: str,
        merchant_account_number: str,
        merchant_mobile_number: str,
        reference_id: str,
        bank_name: str,
        merchant_name: str | None = None,
        otp: str | None = None,
        currency: str = "TZS",
        additional_properties: dict[str, Any] | None = None,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        """Initiate a bank-to-merchant payment (internet banking)."""
        payload: dict[str, Any] = {
            "merchantAccountNumber": merchant_account_number,
            "merchantMobileNumber": merchant_mobile_number,
            "referenceId": reference_id,
            "amount": amount,
            "currency": currency,
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
        return await self._c.request("POST", _BANK_PATH, json=payload)  # type: ignore[return-value]
