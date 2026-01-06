from typing import Any, Dict, List, Optional, Tuple


DEFAULT_CURRENCY = "USD"

TAX_RATE = 0.21

SAVE10_DISCOUNT = 0.10

SAVE20_HIGH_DISCOUNT = 0.20
SAVE20_LOW_DISCOUNT = 0.05
SAVE20_MIN_SUBTOTAL = 200

VIP_HIGH_DISCOUNT = 50
VIP_LOW_DISCOUNT = 10
VIP_MIN_SUBTOTAL = 100


def parse_request(request: dict) -> Tuple[Any, Any, Any, Any]:
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)

    currency = normalize_currency(currency)
    validate_request(user_id, items)

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, coupon)

    total_after_discount = ensure_non_negative(subtotal - discount)
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    order_id = generate_order_id(user_id, len(items))

    return build_response(
        order_id=order_id,
        user_id=user_id,
        currency=currency,
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        total=total,
        items_count=len(items),
    )


def normalize_currency(currency: Optional[str]) -> str:
    if currency is None:
        return DEFAULT_CURRENCY
    return currency


def validate_request(user_id: Any, items: Any) -> None:
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")

    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    validate_items(items)


def validate_items(items: List[Dict[str, Any]]) -> None:
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")


def calculate_subtotal(items: List[Dict[str, Any]]) -> int:
    subtotal = 0
    for item in items:
        subtotal += item["price"] * item["qty"]
    return subtotal


def calculate_discount(subtotal: int, coupon: Any) -> int:
    if coupon is None or coupon == "":
        return 0

    if coupon == "SAVE10":
        return int(subtotal * SAVE10_DISCOUNT)

    if coupon == "SAVE20":
        if subtotal >= SAVE20_MIN_SUBTOTAL:
            return int(subtotal * SAVE20_HIGH_DISCOUNT)
        return int(subtotal * SAVE20_LOW_DISCOUNT)

    if coupon == "VIP":
        if subtotal < VIP_MIN_SUBTOTAL:
            return VIP_LOW_DISCOUNT
        return VIP_HIGH_DISCOUNT

    raise ValueError("unknown coupon")


def ensure_non_negative(value: int) -> int:
    if value < 0:
        return 0
    return value


def calculate_tax(amount: int) -> int:
    return int(amount * TAX_RATE)


def generate_order_id(user_id: Any, items_count: int) -> str:
    return f"{user_id}-{items_count}-X"


def build_response(
    *,
    order_id: str,
    user_id: Any,
    currency: str,
    subtotal: int,
    discount: int,
    tax: int,
    total: int,
    items_count: int,
) -> dict:
    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": items_count,
    }
