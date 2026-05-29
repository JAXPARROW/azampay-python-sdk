from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncAzamPayClient
    from ..client import AzamPayClient

_DISBURSE_PATH = "/api/v1/azampay/disburse"


class DisbursementService:
    """Synchronous disbursement (payout) operations."""

    def __init__(self, client: "AzamPayClient") -> None:
        self._c = client

    def disburse(
        self,
        source: dict[str, Any],
        destination: dict[str, Any],
        amount: str,
        currency: str = "TZS",
        reference_id: str | None = None,
        remarks: str | None = None,
        transfer_type: str = "INTERNAL",
    ) -> dict[str, Any]:
        """Send a disbursement to a bank account or mobile wallet.

        Args:
            source:        Dict describing the sending account.
                           Keys: ``countryCode``, ``fullName``, ``bankName``,
                           ``accountNumber``, ``currency``.
            destination:   Dict describing the receiving account.
                           Same keys as *source*; use the mobile number as
                           ``accountNumber`` for mobile-money recipients.
            amount:        Amount to disburse as a string (e.g. "5000").
            currency:      ISO 4217 currency code (default "TZS").
            reference_id:  Your unique reference for this disbursement.
            remarks:       Free-text description attached to the transfer.
            transfer_type: "INTERNAL" (same bank) or "EXTERNAL" (default "INTERNAL").

        Returns:
            AzamPay response dict with transaction details.
        """
        payload: dict[str, Any] = {
            "source": source,
            "destination": destination,
            "transferDetails": {
                "type": transfer_type,
                "amount": amount,
                "currency": currency,
            },
        }
        if reference_id:
            payload["referenceId"] = reference_id
        if remarks:
            payload["remarks"] = remarks
        return self._c.request(  # type: ignore[return-value]
            "POST", _DISBURSE_PATH, json=payload, base_url=self._c.disburse_url, skip_checksum=True
        )

    def disburse_mobile(
        self,
        full_name: str,
        mobile_number: str,
        provider: str,
        amount: str,
        currency: str = "TZS",
        reference_id: str | None = None,
        remarks: str | None = None,
        source: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Convenience wrapper — disburse to a mobile-money wallet.

        Args:
            full_name:     Recipient's full name.
            mobile_number: Recipient's mobile number (e.g. "0741234567").
            provider:      Mobile provider name (e.g. "Airtel", "Tigo").
            amount:        Amount to disburse as a string.
            currency:      ISO 4217 currency code (default "TZS").
            reference_id:  Your unique reference (optional).
            remarks:       Free-text description (optional).
            source:        Override the source account dict (optional).
        """
        destination = {
            "countryCode": "TZ",
            "fullName": full_name,
            "bankName": provider,
            "accountNumber": mobile_number,
            "currency": currency,
        }
        _source = source or {
            "countryCode": "TZ",
            "fullName": "",
            "bankName": "",
            "accountNumber": "",
            "currency": currency,
        }
        return self.disburse(
            source=_source,
            destination=destination,
            amount=amount,
            currency=currency,
            reference_id=reference_id,
            remarks=remarks,
        )

    def disburse_bank(
        self,
        full_name: str,
        account_number: str,
        bank_name: str,
        amount: str,
        currency: str = "TZS",
        reference_id: str | None = None,
        remarks: str | None = None,
        transfer_type: str = "EXTERNAL",
        source: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Convenience wrapper — disburse to a bank account.

        Args:
            full_name:      Recipient's full name.
            account_number: Recipient's bank account number.
            bank_name:      Bank identifier (e.g. "CRDB", "NMB").
            amount:         Amount to disburse as a string.
            currency:       ISO 4217 currency code (default "TZS").
            reference_id:   Your unique reference (optional).
            remarks:        Free-text description (optional).
            transfer_type:  "INTERNAL" or "EXTERNAL" (default "EXTERNAL").
            source:         Override the source account dict (optional).
        """
        destination = {
            "countryCode": "TZ",
            "fullName": full_name,
            "bankName": bank_name,
            "accountNumber": account_number,
            "currency": currency,
        }
        _source = source or {
            "countryCode": "TZ",
            "fullName": "",
            "bankName": "",
            "accountNumber": "",
            "currency": currency,
        }
        return self.disburse(
            source=_source,
            destination=destination,
            amount=amount,
            currency=currency,
            reference_id=reference_id,
            remarks=remarks,
            transfer_type=transfer_type,
        )


class AsyncDisbursementService:
    """Asynchronous disbursement (payout) operations."""

    def __init__(self, client: "AsyncAzamPayClient") -> None:
        self._c = client

    async def disburse(
        self,
        source: dict[str, Any],
        destination: dict[str, Any],
        amount: str,
        currency: str = "TZS",
        reference_id: str | None = None,
        remarks: str | None = None,
        transfer_type: str = "INTERNAL",
    ) -> dict[str, Any]:
        """Send a disbursement to a bank account or mobile wallet."""
        payload: dict[str, Any] = {
            "source": source,
            "destination": destination,
            "transferDetails": {
                "type": transfer_type,
                "amount": amount,
                "currency": currency,
            },
        }
        if reference_id:
            payload["referenceId"] = reference_id
        if remarks:
            payload["remarks"] = remarks
        return await self._c.request(  # type: ignore[return-value]
            "POST", _DISBURSE_PATH, json=payload, base_url=self._c.disburse_url, skip_checksum=True
        )

    async def disburse_mobile(
        self,
        full_name: str,
        mobile_number: str,
        provider: str,
        amount: str,
        currency: str = "TZS",
        reference_id: str | None = None,
        remarks: str | None = None,
        source: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Convenience wrapper — disburse to a mobile-money wallet."""
        destination = {
            "countryCode": "TZ",
            "fullName": full_name,
            "bankName": provider,
            "accountNumber": mobile_number,
            "currency": currency,
        }
        _source = source or {
            "countryCode": "TZ",
            "fullName": "",
            "bankName": "",
            "accountNumber": "",
            "currency": currency,
        }
        return await self.disburse(
            source=_source,
            destination=destination,
            amount=amount,
            currency=currency,
            reference_id=reference_id,
            remarks=remarks,
        )

    async def disburse_bank(
        self,
        full_name: str,
        account_number: str,
        bank_name: str,
        amount: str,
        currency: str = "TZS",
        reference_id: str | None = None,
        remarks: str | None = None,
        transfer_type: str = "EXTERNAL",
        source: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Convenience wrapper — disburse to a bank account."""
        destination = {
            "countryCode": "TZ",
            "fullName": full_name,
            "bankName": bank_name,
            "accountNumber": account_number,
            "currency": currency,
        }
        _source = source or {
            "countryCode": "TZ",
            "fullName": "",
            "bankName": "",
            "accountNumber": "",
            "currency": currency,
        }
        return await self.disburse(
            source=_source,
            destination=destination,
            amount=amount,
            currency=currency,
            reference_id=reference_id,
            remarks=remarks,
            transfer_type=transfer_type,
        )
