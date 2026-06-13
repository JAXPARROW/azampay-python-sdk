from azampay import BillPayValidator

# Exact values from the AzamPay Bill Pay API documentation
_SECRET = "TRlWYMsr0GQU15REn6KRVn2DDv55MMW9VjLfpQn9RVg6m8QaCGNfY9IuGy6sCB1"

_NAME_LOOKUP_DATA = {
    "BillIdentifier": "123456789",
    "Currency": "TZS",
    "Language": "en",
    "Country": "Tanzania",
    "TimeStamp": "2024-06-12T10:20:30Z",
    "AdditionalProperties": {
        "key1": "value1",
        "key2": "value2",
        "property1": "string",
        "property2": "string",
    },
    "BillType": "Electricity",
}
_NAME_LOOKUP_HASH = "711bd3c3e54488523683182aa01c8a83544e45b7ba2c45652e039bf830e5daf2"

_PAYMENT_DATA = {
    "BillIdentifier": "123456789",
    "Currency": "TZS",
    "Language": "en",
    "Country": "Tanzania",
    "TimeStamp": "2024-06-12T10:20:30Z",
    "AdditionalProperties": {"key1": "value1", "key2": "value2"},
    "BillType": "Electricity",
}
_PAYMENT_HASH = "ca3f49b2ee7740bf68062445ee7027d33baa4dbb0e456cdc7534ddd34bf19fb1"


# ------------------------------------------------------------------
# Hash verification — name lookup
# ------------------------------------------------------------------

def test_name_lookup_hash_matches_documented_example() -> None:
    assert BillPayValidator.verify_hash(_NAME_LOOKUP_DATA, _NAME_LOOKUP_HASH, _SECRET) is True


def test_name_lookup_tampered_data_rejected() -> None:
    tampered = {**_NAME_LOOKUP_DATA, "BillIdentifier": "999999999"}
    assert BillPayValidator.verify_hash(tampered, _NAME_LOOKUP_HASH, _SECRET) is False


def test_name_lookup_wrong_secret_rejected() -> None:
    assert BillPayValidator.verify_hash(_NAME_LOOKUP_DATA, _NAME_LOOKUP_HASH, "wrong-secret") is False


def test_name_lookup_empty_hash_rejected() -> None:
    assert BillPayValidator.verify_hash(_NAME_LOOKUP_DATA, "", _SECRET) is False


def test_name_lookup_empty_secret_rejected() -> None:
    assert BillPayValidator.verify_hash(_NAME_LOOKUP_DATA, _NAME_LOOKUP_HASH, "") is False


# ------------------------------------------------------------------
# Hash verification — payment
# ------------------------------------------------------------------

def test_payment_hash_matches_documented_example() -> None:
    assert BillPayValidator.verify_hash(_PAYMENT_DATA, _PAYMENT_HASH, _SECRET) is True


def test_payment_tampered_amount_rejected() -> None:
    tampered = {**_PAYMENT_DATA, "BillType": "Water"}
    assert BillPayValidator.verify_hash(tampered, _PAYMENT_HASH, _SECRET) is False


# ------------------------------------------------------------------
# Response builders
# ------------------------------------------------------------------

def test_name_lookup_response_shape() -> None:
    resp = BillPayValidator.name_lookup_response("John Doe", 150.0, "123456789")
    assert resp["Name"] == "John Doe"
    assert resp["BillAmount"] == 150.0
    assert resp["BillIdentifier"] == "123456789"
    assert resp["Status"] == "Success"
    assert resp["StatusCode"] == 0


def test_name_lookup_response_custom_status() -> None:
    resp = BillPayValidator.name_lookup_response(
        "", 0, "xxx", status="Failed", message="Not found.", status_code=1
    )
    assert resp["Status"] == "Failed"
    assert resp["StatusCode"] == 1


def test_payment_response_shape() -> None:
    resp = BillPayValidator.payment_response("merchant-ref-001")
    assert resp["MerchantReferenceId"] == "merchant-ref-001"
    assert resp["Status"] == "Success"
    assert resp["StatusCode"] == 0
    assert resp["Message"] == "Payment successful."


def test_payment_response_failed() -> None:
    resp = BillPayValidator.payment_response("ref-002", status="Failed", message="Insufficient funds.", status_code=1)
    assert resp["Status"] == "Failed"
    assert resp["StatusCode"] == 1


def test_status_check_response_shape() -> None:
    resp = BillPayValidator.status_check_response("merchant-ref-001", "Pending")
    assert resp["MerchantReferenceId"] == "merchant-ref-001"
    assert resp["Status"] == "Pending"
    assert resp["StatusCode"] == 0


def test_status_check_response_success() -> None:
    resp = BillPayValidator.status_check_response("ref-003", "Success", "Payment confirmed.", 0)
    assert resp["Status"] == "Success"
    assert resp["Message"] == "Payment confirmed."
