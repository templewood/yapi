from typing import List
from datetime import datetime
from decimal import Decimal

from schemas.orders import OrderItem, OrderStatusEnum
from schemas.couriers import CourierTypeEnum
from sqlalchemy import select
from utils.time import can_be_delivered_in_time
from .schema import tbl_couriers, tbl_orders, tbl_deliveries, tbl_deliveries_orders
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


def assign_orders(courier_id: int):
    with engine.connect() as connection:
        # check if courier_id exists and get courier info
        cs = select(
            [tbl_couriers]
        ).where(
            tbl_couriers.c.courier_id == courier_id
        )
        result = connection.execute(cs)
        row = result.fetchone()
        if row is None:
            return None
        courier_info = dict(row)

        # check if the uncompleted delivery exists for the courier
        ds = select(
            [tbl_deliveries]
        ).where(
            (tbl_deliveries.c.courier_id == courier_id) &
            (tbl_deliveries.c.status == OrderStatusEnum.assigned)
        )
        result = connection.execute(ds)
        row = result.fetchone()

        # if the uncompleted delivery exists, return all assigned, but not completed order ids
        if row:
            us = select(
                [tbl_orders.c.order_id]
            ).where(
                (tbl_orders.c.status == OrderStatusEnum.assigned) &
                (tbl_deliveries.c.delivery_id == row['delivery_id']) &
                (tbl_orders.c.order_id == tbl_deliveries_orders.c.order_id) &
                (tbl_deliveries.c.delivery_id == tbl_deliveries_orders.c.delivery_id)
            )
            result = connection.execute(us)
            rows = [e['order_id'] for e in result.fetchall()]
            return { "orders": list([{"id": x} for x in rows]),
                 "assign_time": row['assigned_at'].isoformat(sep=' ', timespec='milliseconds')[:-1] }

        # find kinda suitable orders (pending & properly located & proper item weight)
        t = select(
            [tbl_orders]
        ).where(
            (tbl_orders.c.status == OrderStatusEnum.pending) &
            (tbl_orders.c.region.in_(courier_info['regions'])) &
            (tbl_orders.c.weight <= CourierTypeEnum.max_weight(courier_info['courier_type']))
        ).order_by(tbl_orders.c.weight
        ).with_for_update()
        result = connection.execute(t)

        # select fully suitable orders (right scheduled & proper total weight)
        good_order_ids = []
        total_weight = Decimal('0.0')
        assign_time = datetime.now()
        for order_row in result:
            if can_be_delivered_in_time(assign_time.strftime('%H:%M'),
                                        courier_info['working_hours'],
                                        order_row['delivery_hours']):
                if total_weight + order_row['weight'] > CourierTypeEnum.max_weight(courier_info['courier_type']):
                    break
                good_order_ids.append(order_row['order_id'])
                total_weight += order_row['weight']
        if not good_order_ids:
            return []

        # mark chosen orders as assigned (and release previously locked orders entries)
        connection.execute(
            tbl_orders.update().values(status=OrderStatusEnum.assigned,
            ).where(tbl_orders.c.order_id.in_(good_order_ids))
        )

        # create delivery entry
        result = connection.execute(tbl_deliveries.insert(), [{
                "courier_id" : courier_info['courier_id'],
                "assigned_at": assign_time.isoformat(sep=' ', timespec='milliseconds')[:-1],
                "coeff": CourierTypeEnum.get_coeff(courier_info['courier_type'])
        }])

        # create many-to-many relation between the created delivery and the assigned orders
        rows_m2m = [ {  "delivery_id": result.inserted_primary_key[0],
                        "order_id": i } for i in good_order_ids]
        connection.execute(tbl_deliveries_orders.insert(), rows_m2m)

        return { "orders": list([{"id": x} for x in good_order_ids]),
                 "assign_time": assign_time.isoformat(sep=' ', timespec='milliseconds')[:-1] }


def complete_order(courier_id: int, order_id: int, complete_time: str):
    with engine.connect() as connection:
        s = select(
            [tbl_orders.c.order_id, tbl_orders.c.status, tbl_deliveries.c.delivery_id]
        ).where(
            (tbl_orders.c.order_id == order_id) &
            (tbl_deliveries.c.courier_id == courier_id) &
            (tbl_orders.c.order_id == tbl_deliveries_orders.c.order_id) &
            (tbl_deliveries.c.delivery_id == tbl_deliveries_orders.c.delivery_id)
        )
        result = connection.execute(s)
        row = result.fetchone()

        # nonexistent / unassigned / belonging to another courier's delivery
        if row is None:
            return None

        # already completed order
        if row['status'] == OrderStatusEnum.completed:
            return order_id

        # mark the order as completed
        delivery_id = row['delivery_id']
        complete_time = datetime.strptime(complete_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        connection.execute(
            tbl_orders.update().values(
                status=OrderStatusEnum.completed,
                completed_at=complete_time.isoformat(sep=' ', timespec='milliseconds')[:-1]
            ).where(tbl_orders.c.order_id == order_id)
        )

        # check if it was the last completed order in the current delivery
        t = select(
            [tbl_orders.c.order_id]
        ).where(
            (tbl_orders.c.status == OrderStatusEnum.assigned) &
            (tbl_deliveries.c.delivery_id == delivery_id) &
            (tbl_orders.c.order_id == tbl_deliveries_orders.c.order_id) &
            (tbl_deliveries.c.delivery_id == tbl_deliveries_orders.c.delivery_id)
        )
        result = connection.execute(t)
        rows = result.fetchall()

        # All orders in the current delivery have been completed
        # Finalize the current delivery
        if not rows:
            connection.execute(
                tbl_deliveries.update().values(
                    status=OrderStatusEnum.completed
                ).where(tbl_deliveries.c.delivery_id == delivery_id)
            )
    return order_id
