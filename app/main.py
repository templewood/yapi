from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pydantic import ValidationError

from exceptions import CouriersLoadException, OrdersLoadException
from schemas.couriers import CouriersPostRequest, CourierItem
from schemas.orders import OrdersPostRequest, OrderItem


app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    details = ''
    if request.url.path.startswith('/couriers'):
        if request.method == 'POST':
            details = { "validation_error": {
                "couriers": []
            } }
    elif request.url.path.startswith('/orders'):
        if request.method == 'POST':
            details = { "validation_error": {
                "orders": []
            } }
    return JSONResponse(
        status_code=400,
        content=details
    )

@app.exception_handler(CouriersLoadException)
def couriers_load_exception_handler(request, exc: CouriersLoadException):
    ids = list([{"id": x} for x in exc.ids])
    details = { "validation_error": {
        "couriers": ids
    } }
    return JSONResponse(
        status_code=400,
        content=details
    )

@app.exception_handler(OrdersLoadException)
def orders_load_exception_handler(request, exc: OrdersLoadException):
    ids = list([{"id": x} for x in exc.ids])
    details = { "validation_error": {
        "orders": ids
    } }
    return JSONResponse(
        status_code=400,
        content=details
    )

# 1: POST /couriers
@app.post("/couriers")
def route_post_couriers(request_body: CouriersPostRequest):
    couriers_good = []
    couriers_bad = []
    for kinda_courier in request_body.data:
        courier_id = kinda_courier.courier_id
        try:
            courier = CourierItem(**kinda_courier.dict())
        except ValidationError as e:
            couriers_bad.append(courier_id)
        else:
            couriers_good.append(courier)

    if couriers_bad:
        raise CouriersLoadException(couriers_bad)
    return request_body # FIXME


# 3: POST /orders
@app.post("/orders")
def route_post_orders(request_body: OrdersPostRequest):
    orders_good = []
    orders_bad = []
    for kinda_order in request_body.data:
        order_id = kinda_order.order_id
        try:
            order = OrderItem(**kinda_order.dict())
        except ValidationError as e:
            orders_bad.append(order_id)
        else:
            orders_good.append(order)
    if orders_bad:
        raise OrdersLoadException(orders_bad)
    return request_body # FIXME
