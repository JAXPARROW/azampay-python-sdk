import pytest

from azampay import AsyncAzamPay, AzamPay

SANDBOX_BASE = "https://sandbox.azampay.co.tz"
SANDBOX_AUTH = "https://authenticator-sandbox.azampay.co.tz"
MOCK_TOKEN = "Bearer mock_token_123"


@pytest.fixture
def client() -> AzamPay:
    return AzamPay(
        app_name="TestApp",
        client_id="test_client_id",
        client_secret="test_client_secret",
        x_api_key="test_x_api_key",
        sandbox=True,
    )


@pytest.fixture
def async_client() -> AsyncAzamPay:
    return AsyncAzamPay(
        app_name="TestApp",
        client_id="test_client_id",
        client_secret="test_client_secret",
        x_api_key="test_x_api_key",
        sandbox=True,
    )
