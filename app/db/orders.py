from typing import List
from schemas.orders import OrderItem


def save_posted_orders(orders: List[OrderItem]):
    if not orders:
        return []

    posted_ids = set([e.order_id for e in orders])
    return list(posted_ids) # FIXME
