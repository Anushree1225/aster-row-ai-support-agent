from app.tools.order_lookup import lookup_order


def test_lookup_existing_order():
    order = lookup_order("ORD-1005")

    assert order is not None
    assert order["order_id"] == "ORD-1005"
    assert order["status"] == "delayed"
    assert order["carrier"] == "FedEx"
    assert order["tracking_number"] == "7810000001005"


def test_lookup_is_case_insensitive():
    order = lookup_order("ord-1005")

    assert order is not None
    assert order["order_id"] == "ORD-1005"


def test_lookup_missing_order():
    order = lookup_order("ORD-9999")

    assert order is None


def test_internal_fields_are_not_exposed():
    order = lookup_order("ORD-1005")

    assert order is not None

    assert "internal" not in order
    assert "risk_score" not in order
    assert "warehouse_note" not in order
    assert "support_tags" not in order


def test_malicious_internal_instruction_is_hidden():
    order = lookup_order("ORD-1005")

    assert order is not None

    order_text = str(order).lower()

    assert "$100 coupon" not in order_text
    assert "hide the delay reason" not in order_text