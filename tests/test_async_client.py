import pytest
import respx
from httpx import Response

from azampay import AsyncAzamPay, AzamPayError, AuthenticationError, ValidationError
from tests.conftest import SANDBOX_AUTH, SANDBOX_BASE

AUTH_URL = f"{SANDBOX_AUTH}/AppRegistration/GenerateToken"
CHECKOUT_URL = f"{SANDBOX_BASE}/azampay/mno/checkout"


def _auth_response() -> Response:
    return Response(200, json={"success": True, "data": {"accessToken": "mock_token_async"}, "message": "OK"})


@pytest.mark.asyncio
@respx.mock
async def test_async_token_fetched(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(200, json={"success": True, "transactionId": "tx-async"}))

    result = await async_client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")
    assert result["transactionId"] == "tx-async"


@pytest.mark.asyncio
@respx.mock
async def test_async_token_cached(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(200, json={"success": True, "transactionId": "tx1"}))

    await async_client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")
    await async_client.checkout.mobile_checkout("2000", "0741234567", "order-2", "Tigo")

    auth_calls = [c for c in respx.calls if AUTH_URL in str(c.request.url)]
    assert len(auth_calls) == 1


@pytest.mark.asyncio
@respx.mock
async def test_async_raises_authentication_error(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=Response(401, json={"message": "Bad credentials"}))

    with pytest.raises(AuthenticationError):
        await async_client._authenticate()


@pytest.mark.asyncio
@respx.mock
async def test_async_raises_validation_error(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(400, json={"message": "Invalid phone"}))

    with pytest.raises(ValidationError):
        await async_client.checkout.mobile_checkout("bad", "invalid", "order-1", "Airtel")


@pytest.mark.asyncio
@respx.mock
async def test_async_checksum_injected(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    mock_route = respx.post(CHECKOUT_URL).mock(return_value=Response(200, json={"success": True}))

    await async_client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")

    import json
    body = json.loads(mock_route.calls[0].request.content)
    assert "checksum" in body
    assert len(body["checksum"]) == 64


@pytest.mark.asyncio
@respx.mock
async def test_async_caller_dict_not_mutated(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(return_value=Response(200, json={"success": True}))

    original = {"accountNumber": "0741234567", "amount": "1000", "currency": "TZS", "externalId": "ord-1", "provider": "Airtel"}
    before = dict(original)
    await async_client.request("POST", "/azampay/mno/checkout", json=original)

    assert original == before


@pytest.mark.asyncio
@respx.mock
async def test_async_is_healthy(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    assert await async_client.is_healthy() is True


@pytest.mark.asyncio
@respx.mock
async def test_async_context_manager_closes_client(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    async with async_client:
        assert async_client._http is not None
    assert async_client._http.is_closed


@pytest.mark.asyncio
@respx.mock
async def test_async_success_false_raises(async_client: AsyncAzamPay) -> None:
    respx.post(AUTH_URL).mock(return_value=_auth_response())
    respx.post(CHECKOUT_URL).mock(
        return_value=Response(200, json={"success": False, "message": "Provider unavailable"})
    )

    with pytest.raises(AzamPayError):
        await async_client.checkout.mobile_checkout("1000", "0741234567", "order-1", "Airtel")
