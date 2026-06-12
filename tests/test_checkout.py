import json

import pytest
import respx
from httpx import Response

from azampay import AzamPay, ValidationError
from tests.conftest import SANDBOX_AUTH, SANDBOX_BASE

AUTH_URL = f"{SANDBOX_AUTH}/AppRegistration/GenerateToken"
MNO_URL = f"{SANDBOX_BASE}/azampay/mno/checkout"
BANK_URL = f"{SANDBOX_BASE}/azampay/bank/checkout"
PARTNERS_URL = f"{SANDBOX_BASE}/api/v1/Partner/GetPaymentPartners"
POST_CHECKOUT_URL = f"{SANDBOX_BASE}/api/v1/Partner/PostCheckout"
PUBLIC_KEY_URL = f"{SANDBOX_BASE}/azampay/v1/public-key"


def _auth_ok() -> Response:
    return Response(200, json={"success": True, "data": {"accessToken": "tok"}, "message": "OK"})


@respx.mock
def test_mobile_checkout_payload(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(MNO_URL).mock(return_value=Response(200, json={"success": True, "transactionId": "t1"}))

    client.checkout.mobile_checkout("5000", "0741234567", "ord-1", "Airtel")

    body = json.loads(mock.calls[0].request.content)
    assert body["accountNumber"] == "0741234567"
    assert body["amount"] == "5000"
    assert body["currency"] == "TZS"
    assert body["externalId"] == "ord-1"
    assert body["provider"] == "Airtel"


@respx.mock
def test_mobile_checkout_default_currency(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(MNO_URL).mock(return_value=Response(200, json={"success": True}))

    client.checkout.mobile_checkout("1000", "0741234567", "ord-1", "Tigo")

    body = json.loads(mock.calls[0].request.content)
    assert body["currency"] == "TZS"


@respx.mock
def test_mobile_checkout_with_callback_url(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(MNO_URL).mock(return_value=Response(200, json={"success": True}))

    client.checkout.mobile_checkout(
        "1000", "0741234567", "ord-1", "MPESA", callback_url="https://myapp.com/callback"
    )

    body = json.loads(mock.calls[0].request.content)
    assert body["callbackUrl"] == "https://myapp.com/callback"


@respx.mock
def test_mobile_checkout_with_additional_properties(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(MNO_URL).mock(return_value=Response(200, json={"success": True}))

    client.checkout.mobile_checkout(
        "1000", "0741234567", "ord-1", "Airtel", additional_properties={"meta": "value"}
    )

    body = json.loads(mock.calls[0].request.content)
    assert body["additionalProperties"] == {"meta": "value"}


@respx.mock
def test_mobile_checkout_checksum_injected(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(MNO_URL).mock(return_value=Response(200, json={"success": True}))

    client.checkout.mobile_checkout("1000", "0741234567", "ord-1", "Airtel")

    body = json.loads(mock.calls[0].request.content)
    assert "checksum" in body
    assert len(body["checksum"]) == 64


@respx.mock
def test_mobile_checkout_raises_on_400(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    respx.post(MNO_URL).mock(return_value=Response(400, json={"message": "Invalid account number"}))

    with pytest.raises(ValidationError):
        client.checkout.mobile_checkout("1000", "bad", "ord-1", "Airtel")


@respx.mock
def test_bank_checkout_payload(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(BANK_URL).mock(return_value=Response(200, json={"success": True, "transactionId": "b1"}))

    client.checkout.bank_checkout(
        amount="20000",
        merchant_account_number="1234567890",
        merchant_mobile_number="0741234567",
        reference_id="ref-001",
        bank_name="CRDB",
        merchant_name="Test Merchant",
    )

    body = json.loads(mock.calls[0].request.content)
    assert body["merchantAccountNumber"] == "1234567890"
    assert body["merchantMobileNumber"] == "0741234567"
    assert body["referenceId"] == "ref-001"
    assert body["provider"] == "CRDB"
    assert body["merchantName"] == "Test Merchant"
    assert body["currencyCode"] == "TZS"


@respx.mock
def test_bank_checkout_optional_otp(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(BANK_URL).mock(return_value=Response(200, json={"success": True}))

    client.checkout.bank_checkout("10000", "acc-1", "0741234567", "ref-1", "NMB", otp="123456")

    body = json.loads(mock.calls[0].request.content)
    assert body["otp"] == "123456"


@respx.mock
def test_get_payment_partners(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    partners = [{"partnerName": "Airtel", "provider": "Airtel"}, {"partnerName": "Tigo", "provider": "Tigo"}]
    respx.get(PARTNERS_URL).mock(return_value=Response(200, json=partners))

    result = client.checkout.get_payment_partners()

    assert isinstance(result, list)
    assert result[0]["partnerName"] == "Airtel"


@respx.mock
def test_post_checkout_returns_url(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(POST_CHECKOUT_URL).mock(return_value=Response(200, json="https://checkout.azampay.co.tz/pay/abc123"))

    result = client.checkout.post_checkout(
        amount="5000",
        external_id="ord-123",
        redirect_success_url="https://myapp.com/success",
        redirect_fail_url="https://myapp.com/fail",
    )

    body = json.loads(mock.calls[0].request.content)
    assert body["amount"] == "5000"
    assert body["externalId"] == "ord-123"
    assert body["redirectSuccessURL"] == "https://myapp.com/success"
    assert body["redirectFailURL"] == "https://myapp.com/fail"
    assert body["currency"] == "TZS"
    assert body["language"] == "en"
    assert result == "https://checkout.azampay.co.tz/pay/abc123"


@respx.mock
def test_post_checkout_optional_fields_omitted(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    mock = respx.post(POST_CHECKOUT_URL).mock(return_value=Response(200, json="https://pay.example.com/x"))

    client.checkout.post_checkout(amount="1000", external_id="ord-1")

    body = json.loads(mock.calls[0].request.content)
    assert "appName" not in body
    assert "cart" not in body
    assert "vendorId" not in body


@respx.mock
def test_get_public_key(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    pem_response = {"success": True, "format": "Pem", "publicKey": "-----BEGIN PUBLIC KEY-----\nMIIB...\n-----END PUBLIC KEY-----\n"}
    mock = respx.get(PUBLIC_KEY_URL).mock(return_value=Response(200, json=pem_response))

    result = client.checkout.get_public_key()

    assert mock.calls[0].request.url.params["format"] == "Pem"
    assert result["format"] == "Pem"
    assert "publicKey" in result


@respx.mock
def test_get_public_key_xml_format(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_ok())
    respx.get(PUBLIC_KEY_URL).mock(return_value=Response(200, json={"success": True, "format": "Xml", "publicKey": "<RSAKeyValue/>"}))

    result = client.checkout.get_public_key(format="Xml")

    assert result["format"] == "Xml"
