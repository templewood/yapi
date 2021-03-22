from typing import List
from schemas.couriers import CourierItem


def save_posted_couriers(couriers: List[CourierItem]):
    if not couriers:
        return []

    posted_ids = set([e.courier_id for e in couriers])
    return list(posted_ids) # FIXME


def update_courier(courier_id: int, data):
    dummy = {
        "courier_type": "foot",
        "regions": [11, 33, 2],
        "working_hours": ["09:00-18:00"]
    }
    return dummy
