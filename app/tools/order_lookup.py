import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ORDERS_PATH = PROJECT_ROOT / "data" / "orders.json"


# Fields that are safe to expose to the customer-facing agent.
SAFE_ORDER_FIELDS = {
    "order_id",
    "items",
    "placed_at",
    "status",
    "status_updated_at",
    "shipped_at",
    "delivered_at",
    "carrier",
    "tracking_number",
    "estimated_delivery",
    "customer_safe_message",
}


def load_orders() -> list[dict[str, Any]]:
    """Load the mock order dataset."""

    if not ORDERS_PATH.exists():
        raise FileNotFoundError(
            f"Order dataset not found: {ORDERS_PATH}"
        )

    data = json.loads(
        ORDERS_PATH.read_text(encoding="utf-8")
    )

    return data["orders"]


def lookup_order(order_id: str) -> dict[str, Any] | None:
    """
    Look up an order and return only customer-safe information.

    Internal fields such as risk scores, warehouse notes,
    and support tags are deliberately excluded.
    """

    order_id = order_id.strip().upper()

    for order in load_orders():
        if order.get("order_id") != order_id:
            continue

        safe_order = {
            key: order[key]
            for key in SAFE_ORDER_FIELDS
            if key in order
        }

        return safe_order

    return None