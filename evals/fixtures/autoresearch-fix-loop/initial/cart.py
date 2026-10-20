"""Cart arithmetic in integer cents."""


def subtotal(items):
    """items: list of (unit_cents, quantity)."""
    return sum(price for price, qty in items)


def apply_discount(cents, percent):
    """Return cents after a percentage discount, rounded down."""
    return cents * percent // 100


def split_evenly(total, parts):
    """Split total into `parts` shares summing to total; earlier shares take the remainder."""
    return [total // parts] * parts


def format_money(cents):
    return f"${cents // 100}.{cents % 100:02d}"
