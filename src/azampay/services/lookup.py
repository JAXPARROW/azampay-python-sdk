from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._payloads import transaction_status_params

if TYPE_CHECKING:
    from ..async_client import AsyncAzamPayClient
    from ..client import AzamPayClient

_STATUS_PATH = "/api/v1/azampay/transactionstatus"
_NAME_LOOKUP_PATH = "/api/v1/azampay/namelookup"


class LookupService:
    """Synchronous transaction and account lookup operations."""

    def __init__(self, client: "AzamPayClient") -> None:
        self._c = client

    def transaction_status(
        self,
        pg_reference_id: str | None = None,
        external_id: str | None = None,
        bank_name: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve the status of a transaction.

        Provide at least one of *pg_reference_id* or *external_id*.

        Args:
            pg_reference_id: AzamPay payment gateway reference ID.
            external_id:     Your external/order reference ID.
            bank_name:       Bank or provider name (optional, used with pg_reference_id).

        Returns:
            Dict containing transaction status details.

        Raises:
            ValueError: If neither identifier is provided.
        """
        params = transaction_status_params(pg_reference_id, external_id, bank_name)
        return self._c.request(  # type: ignore[no-any-return]
            "GET", _STATUS_PATH, params=params, base_url=self._c.disburse_url, skip_checksum=True
        )

    def name_lookup(self, bank_name: str, account_number: str) -> dict[str, Any]:
        """Resolve the account holder name for a bank or mobile-money account.

        Args:
            bank_name:      Bank or mobile provider identifier (e.g. "CRDB", "Airtel").
            account_number: The account or mobile number to query.

        Returns:
            Dict with account holder details (firstName, lastName, accountNumber, etc.).
        """
        payload = {"bankName": bank_name, "accountNumber": account_number}
        return self._c.request(  # type: ignore[no-any-return]
            "POST", _NAME_LOOKUP_PATH, json=payload, base_url=self._c.disburse_url, skip_checksum=True
        )


class AsyncLookupService:
    """Asynchronous transaction and account lookup operations."""

    def __init__(self, client: "AsyncAzamPayClient") -> None:
        self._c = client

    async def transaction_status(
        self,
        pg_reference_id: str | None = None,
        external_id: str | None = None,
        bank_name: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve the status of a transaction.

        Provide at least one of *pg_reference_id* or *external_id*.

        Raises:
            ValueError: If neither identifier is provided.
        """
        params = transaction_status_params(pg_reference_id, external_id, bank_name)
        return await self._c.request(  # type: ignore[no-any-return]
            "GET", _STATUS_PATH, params=params, base_url=self._c.disburse_url, skip_checksum=True
        )

    async def name_lookup(self, bank_name: str, account_number: str) -> dict[str, Any]:
        """Resolve the account holder name for a bank or mobile-money account."""
        payload = {"bankName": bank_name, "accountNumber": account_number}
        return await self._c.request(  # type: ignore[no-any-return]
            "POST", _NAME_LOOKUP_PATH, json=payload, base_url=self._c.disburse_url, skip_checksum=True
        )
