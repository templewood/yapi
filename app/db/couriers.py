from typing import List
from schemas.couriers import CourierItem
from sqlalchemy import select
from .schema import tbl_couriers, tbl_orders
from .db import engine


def save_posted_couriers(couriers: List[CourierItem]):
    if not couriers:
        return []

    posted_ids = set([e.courier_id for e in couriers])

    with engine.connect() as connection:
        # get existing courier ids
        s = select(
            [tbl_couriers.c.courier_id]
        ).where(
            tbl_couriers.c.courier_id.in_(posted_ids)
        )
        result = connection.execute(s)
        existing_ids = set([row[0] for row in result])

        # get posted but not existing ids
        new_ids = list(posted_ids - existing_ids)

        data_to_db = [e.dict() for e in couriers if e.courier_id in new_ids]
        if data_to_db:
            connection.execute(tbl_couriers.insert(), data_to_db)
            return new_ids
    return []


def update_courier(courier_id: int, data):
    with engine.connect() as connection:
        s = select(
            [
                tbl_couriers.c.courier_type,
                tbl_couriers.c.regions,
                tbl_couriers.c.working_hours
            ]
        ).where(
            tbl_couriers.c.courier_id == courier_id
        )
        result = connection.execute(s)
        row = result.fetchone()

        if row is None:
            return None

        courier_info = dict(row)

        if data:
            # TODO: remove assigned orders (if any) that got unfit
            #       upon courier info alteration
            for k, v in data.items():
                courier_info[k] = v
            connection.execute(
                tbl_couriers.update().values(**courier_info
                ).where(
                    tbl_couriers.c.courier_id == courier_id
                )
            )
    return courier_info
