from typing import List
from schemas.orders import OrderItem
from sqlalchemy import select
from .schema import tbl_couriers, tbl_orders
from .db import engine

def save_posted_orders(orders: List[OrderItem]):
    if not orders:
        return []

    posted_ids = set([e.order_id for e in orders])

    with engine.connect() as connection:
        # get existing order ids
        s = select(
            [tbl_orders.c.order_id]
        ).where(
            tbl_orders.c.order_id.in_(posted_ids)
        )
        result = connection.execute(s)
        existing_ids = set([row[0] for row in result])

        # get posted but not existing ids
        new_ids = list(posted_ids - existing_ids)

        data_to_db = [e.dict() for e in orders if e.order_id in new_ids]
        if data_to_db:
            connection.execute(tbl_orders.insert(), data_to_db)
            return new_ids
    return []
