from typing import List
from datetime import datetime
from decimal import Decimal

from schemas.couriers import CourierItem, CourierTypeEnum
from schemas.orders import OrderStatusEnum
from sqlalchemy import select
from sqlalchemy.sql import func
from utils.time import can_be_delivered_in_time
from .schema import (
    tbl_couriers,
    tbl_orders,
    tbl_deliveries,
    tbl_deliveries_orders
)
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
            for k, v in data.items():
                courier_info[k] = v
            connection.execute(
                tbl_couriers.update().values(**courier_info).where(
                    tbl_couriers.c.courier_id == courier_id
                )
            )

            # TODO: remove assigned orders (if any) that got unfit
            #       upon courier info alteration

            # check if the uncompleted delivery exists for the courier
            ds = select(
                [tbl_deliveries]
            ).where(
                (tbl_deliveries.c.courier_id == courier_id) &
                (tbl_deliveries.c.status == OrderStatusEnum.assigned)
            )
            result = connection.execute(ds)
            row = result.fetchone()

            # if the uncompleted delivery exists, return all assigned,
            # but not completed orders
            if row:
                delivery_id = row['delivery_id']
                us = select(
                    [tbl_orders]
                ).where(
                    (tbl_orders.c.status == OrderStatusEnum.assigned) &
                    (tbl_deliveries.c.delivery_id == delivery_id) &
                    (tbl_orders.c.order_id == tbl_deliveries_orders.c.order_id) &
                    (tbl_deliveries.c.delivery_id == tbl_deliveries_orders.c.delivery_id)
                ).order_by(tbl_orders.c.weight)
                result = connection.execute(us)
                rows = result.fetchall()
                if rows:
                    orders_good = []
                    orders_bad = []
                    total_weight = Decimal('0.0')
                    assign_time = datetime.now()
                    for order in rows:
                        if order['region'] not in courier_info['regions']:
                            orders_bad.append(order)
                        elif order['weight'] > CourierTypeEnum.max_weight(courier_info['courier_type']):
                            orders_bad.append(order)
                        elif not can_be_delivered_in_time(assign_time.strftime('%H:%M'),
                            courier_info['working_hours'], order['delivery_hours']):
                            orders_bad.append(order)
                        elif total_weight + order['weight'] > CourierTypeEnum.max_weight(courier_info['courier_type']):
                            orders_bad.append(order)
                        else:
                            orders_good.append(order)

                    # release unfit orders
                    if orders_bad:
                        bad_ids = [e['order_id'] for e in orders_bad]
                        connection.execute(
                            tbl_orders.update().values(
                                status=OrderStatusEnum.pending,
                                completed_at=None
                            ).where(tbl_orders.c.order_id.in_(bad_ids))
                        )
                        connection.execute(
                            tbl_deliveries_orders.delete(
                            ).where(
                                (tbl_deliveries_orders.c.order_id.in_(bad_ids)) &
                                (tbl_deliveries_orders.c.delivery_id == delivery_id)
                            )
                        )

                        # check if the delivery empty (both assigned and
                        # completed orders are absent) and delete it
                        eds = select(
                            [tbl_deliveries_orders]
                        ).where(
                            tbl_deliveries_orders.c.delivery_id == delivery_id
                        )
                        result = connection.execute(eds)
                        rows = result.fetchall()
                        if not rows:
                            connection.execute(
                                tbl_deliveries.delete(
                                ).where(
                                    tbl_deliveries.c.delivery_id == delivery_id
                                )
                            )
    return courier_info


def get_courier_info(courier_id: int):
    with engine.connect() as connection:
        s = select(
            [tbl_couriers]
        ).where(
            tbl_couriers.c.courier_id == courier_id
        )
        result = connection.execute(s)
        row = result.fetchone()
        if row is None:
            return None
        courier_info = dict(row)

        # calculate earnings based on completed deliveries
        result = connection.execute(
            select(
                func.sum(tbl_deliveries.c.coeff)
            ).where(
                (tbl_deliveries.c.courier_id == courier_id) &
                (tbl_deliveries.c.status == OrderStatusEnum.completed)
            )
        ).scalar()
        courier_info['earnings'] = 0
        if result:
            courier_info['earnings'] = result * 500
        return courier_info
