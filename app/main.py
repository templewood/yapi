from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pydantic import ValidationError, PositiveInt

from config import settings
from exceptions import CouriersLoadException, OrdersLoadException
from schemas.couriers import (
    CouriersPostRequest,
    CourierItem,
    CourierUpdateRequest
)
from schemas.orders import (
    OrdersPostRequest,
    OrderItem,
    OrdersAssignPostRequest,
    OrdersCompletePostRequest
)
from utils.time import validate_hours_input
from db.couriers import save_posted_couriers, update_courier, get_courier_info
from db.orders import save_posted_orders, assign_orders, complete_order

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    details = ''
    if request.url.path.startswith('/couriers'):
        if request.method == 'POST':
            details = {"validation_error": {
                "couriers": []
            }}
    elif request.url.path.startswith(
            '/orders/complete') or request.url.path.startswith(
            '/orders/assign'):
        pass
    elif request.url.path.startswith('/orders'):
        if request.method == 'POST':
            details = {"validation_error": {
                "orders": []
            }}
    return JSONResponse(
        status_code=400,
        content=details
    )


@app.exception_handler(CouriersLoadException)
def couriers_load_exception_handler(request, exc: CouriersLoadException):
    ids = list([{"id": x} for x in exc.ids])
    details = {"validation_error": {
        "couriers": ids
    }}
    return JSONResponse(
        status_code=400,
        content=details
    )


@app.exception_handler(OrdersLoadException)
def orders_load_exception_handler(request, exc: OrdersLoadException):
    ids = list([{"id": x} for x in exc.ids])
    details = {"validation_error": {
        "orders": ids
    }}
    return JSONResponse(
        status_code=400,
        content=details
    )


# 1: POST /couriers
@app.post("/couriers")
def route_post_couriers(request_body: CouriersPostRequest):
    if not request_body.data:
        raise CouriersLoadException([])
    couriers_good = []
    couriers_bad = []
    for kinda_courier in request_body.data:
        courier_id = kinda_courier.courier_id
        try:
            courier = CourierItem(**kinda_courier.dict())
        except ValidationError as e:
            couriers_bad.append(courier_id)
        else:
            if not validate_hours_input(courier.working_hours):
                couriers_bad.append(courier_id)
            else:
                couriers_good.append(courier)

    if couriers_bad:
        raise CouriersLoadException(couriers_bad)
    inserted_ids = save_posted_couriers(couriers_good)
    details = {"couriers": list([{"id": x} for x in inserted_ids])}
    return JSONResponse(
        status_code=201,
        content=details
    )


# 2: PATCH /couriers/$courier_id
@app.patch("/couriers/{courier_id}")
def route_patch_courier(
    courier_id: PositiveInt,
    courier_info: CourierUpdateRequest
):
    result = update_courier(courier_id, courier_info.dict(exclude_unset=True))
    if not result:
        return JSONResponse(status_code=404)
    return CourierItem(courier_id=courier_id, **result)


# 3: POST /orders
@app.post("/orders")
def route_post_orders(request_body: OrdersPostRequest):
    if not request_body.data:
        raise OrdersLoadException([])
    orders_good = []
    orders_bad = []
    for kinda_order in request_body.data:
        order_id = kinda_order.order_id
        try:
            order = OrderItem(**kinda_order.dict())
        except ValidationError as e:
            orders_bad.append(order_id)
        else:
            if not validate_hours_input(order.delivery_hours):
                orders_bad.append(order_id)
            else:
                orders_good.append(order)
    if orders_bad:
        raise OrdersLoadException(orders_bad)
    inserted_ids = save_posted_orders(orders_good)
    details = {"orders": list([{"id": x} for x in inserted_ids])}
    return JSONResponse(
        status_code=201,
        content=details
    )


# 4: POST /orders/assign
@app.post("/orders/assign")
def route_assign_orders(request_body: OrdersAssignPostRequest):
    result = assign_orders(request_body.courier_id)
    if result is None:
        return JSONResponse(status_code=400)
    elif not result:
        return {"orders": []}
    return result


# 5: POST /orders/complete
@app.post("/orders/complete")
def route_complete_order(request_body: OrdersCompletePostRequest):
    order_id = complete_order(**request_body.dict())
    if not order_id:
        return JSONResponse(status_code=400)
    return {"order_id": order_id}


# 6: GET /couriers/$courier_id
@app.get("/couriers/{courier_id}")
def route_get_courier(courier_id: PositiveInt):
    result = get_courier_info(courier_id)
    if not result:
        return JSONResponse(status_code=404)
    return result
