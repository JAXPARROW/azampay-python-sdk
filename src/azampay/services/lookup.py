from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncAzamPayClient
    from ..client import AzamPayClient

_STATUS_PATH = "/azampay/api/v1/Partner/TransactionStatus"
_NAME_LOOKUP_PATH = "/azampay/api/v1/Bank/Inquiry"


class LookupService:
    """Synchronous transaction and account lookup operations."""

    def __init__(self, client: "AzamPayClient") -> None:
        self._c = client

    def transaction_status(
        self,
        pg_reference_id: str | None = None,
        external_id: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve the status of a transaction.

        Provide at least one of *pg_reference_id* (AzamPay's internal ID) or
        *external_id* (your own reference passed during checkout).

        Args:
            pg_reference_id: AzamPay payment gateway reference ID.
            external_id:     Your external/order reference ID.

        Returns:
            Dict containing transaction status details.

        Raises:
            ValueError: If neither identifier is provided.
        """
        if not pg_reference_id and not external_id:
            raise ValueError("Provide at least one of pg_reference_id or external_id.")
        params: dict[str, str] = {}
        if pg_reference_id:
            params["pgReferenceId"] = pg_reference_id
        if external_id:
            params["externalId"] = external_id
        return self._c.request("GET", _STATUS_PATH, params=params)  # type: ignore[return-value]

    def name_lookup(self, bank_name: str, account_number: str) -> dict[str, Any]:
        """Resolve the account holder name for a bank account.

        Args:
            bank_name:      Bank identifier (e.g. "CRDB", "NMB").
            account_number: The bank account number to query.

        Returns:
            Dict with account holder details returned by the bank.
        """
        payload = {"bankName": bank_name, "accountNumber": account_number}
        return self._c.request("POST", _NAME_LOOKUP_PATH, json=payload)  # type: ignore[return-value]


class AsyncLookupService:
    """Asynchronous transaction and account lookup operations."""

    def __init__(self, client: "AsyncAzamPayClient") -> None:
        self._c = client

    async def transaction_status(
        self,
        pg_reference_id: str | None = None,
        external_id: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve the status of a transaction.

        Provide at least one of *pg_reference_id* or *external_id*.

        Raises:
            ValueError: If neither identifier is provided.
        """
        if not pg_reference_id and not external_id:
            raise ValueError("Provide at least one of pg_reference_id or external_id.")
        params: dict[str, str] = {}
        if pg_reference_id:
            params["pgReferenceId"] = pg_reference_id
        if external_id:
            params["externalId"] = external_id
        return await self._c.request("GET", _STATUS_PATH, params=params)  # type: ignore[return-value]

    async def name_lookup(self, bank_name: str, account_number: str) -> dict[str, Any]:
        """Resolve the account holder name for a bank account."""
        payload = {"bankName": bank_name, "accountNumber": account_number}
        return await self._c.request("POST", _NAME_LOOKUP_PATH, json=payload)  # type: ignore[return-value]
