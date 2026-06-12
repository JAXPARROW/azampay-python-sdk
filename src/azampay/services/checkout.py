from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from ._payloads import bank_checkout_payload, mobile_checkout_payload, post_checkout_payload

if TYPE_CHECKING:
    from ..async_client import AsyncAzamPayClient
    from ..client import AzamPayClient

MobileProvider = Literal["Airtel", "Tigo", "Halopesa", "Azampesa", "Mpesa"]
DisburseProvider = Literal["Airtel", "Azampesa", "Tigo"]
BankProvider = Literal["CRDB", "NMB"]

_MNO_PATH = "/azampay/mno/checkout"
_BANK_PATH = "/azampay/bank/checkout"
_PARTNERS_PATH = "/api/v1/Partner/GetPaymentPartners"
_POST_CHECKOUT_PATH = "/api/v1/Partner/PostCheckout"
_PUBLIC_KEY_PATH = "/azampay/v1/public-key"


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
        payload = mobile_checkout_payload(
            amount, account_number, external_id, provider, currency, additional_properties, callback_url
        )
        return self._c.request("POST", _MNO_PATH, json=payload)  # type: ignore[no-any-return]

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
        payload = bank_checkout_payload(
            amount, merchant_account_number, merchant_mobile_number, reference_id,
            bank_name, merchant_name, otp, currency, additional_properties, callback_url,
        )
        return self._c.request("POST", _BANK_PATH, json=payload)  # type: ignore[no-any-return]

    def get_payment_partners(self) -> list[dict[str, Any]]:
        """Return the list of payment partners registered for this merchant."""
        return self._c.request("GET", _PARTNERS_PATH)  # type: ignore[no-any-return]

    def post_checkout(
        self,
        amount: str,
        external_id: str,
        currency: str = "TZS",
        language: str = "en",
        app_name: str | None = None,
        cart: dict[str, Any] | None = None,
        client_id: str | None = None,
        redirect_fail_url: str | None = None,
        redirect_success_url: str | None = None,
        request_origin: str | None = None,
        vendor_id: str | None = None,
        vendor_name: str | None = None,
    ) -> str:
        """Create a hosted payment page and return its URL.

        The returned URL should be opened in a browser or iframe to let the
        customer complete payment via AzamPay's checkout page.

        Args:
            amount:               Amount to collect as a string (e.g. "10000").
            external_id:          Your unique order/reference ID.
            currency:             ISO 4217 currency code (default "TZS").
            language:             UI language code (default "en").
            app_name:             Registered application name (optional).
            cart:                 Cart object with item details (optional).
            client_id:            Your registered client ID (optional).
            redirect_fail_url:    URL to redirect on payment failure.
            redirect_success_url: URL to redirect on payment success.
            request_origin:       Origin URL of the merchant application.
            vendor_id:            AzamPay vendor ID (optional).
            vendor_name:          AzamPay vendor name (optional).

        Returns:
            Payment page URL string.
        """
        payload = post_checkout_payload(
            amount, external_id, currency, language, app_name, cart, client_id,
            redirect_fail_url, redirect_success_url, request_origin, vendor_id, vendor_name,
        )
        return self._c.request("POST", _POST_CHECKOUT_PATH, json=payload)  # type: ignore[no-any-return]

    def get_public_key(self, format: str = "Pem") -> dict[str, Any]:
        """Fetch AzamPay's RSA public key for callback signature verification.

        Cache the returned key locally and refresh every 24 hours, or
        re-fetch and retry once if ``WebhookValidator.verify_callback_signature``
        returns False.

        Args:
            format: Key format — ``"Pem"`` (default) or ``"Xml"``.

        Returns:
            Dict with ``success``, ``format``, and ``publicKey`` fields.
        """
        return self._c.request(  # type: ignore[no-any-return]
            "GET", _PUBLIC_KEY_PATH, params={"format": format}
        )


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
        payload = mobile_checkout_payload(
            amount, account_number, external_id, provider, currency, additional_properties, callback_url
        )
        return await self._c.request("POST", _MNO_PATH, json=payload)  # type: ignore[no-any-return]

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
        payload = bank_checkout_payload(
            amount, merchant_account_number, merchant_mobile_number, reference_id,
            bank_name, merchant_name, otp, currency, additional_properties, callback_url,
        )
        return await self._c.request("POST", _BANK_PATH, json=payload)  # type: ignore[no-any-return]

    async def get_payment_partners(self) -> list[dict[str, Any]]:
        """Return the list of payment partners registered for this merchant."""
        return await self._c.request("GET", _PARTNERS_PATH)  # type: ignore[no-any-return]

    async def post_checkout(
        self,
        amount: str,
        external_id: str,
        currency: str = "TZS",
        language: str = "en",
        app_name: str | None = None,
        cart: dict[str, Any] | None = None,
        client_id: str | None = None,
        redirect_fail_url: str | None = None,
        redirect_success_url: str | None = None,
        request_origin: str | None = None,
        vendor_id: str | None = None,
        vendor_name: str | None = None,
    ) -> str:
        """Create a hosted payment page and return its URL."""
        payload = post_checkout_payload(
            amount, external_id, currency, language, app_name, cart, client_id,
            redirect_fail_url, redirect_success_url, request_origin, vendor_id, vendor_name,
        )
        return await self._c.request("POST", _POST_CHECKOUT_PATH, json=payload)  # type: ignore[no-any-return]

    async def get_public_key(self, format: str = "Pem") -> dict[str, Any]:
        """Fetch AzamPay's RSA public key for callback signature verification."""
        return await self._c.request(  # type: ignore[no-any-return]
            "GET", _PUBLIC_KEY_PATH, params={"format": format}
        )
