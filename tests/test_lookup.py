import json

import pytest
import respx
from httpx import Response

from azampay import AzamPay, NotFoundError
from tests.conftest import SANDBOX_AUTH, SANDBOX_DISBURSE

AUTH_URL = f"{SANDBOX_AUTH}/AppRegistration/GenerateToken"
STATUS_URL = f"{SANDBOX_DISBURSE}/api/v1/azampay/transactionstatus"
NAME_LOOKUP_URL = f"{SANDBOX_DISBURSE}/api/v1/azampay/namelookup"


def _auth_ok() -> Response:
    return Response(200, json={"success": True, "data": {"accessToken": "tok"}, "message": "OK"})


@respx.mock
def test_transaction_status_by_pg_reference(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.get(STATUS_URL).mock(
        return_value=Response(200, json={"success": True, "status": "SUCCESS", "transactionId": "pg-123"})
    )

    result = client.lookup.transaction_status(pg_reference_id="pg-123")

    assert result["status"] == "SUCCESS"
    assert "pgReferenceId=pg-123" in str(mock.calls[0].request.url)


@respx.mock
def test_transaction_status_by_external_id(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.get(STATUS_URL).mock(
        return_value=Response(200, json={"success": True, "status": "PENDING"})
    )

    client.lookup.transaction_status(external_id="order-99")

    assert "externalId=order-99" in str(mock.calls[0].request.url)


def test_transaction_status_raises_without_identifiers(client: AzamPay) -> None:
    with pytest.raises(ValueError, match="at least one"):
        client.lookup.transaction_status()


@respx.mock
def test_transaction_status_404(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    respx.get(STATUS_URL).mock(return_value=Response(404, json={"message": "Transaction not found"}))

    with pytest.raises(NotFoundError):
        client.lookup.transaction_status(pg_reference_id="bad-id")


@respx.mock
def test_name_lookup_payload(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(NAME_LOOKUP_URL).mock(
        return_value=Response(200, json={"success": True, "accountName": "John Doe"})
    )

    result = client.lookup.name_lookup("CRDB", "1234567890")

    assert result["accountName"] == "John Doe"
    body = json.loads(mock.calls[0].request.content)
    assert body["bankName"] == "CRDB"
    assert body["accountNumber"] == "1234567890"
