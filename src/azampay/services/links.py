from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncAzamPayClient
    from ..client import AzamPayClient

_LIST_PATH = "/azampay/api/v1/Partner/GetPaymentLinks"
_CREATE_PATH = "/azampay/api/v1/Partner/CreatePaymentLink"
_LINK_PAYMENTS_PATH = "/azampay/api/v1/Partner/GetLinkPayments"


class LinkService:
    """Synchronous payment-link operations."""

    def __init__(self, client: "AzamPayClient") -> None:
        self._c = client

    def list_links(self) -> list[dict[str, Any]]:
        """Return all payment links for this merchant account."""
        result = self._c.request("GET", _LIST_PATH)
        if isinstance(result, dict):
            return result.get("data", result)  # type: ignore[no-any-return]
        return result  # type: ignore[no-any-return]

    def create_link(
        self,
        amount: str,
        currency: str = "TZS",
        link_name: str | None = None,
        description: str | None = None,
        expiry_date: str | None = None,
    ) -> dict[str, Any]:
        """Create a reusable payment link.

        Args:
            amount:      Fixed amount for the link as a string (e.g. "10000").
            currency:    ISO 4217 currency code (default "TZS").
            link_name:   Human-friendly label shown to payers.
            description: Optional description or purpose of the payment.
            expiry_date: Optional expiry in ISO 8601 format (e.g. "2025-12-31").

        Returns:
            Dict with ``linkCode``, ``paymentLink``, and related metadata.
        """
        payload: dict[str, Any] = {"amount": amount, "currency": currency}
        if link_name:
            payload["linkName"] = link_name
        if description:
            payload["description"] = description
        if expiry_date:
            payload["expiryDate"] = expiry_date
        return self._c.request("POST", _CREATE_PATH, json=payload)  # type: ignore[no-any-return]

    def get_link_payments(self, link_code: str) -> list[dict[str, Any]]:
        """Return all payments made against *link_code*.

        Args:
            link_code: The unique code identifying the payment link.
        """
        result = self._c.request("GET", _LINK_PAYMENTS_PATH, params={"LinkCode": link_code})
        if isinstance(result, dict):
            return result.get("data", result)  # type: ignore[no-any-return]
        return result  # type: ignore[no-any-return]


class AsyncLinkService:
    """Asynchronous payment-link operations."""

    def __init__(self, client: "AsyncAzamPayClient") -> None:
        self._c = client

    async def list_links(self) -> list[dict[str, Any]]:
        """Return all payment links for this merchant account."""
        result = await self._c.request("GET", _LIST_PATH)
        if isinstance(result, dict):
            return result.get("data", result)  # type: ignore[no-any-return]
        return result  # type: ignore[no-any-return]

    async def create_link(
        self,
        amount: str,
        currency: str = "TZS",
        link_name: str | None = None,
        description: str | None = None,
        expiry_date: str | None = None,
    ) -> dict[str, Any]:
        """Create a reusable payment link."""
        payload: dict[str, Any] = {"amount": amount, "currency": currency}
        if link_name:
            payload["linkName"] = link_name
        if description:
            payload["description"] = description
        if expiry_date:
            payload["expiryDate"] = expiry_date
        return await self._c.request("POST", _CREATE_PATH, json=payload)  # type: ignore[no-any-return]

    async def get_link_payments(self, link_code: str) -> list[dict[str, Any]]:
        """Return all payments made against *link_code*."""
        result = await self._c.request("GET", _LINK_PAYMENTS_PATH, params={"LinkCode": link_code})
        if isinstance(result, dict):
            return result.get("data", result)  # type: ignore[no-any-return]
        return result  # type: ignore[no-any-return]
