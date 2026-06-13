"""AzamPay Python SDK — sync & async, mobile checkout, bank checkout, disbursements, and payment links."""

from ._version import __version__
from .async_client import AsyncAzamPayClient
from .bill_pay import BillPayValidator
from .client import AzamPayClient
from .exceptions import (
    AzamPayError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .security import SecurityManager
from .services import (
    AsyncCheckoutService,
    AsyncDisbursementService,
    AsyncLinkService,
    AsyncLookupService,
    CheckoutService,
    DisbursementService,
    LinkService,
    LookupService,
)
from .webhooks import WebhookValidator


class AzamPay(AzamPayClient):
    """Synchronous AzamPay client with service namespaces.

    Usage::

        with AzamPay(app_name="MyApp", client_id="...", client_secret="...", sandbox=True) as client:
            result = client.checkout.mobile_checkout(
                amount="5000",
                account_number="0741234567",
                external_id="order-001",
                provider="Airtel",
            )
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.checkout = CheckoutService(self)
        self.disbursement = DisbursementService(self)
        self.lookup = LookupService(self)
        self.links = LinkService(self)


class AsyncAzamPay(AsyncAzamPayClient):
    """Asynchronous AzamPay client with service namespaces.

    Usage::

        async with AsyncAzamPay(app_name="MyApp", client_id="...", client_secret="...", sandbox=True) as client:
            result = await client.checkout.mobile_checkout(
                amount="5000",
                account_number="0741234567",
                external_id="order-001",
                provider="Airtel",
            )
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.checkout = AsyncCheckoutService(self)
        self.disbursement = AsyncDisbursementService(self)
        self.lookup = AsyncLookupService(self)
        self.links = AsyncLinkService(self)


__all__ = [
    # Top-level clients
    "AzamPay",
    "AsyncAzamPay",
    # Base clients (for subclassing)
    "AzamPayClient",
    "AsyncAzamPayClient",
    # Utilities
    "SecurityManager",
    "WebhookValidator",
    "BillPayValidator",
    # Exceptions
    "AzamPayError",
    "AuthenticationError",
    "ForbiddenError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    # Services
    "CheckoutService",
    "AsyncCheckoutService",
    "DisbursementService",
    "AsyncDisbursementService",
    "LookupService",
    "AsyncLookupService",
    "LinkService",
    "AsyncLinkService",
    # Version
    "__version__",
]
