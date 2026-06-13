import pytest
import respx
from httpx import Response

from azampay import AzamPay, AzamPayError, AuthenticationError, ForbiddenError, NotFoundError, RateLimitError, ServerError, ValidationError
from tests.conftest import SANDBOX_AUTH, SANDBOX_BASE, SANDBOX_DISBURSE

AUTH_URL = f"{SANDBOX_AUTH}/AppRegistration/GenerateToken"
CHECKOUT_URL = f"{SANDBOX_BASE}/azampay/mno/checkout"


def _auth_response() -> Response:
    return Response(200, json={"success": True, "data": {"accessToken": "mock_token_123"}, "message": "OK"})


@respx.mock
def test_token_fetched_on_first_request(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(200, json={"success": True, "transactionId": "tx1"}))

    client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")

    assert respx.calls.call_count == 2


@respx.mock
def test_token_cached_across_requests(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(200, json={"success": True, "transactionId": "tx1"}))

    client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")
    client.checkout.mobile_checkout("2000", "0741234567", "order-2", "Tigo")

    auth_calls = [c for c in respx.calls if AUTH_URL in str(c.request.url)]
    assert len(auth_calls) == 1


@respx.mock
def test_raises_authentication_error_on_401(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=Response(401, json={"message": "Invalid credentials"}))

    with pytest.raises(AuthenticationError) as exc_info:
        client._authenticate()

    assert exc_info.value.status_code == 401


@respx.mock
def test_raises_forbidden_error_on_auth_403(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=Response(403, json={"message": "Forbidden"}))

    with pytest.raises(ForbiddenError):
        client._authenticate()


@respx.mock
def test_raises_validation_error_on_400(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(400, json={"message": "Invalid amount"}))

    with pytest.raises(ValidationError) as exc_info:
        client.checkout.mobile_checkout("bad", "0741234567", "order-1", "Airtel")

    assert exc_info.value.status_code == 400


@respx.mock
def test_raises_not_found_error_on_404(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    status_url = f"{SANDBOX_DISBURSE}/api/v1/azampay/transactionstatus"
    respx.get(status_url).mock(return_value=Response(404, json={"message": "Not found"}))

    with pytest.raises(NotFoundError):
        client.lookup.transaction_status(pg_reference_id="unknown")


@respx.mock
def test_raises_rate_limit_error_on_429(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(429, json={"message": "Too many requests"}))

    with pytest.raises(RateLimitError):
        client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")


@respx.mock
def test_raises_server_error_on_5xx(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(
        side_effect=[
            Response(500, json={"message": "Internal server error"}),
            Response(500, json={"message": "Internal server error"}),
            Response(500, json={"message": "Internal server error"}),
        ]
    )
    client.max_retries = 3

    with pytest.raises(ServerError):
        client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")


@respx.mock
def test_retries_on_5xx_and_succeeds(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(
        side_effect=[
            Response(503, json={"message": "Unavailable"}),
            Response(200, json={"success": True, "transactionId": "tx-ok"}),
        ]
    )
    client.max_retries = 3

    result = client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")
    assert result["transactionId"] == "tx-ok"


@respx.mock
def test_x_api_key_sent_in_header(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    mock_route = respx.post(CHECKOUT_URL).mock(
        return_value=Response(200, json={"success": True, "transactionId": "tx1"})
    )

    client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")

    request = mock_route.calls[0].request
    assert request.headers.get("X-API-Key") == "test_x_api_key"


@respx.mock
def test_checksum_injected_on_post(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    mock_route = respx.post(CHECKOUT_URL).mock(
        return_value=Response(200, json={"success": True, "transactionId": "tx1"})
    )

    client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")

    import json
    body = json.loads(mock_route.calls[0].request.content)
    assert "checksum" in body
    assert len(body["checksum"]) == 64


@respx.mock
def test_caller_dict_not_mutated(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(200, json={"success": True}))

    original = {"accountNumber": "0741234567", "amount": "1000", "currency": "TZS", "externalId": "ord-1", "provider": "Airtel"}
    before = dict(original)
    client.request("POST", "/azampay/mno/checkout", json=original)

    assert original == before


@respx.mock
def test_is_healthy_returns_true(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    assert client.is_healthy() is True


@respx.mock
def test_is_healthy_returns_false_on_auth_failure(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=Response(401, json={"message": "Bad creds"}))
    assert client.is_healthy() is False


@respx.mock
def test_context_manager_closes_client(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    with client:
        assert client._http is not None
    assert client._http.is_closed


@respx.mock
def test_exception_carries_response_payload(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(400, json={"message": "Bad amount", "code": "E001"}))

    with pytest.raises(ValidationError) as exc_info:
        client.checkout.mobile_checkout("bad", "0741234567", "order-1", "Airtel")

    assert exc_info.value.response["code"] == "E001"


@respx.mock
def test_success_false_body_raises_azampay_error(client: AzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(
        return_value=Response(200, json={"success": False, "message": "Provider unavailable"})
    )

    with pytest.raises(AzamPayError):
        client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")
