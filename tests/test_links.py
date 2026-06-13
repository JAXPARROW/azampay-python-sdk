import json

import respx
from httpx import Response

from azampay import AzamPay
from tests.conftest import SANDBOX_AUTH, SANDBOX_BASE

AUTH_URL = f"{SANDBOX_AUTH}/AppRegistration/GenerateToken"
LIST_URL = f"{SANDBOX_BASE}/azampay/api/v1/Partner/GetPaymentLinks"
CREATE_URL = f"{SANDBOX_BASE}/azampay/api/v1/Partner/CreatePaymentLink"
PAYMENTS_URL = f"{SANDBOX_BASE}/azampay/api/v1/Partner/GetLinkPayments"


def _auth_ok() -> Response:
    return Response(200, json={"success": True, "data": {"accessToken": "tok"}, "message": "OK"})


@respx.mock
def test_list_links(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    respx.get(LIST_URL).mock(
        return_value=Response(200, json={"success": True, "data": [{"linkCode": "LC1"}, {"linkCode": "LC2"}]})
    )

    result = client.links.list_links()

    assert len(result) == 2
    assert result[0]["linkCode"] == "LC1"


@respx.mock
def test_create_link_payload(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(CREATE_URL).mock(
        return_value=Response(200, json={"success": True, "linkCode": "LC3", "paymentLink": "https://pay.azampay.co.tz/LC3"})
    )

    result = client.links.create_link(
        amount="10000",
        link_name="School Fees",
        description="Term 1 fees",
        expiry_date="2025-12-31",
    )

    assert result["linkCode"] == "LC3"
    body = json.loads(mock.calls[0].request.content)
    assert body["amount"] == "10000"
    assert body["linkName"] == "School Fees"
    assert body["description"] == "Term 1 fees"
    assert body["expiryDate"] == "2025-12-31"
    assert body["currency"] == "TZS"


@respx.mock
def test_create_link_default_currency(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(CREATE_URL).mock(return_value=Response(200, json={"success": True}))

    client.links.create_link(amount="5000")

    body = json.loads(mock.calls[0].request.content)
    assert body["currency"] == "TZS"


@respx.mock
def test_create_link_checksum_injected(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(CREATE_URL).mock(return_value=Response(200, json={"success": True}))

    client.links.create_link(amount="5000")

    body = json.loads(mock.calls[0].request.content)
    assert "checksum" in body
    assert len(body["checksum"]) == 64


@respx.mock
def test_get_link_payments(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.get(PAYMENTS_URL).mock(
        return_value=Response(200, json={"success": True, "data": [{"transactionId": "tx-lp1"}]})
    )

    result = client.links.get_link_payments("LC3")

    assert result[0]["transactionId"] == "tx-lp1"
    assert "LinkCode=LC3" in str(mock.calls[0].request.url)
