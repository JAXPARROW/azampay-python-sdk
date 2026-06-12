from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._payloads import bank_destination, disburse_payload, mobile_destination

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
        reference_id: str,
        currency: str = "TZS",
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
            reference_id:  Your unique reference ID (max 30 chars, required by API).
            currency:      ISO 4217 currency code (default "TZS").
            remarks:       Free-text description attached to the transfer.
            transfer_type: "INTERNAL" (same bank) or "EXTERNAL" (default "INTERNAL").

        Returns:
            AzamPay response dict with transaction details.
        """
        payload = disburse_payload(
            source, destination, amount, reference_id, currency, remarks,
            transfer_type, self._c.rsa_public_key,
        )
        return self._c.request(  # type: ignore[no-any-return]
            "POST", _DISBURSE_PATH, json=payload, base_url=self._c.disburse_url, skip_checksum=True
        )

    def disburse_mobile(
        self,
        full_name: str,
        mobile_number: str,
        provider: str,
        amount: str,
        reference_id: str,
        source: dict[str, Any],
        currency: str = "TZS",
        remarks: str | None = None,
    ) -> dict[str, Any]:
        """Convenience wrapper — disburse to a mobile-money wallet.

        Args:
            full_name:     Recipient's full name.
            mobile_number: Recipient's mobile number (e.g. "0741234567").
            provider:      Mobile provider name (e.g. "Airtel", "Tigo", "Azampesa", "Vodacom", "Selcom").
            amount:        Amount to disburse as a string.
            reference_id:  Your unique reference ID (max 30 chars, required by API).
            source:        Source account dict with countryCode, fullName, bankName,
                           accountNumber, currency.
            currency:      ISO 4217 currency code (default "TZS").
            remarks:       Free-text description (optional).
        """
        destination = mobile_destination(full_name, mobile_number, provider, currency)
        return self.disburse(source=source, destination=destination, amount=amount,
                             reference_id=reference_id, currency=currency, remarks=remarks)

    def disburse_bank(
        self,
        full_name: str,
        account_number: str,
        bank_name: str,
        amount: str,
        reference_id: str,
        source: dict[str, Any],
        currency: str = "TZS",
        remarks: str | None = None,
        transfer_type: str = "EXTERNAL",
    ) -> dict[str, Any]:
        """Convenience wrapper — disburse to a bank account.

        Args:
            full_name:      Recipient's full name.
            account_number: Recipient's bank account number.
            bank_name:      Bank identifier (e.g. "CRDB", "NMB").
            amount:         Amount to disburse as a string.
            reference_id:   Your unique reference ID (max 30 chars, required by API).
            source:         Source account dict with countryCode, fullName, bankName,
                            accountNumber, currency.
            currency:       ISO 4217 currency code (default "TZS").
            remarks:        Free-text description (optional).
            transfer_type:  "INTERNAL" or "EXTERNAL" (default "EXTERNAL").
        """
        destination = bank_destination(full_name, account_number, bank_name, currency)
        return self.disburse(source=source, destination=destination, amount=amount,
                             reference_id=reference_id, currency=currency, remarks=remarks,
                             transfer_type=transfer_type)


class AsyncDisbursementService:
    """Asynchronous disbursement (payout) operations."""

    def __init__(self, client: "AsyncAzamPayClient") -> None:
        self._c = client

    async def disburse(
        self,
        source: dict[str, Any],
        destination: dict[str, Any],
        amount: str,
        reference_id: str,
        currency: str = "TZS",
        remarks: str | None = None,
        transfer_type: str = "INTERNAL",
    ) -> dict[str, Any]:
        """Send a disbursement to a bank account or mobile wallet."""
        payload = disburse_payload(
            source, destination, amount, reference_id, currency, remarks,
            transfer_type, self._c.rsa_public_key,
        )
        return await self._c.request(  # type: ignore[no-any-return]
            "POST", _DISBURSE_PATH, json=payload, base_url=self._c.disburse_url, skip_checksum=True
        )

    async def disburse_mobile(
        self,
        full_name: str,
        mobile_number: str,
        provider: str,
        amount: str,
        reference_id: str,
        source: dict[str, Any],
        currency: str = "TZS",
        remarks: str | None = None,
    ) -> dict[str, Any]:
        """Convenience wrapper — disburse to a mobile-money wallet."""
        destination = mobile_destination(full_name, mobile_number, provider, currency)
        return await self.disburse(source=source, destination=destination, amount=amount,
                                   reference_id=reference_id, currency=currency, remarks=remarks)

    async def disburse_bank(
        self,
        full_name: str,
        account_number: str,
        bank_name: str,
        amount: str,
        reference_id: str,
        source: dict[str, Any],
        currency: str = "TZS",
        remarks: str | None = None,
        transfer_type: str = "EXTERNAL",
    ) -> dict[str, Any]:
        """Convenience wrapper — disburse to a bank account."""
        destination = bank_destination(full_name, account_number, bank_name, currency)
        return await self.disburse(source=source, destination=destination, amount=amount,
                                   reference_id=reference_id, currency=currency, remarks=remarks,
                                   transfer_type=transfer_type)
