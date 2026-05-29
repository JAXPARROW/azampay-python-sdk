import json

import pytest
import respx
from httpx import Response

from azampay import AzamPay
from tests.conftest import SANDBOX_AUTH, SANDBOX_BASE

AUTH_URL = f"{SANDBOX_AUTH}/AppRegistration/GenerateToken"
DISBURSE_URL = f"{SANDBOX_BASE}/azampay/api/v1/Partner/PostDisburse"


def _auth_ok() -> Response:
    return Response(200, json={"success": True, "data": {"accessToken": "tok"}, "message": "OK"})


def _disburse_ok() -> Response:
    return Response(200, json={"success": True, "transactionId": "d1", "message": "Disbursement queued"})


@respx.mock
def test_disburse_raw_payload(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(DISBURSE_URL).mock(return_value=_disburse_ok())

    source = {"countryCode": "TZ", "fullName": "Corp", "bankName": "CRDB", "accountNumber": "111", "currency": "TZS"}
    dest = {"countryCode": "TZ", "fullName": "John", "bankName": "Airtel", "accountNumber": "0741234567", "currency": "TZS"}
    client.disbursement.disburse(source=source, destination=dest, amount="5000")

    body = json.loads(mock.calls[0].request.content)
    assert body["transferDetails"]["amount"] == "5000"
    assert body["transferDetails"]["currency"] == "TZS"
    assert body["source"]["accountNumber"] == "111"
    assert body["destination"]["accountNumber"] == "0741234567"


@respx.mock
def test_disburse_with_reference_and_remarks(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(DISBURSE_URL).mock(return_value=_disburse_ok())

    source = {"countryCode": "TZ", "fullName": "", "bankName": "", "accountNumber": "", "currency": "TZS"}
    dest = {"countryCode": "TZ", "fullName": "Jane", "bankName": "Tigo", "accountNumber": "0655555555", "currency": "TZS"}
    client.disbursement.disburse(
        source=source,
        destination=dest,
        amount="3000",
        reference_id="ref-99",
        remarks="Salary payment",
    )

    body = json.loads(mock.calls[0].request.content)
    assert body["referenceId"] == "ref-99"
    assert body["remarks"] == "Salary payment"


@respx.mock
def test_disburse_mobile_convenience(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(DISBURSE_URL).mock(return_value=_disburse_ok())

    client.disbursement.disburse_mobile(
        full_name="Alice",
        mobile_number="0741111111",
        provider="Airtel",
        amount="2000",
    )

    body = json.loads(mock.calls[0].request.content)
    assert body["destination"]["accountNumber"] == "0741111111"
    assert body["destination"]["bankName"] == "Airtel"
    assert body["destination"]["fullName"] == "Alice"


@respx.mock
def test_disburse_bank_convenience(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(DISBURSE_URL).mock(return_value=_disburse_ok())

    client.disbursement.disburse_bank(
        full_name="Bob",
        account_number="9876543210",
        bank_name="NMB",
        amount="10000",
        reference_id="pay-001",
    )

    body = json.loads(mock.calls[0].request.content)
    assert body["destination"]["accountNumber"] == "9876543210"
    assert body["destination"]["bankName"] == "NMB"
    assert body["transferDetails"]["type"] == "EXTERNAL"
    assert body["referenceId"] == "pay-001"


@respx.mock
def test_disburse_checksum_injected(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(DISBURSE_URL).mock(return_value=_disburse_ok())

    client.disbursement.disburse_mobile("Charlie", "0741222222", "Tigo", "500")

    body = json.loads(mock.calls[0].request.content)
    assert "checksum" in body
    assert len(body["checksum"]) == 64
