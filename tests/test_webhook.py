from azampay import SecurityManager, WebhookValidator

CHECKSUM_KEY = "my-secret-key"
PAYLOAD = {
    "transactionId": "tx-abc",
    "externalId": "order-42",
    "amount": "10000",
    "currency": "TZS",
    "provider": "Airtel",
    "status": "SUCCESS",
}


def test_valid_signature_accepted() -> None:
    sig = SecurityManager.create_checksum(CHECKSUM_KEY, PAYLOAD)
    assert WebhookValidator.verify(PAYLOAD, sig, CHECKSUM_KEY) is True


def test_wrong_signature_rejected() -> None:
    assert WebhookValidator.verify(PAYLOAD, "wrong" * 10, CHECKSUM_KEY) is False


def test_tampered_payload_rejected() -> None:
    sig = SecurityManager.create_checksum(CHECKSUM_KEY, PAYLOAD)
    tampered = {**PAYLOAD, "amount": "99999"}
    assert WebhookValidator.verify(tampered, sig, CHECKSUM_KEY) is False


def test_wrong_key_rejected() -> None:
    sig = SecurityManager.create_checksum(CHECKSUM_KEY, PAYLOAD)
    assert WebhookValidator.verify(PAYLOAD, sig, "wrong-key") is False


def test_empty_signature_rejected() -> None:
    assert WebhookValidator.verify(PAYLOAD, "", CHECKSUM_KEY) is False


def test_empty_key_returns_empty_string() -> None:
    assert SecurityManager.create_checksum("", PAYLOAD) == ""


def test_checksum_is_64_char_hex() -> None:
    sig = SecurityManager.create_checksum(CHECKSUM_KEY, PAYLOAD)
    assert len(sig) == 64
    assert all(c in "0123456789abcdef" for c in sig)


def test_sorted_key_order_produces_same_checksum() -> None:
    reversed_payload = {k: PAYLOAD[k] for k in reversed(list(PAYLOAD.keys()))}
    sig1 = SecurityManager.create_checksum(CHECKSUM_KEY, PAYLOAD)
    sig2 = SecurityManager.create_checksum(CHECKSUM_KEY, reversed_payload)
    assert sig1 == sig2


def test_nested_payload_canonicalized() -> None:
    nested = {"z": "last", "a": "first", "data": {"z": 2, "a": 1}}
    nested_rev = {"data": {"z": 2, "a": 1}, "z": "last", "a": "first"}
    sig1 = SecurityManager.create_checksum(CHECKSUM_KEY, nested)
    sig2 = SecurityManager.create_checksum(CHECKSUM_KEY, nested_rev)
    assert sig1 == sig2


def test_real_webhook_structure() -> None:
    webhook = {
        "event": "payment.completed",
        "data": {
            "transactionId": "tx-xyz",
            "externalId": "order-101",
            "amount": "5000",
            "currency": "TZS",
            "provider": "MPESA",
            "status": "SUCCESS",
        },
    }
    sig = SecurityManager.create_checksum(CHECKSUM_KEY, webhook)
    assert WebhookValidator.verify(webhook, sig, CHECKSUM_KEY) is True
